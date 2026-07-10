import os, uuid, requests

from decimal import Decimal
from datetime import datetime
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from pkg import app, csrf
from pkg.models import db, Event, EventTicket, EventAttendees, TicketOrder, TicketOrderItem, Notification

PAYSTACK_SECRET = os.environ.get('PAYSTACK_SECRET_KEY')


@app.route('/rsvp/<int:event_id>/')
def rsvp(event_id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    event = Event.query.get_or_404(event_id)
    tickets = EventTicket.query.filter_by(event_id=event_id, active=True).all()
    return render_template('rsvp/rsvp.html', event=event, tickets=tickets, current_page='rsvp')


@csrf.exempt
@app.post('/rsvp/submit/')
def rsvp_submit():
    if session.get('useronline') is None:
        return jsonify(success=False, message='Login required'), 401

    data = request.get_json(silent=True) or {}
    event_id = data.get('event_id')
    selections = data.get('selections', [])
    email = data.get('email')

    if not event_id or not selections or not email:
        return jsonify(success=False, message='Missing ticket selection or email'), 400

    now = datetime.utcnow()
    total = Decimal('0')
    line_items = []

    for sel in selections:
        ticket = EventTicket.query.filter_by(id=sel.get('ticket_id'), event_id=event_id, active=True).first()
        if not ticket:
            return jsonify(success=False, message='Invalid ticket selected'), 400

        qty = int(sel.get('qty', 0))
        if qty < 1 or qty > ticket.max_per_order:
            return jsonify(success=False, message=f'Invalid quantity for {ticket.name}'), 400
        if ticket.sales_start and now < ticket.sales_start:
            return jsonify(success=False, message=f'{ticket.name} sales have not started yet'), 400
        if ticket.sales_end and now > ticket.sales_end:
            return jsonify(success=False, message=f'{ticket.name} sales have ended'), 400

        # quantity == 0 means unlimited, matches the frontend convention
        if ticket.quantity > 0:
            remaining = ticket.quantity - ticket.sold
            if qty > remaining:
                return jsonify(success=False, message=f'Only {remaining} left for {ticket.name}'), 400

        total += ticket.price * qty
        line_items.append((ticket, qty))

    fee = (total * Decimal('0.05')).quantize(Decimal('1'))
    grand_total = total + fee
    reference = f"scenex_{uuid.uuid4().hex[:20]}"

    order = TicketOrder(user_id=session['useronline'], event_id=event_id, reference=reference,
                         email=email, total_amount=grand_total, status='pending')
    db.session.add(order)
    db.session.flush()
    for ticket, qty in line_items:
        db.session.add(TicketOrderItem(order_id=order.id, ticket_id=ticket.id, quantity=qty, unit_price=ticket.price))
    db.session.commit()

    if grand_total == 0:
        _fulfil_order(order)
        return jsonify(success=True, free=True, reference=reference)

    callback_url = url_for('rsvp_verify', _external=True) + f'?reference={reference}'
    try:
        resp = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers={'Authorization': f'Bearer {PAYSTACK_SECRET}'},
            json={'email': email, 'amount': int(grand_total * 100), 'reference': reference, 'callback_url': callback_url},
            timeout=15
        ).json()
        
        if not resp.get('status') or 'data' not in resp:
            order.status = 'failed'
            db.session.commit()
            app.logger.error(f"Paystack init failed for order {order.id}: {resp}")
            return jsonify(success=False, message=resp.get('message', 'Could not start payment, please try again')), 502
    except requests.exceptions.RequestException as e:
        order.status = 'failed'
        db.session.commit()
        return jsonify(success=False, message='Could not reach the payment provider, please try again'), 502

    return jsonify(success=True, authorization_url=resp['data']['authorization_url'])


def _fulfil_order(order):
    if order.status == 'paid':
        return
    for item in order.items:
        item.ticket.sold += item.quantity
    if not EventAttendees.query.filter_by(event_id=order.event_id, user_id=order.user_id).first():
        db.session.add(EventAttendees(event_id=order.event_id, user_id=order.user_id))
    order.status = 'paid'
    order.paid_at = datetime.utcnow()
    db.session.add(Notification(recipient_id=order.event.creator_id, actor_id=order.user_id, type='event_join', event_id=order.event_id))
    db.session.commit()


@app.get('/rsvp/verify/')
def rsvp_verify():
    reference = request.args.get('reference')
    order = TicketOrder.query.filter_by(reference=reference).first_or_404()
    if order.status != 'paid':
        resp = requests.get(f'https://api.paystack.co/transaction/verify/{reference}',
                             headers={'Authorization': f'Bearer {PAYSTACK_SECRET}'}).json()
        data = resp.get('data', {})
        if resp.get('status') and data.get('status') == 'success' and int(data.get('amount', 0)) == int(order.total_amount * 100):
            _fulfil_order(order)
        else:
            order.status = 'failed'
            db.session.commit()
            flash('Payment could not be verified', category='errormsg')
            return redirect(url_for('event_detail', id=order.event_id))
    return redirect(url_for('rsvp', event_id=order.event_id, reference=reference))


@app.get('/rsvp/order/<reference>/')
def rsvp_order_detail(reference):
    order = TicketOrder.query.filter_by(reference=reference).first_or_404()
    if order.user_id != session.get('useronline'):
        return jsonify(success=False), 403
    return jsonify(success=True, order={
        'reference': order.reference,
        'email': order.email,
        'total': float(order.total_amount),
        'items': [{'name': i.ticket.name, 'quantity': i.quantity} for i in order.items]
    })