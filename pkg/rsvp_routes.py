import os
from flask import render_template, request, jsonify, redirect, url_for, flash, session

from pkg import app, csrf
from pkg.models import db, Event, EventTicket, EventAttendees, User, Notification


@app.route('/rsvp/<int:event_id>/')
def rsvp(event_id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user = User.query.get(user_id)
    event = Event.query.get_or_404(event_id)
    tickets = EventTicket.query.filter_by(event_id=event_id, active=True).all()

    return render_template('rsvp/rsvp.html', event=event, tickets=tickets, user=user)


@csrf.exempt
@app.post('/rsvp/submit/')
def rsvp_submit():
    """AJAX endpoint: validate, deduct inventory, register attendee, notify creator."""
    if session.get('useronline') is None:
        return jsonify(success=False, message='Login required'), 401

    user_id = session.get('useronline')
    data = request.get_json(silent=True) or {}

    event_id = data.get('event_id')
    selections = data.get('selections', [])  # [{"ticket_id": 1, "qty": 2}, ...]

    if not event_id or not selections:
        return jsonify(success=False, message='Missing event or ticket selections'), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify(success=False, message='Event not found'), 404

    # Validate & deduct quantities
    tickets_to_update = []
    for sel in selections:
        ticket_id = sel.get('ticket_id')
        qty = int(sel.get('qty', 0))
        if qty <= 0:
            continue

        ticket = EventTicket.query.filter_by(id=ticket_id, event_id=event_id, active=True).first()
        if not ticket:
            return jsonify(success=False, message=f'Ticket {ticket_id} not found or inactive'), 400

        remaining = (ticket.quantity or 0) - (ticket.sold or 0)
        if qty > remaining:
            return jsonify(
                success=False,
                message=f'Only {remaining} spot(s) left for "{ticket.name}"'
            ), 400

        if qty > ticket.max_per_order:
            return jsonify(
                success=False,
                message=f'Max {ticket.max_per_order} ticket(s) per order for "{ticket.name}"'
            ), 400

        tickets_to_update.append((ticket, qty))

    if not tickets_to_update:
        return jsonify(success=False, message='No valid tickets selected'), 400

    # Check if user already RSVP'd
    already = EventAttendees.query.filter_by(event_id=event_id, user_id=user_id).first()
    if already:
        return jsonify(success=False, message='You have already RSVP\'d to this event'), 409

    try:
        for ticket, qty in tickets_to_update:
            ticket.sold = (ticket.sold or 0) + qty

        attendee = EventAttendees(event_id=event_id, user_id=user_id)
        db.session.add(attendee)

        # Notify event creator
        if event.creator_id and event.creator_id != user_id:
            notif = Notification(
                recipient_id=event.creator_id,
                actor_id=user_id,
                type='event_join',
                event_id=event_id,
            )
            db.session.add(notif)

        db.session.commit()
        return jsonify(success=True, message='RSVP confirmed!')

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500