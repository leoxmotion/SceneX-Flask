import os
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from pkg import app
from pkg.forms import TicketForm
from pkg.models import db, Event, EventTicket


@app.route('/creator/events/<int:event_id>/tickets/')
def creator_event_tickets(event_id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    event = Event.query.get_or_404(event_id)
    if event.creator_id != session.get('useronline'):
        flash('Unauthorized access to ticket management', category='errormsg')
        return redirect(url_for('creator_events'))

    ticketform = TicketForm()
    tickets = EventTicket.query.filter_by(event_id=event.id).all()
    return render_template('creator/creator_add_tickets.html', title='Manage Tickets', event=event, tickets=tickets, ticketform=ticketform, current_page='events')


@app.route('/creator/events/<int:event_id>/tickets/add/', methods=['POST'])
def add_event_ticket(event_id):
    if session.get('useronline') is None:
        return jsonify(success=False, error='Authentication required'), 401

    event = Event.query.get_or_404(event_id)
    if event.creator_id != session.get('useronline'):
        return jsonify(success=False, error='Unauthorized'), 403

    ticketform = TicketForm()
    if ticketform.validate_on_submit():
        category = ticketform.category.data
        price = 0 if category == 'free' else float(ticketform.price.data or 0)
        seats = ticketform.seats_per_ticket.data if category == 'table' else None

        ticket = EventTicket(
            event_id=event.id,
            name=ticketform.name.data,
            category=category,
            description=ticketform.description.data,
            price=price,
            quantity=ticketform.quantity.data or 0,
            sold=0,
            max_per_order=ticketform.max_per_order.data or 1,
            seats_per_ticket=seats,
            sales_start=ticketform.sales_start.data,
            sales_end=ticketform.sales_end.data,
            active=True,
        )

        db.session.add(ticket)
        db.session.commit()
        res = jsonify(success=True, ticket=ticket.to_dict())
        return redirect(url_for('creator_event_tickets', event_id=event.id))

    return jsonify(success=False, error='Invalid ticket data', errors=ticketform.errors)


@app.route('/creator/tickets/<int:ticket_id>/update/', methods=['POST'])
def update_event_ticket(ticket_id):
    if session.get('useronline') is None:
        return jsonify(success=False, error='Authentication required'), 401

    ticket = EventTicket.query.get_or_404(ticket_id)
    event = Event.query.get_or_404(ticket.event_id)
    if event.creator_id != session.get('useronline'):
        return jsonify(success=False, error='Unauthorized'), 403

    ticketform = TicketForm()
    if ticketform.validate_on_submit():
        category = ticketform.category.data
        ticket.name = ticketform.name.data
        ticket.category = category
        ticket.description = ticketform.description.data
        ticket.price = 0 if category == 'free' else float(ticketform.price.data or 0)
        ticket.quantity = ticketform.quantity.data or 0
        ticket.max_per_order = ticketform.max_per_order.data or 1
        ticket.seats_per_ticket = ticketform.seats_per_ticket.data if category == 'table' else None
        ticket.sales_start = ticketform.sales_start.data
        ticket.sales_end = ticketform.sales_end.data
        db.session.commit()
        return jsonify(success=True, ticket=ticket.to_dict())

    return jsonify(success=False, error='Unable to update ticket', errors=ticketform.errors)


@app.route('/creator/tickets/<int:ticket_id>/delete/', methods=['POST'])
def delete_event_ticket(ticket_id):
    if session.get('useronline') is None:
        return jsonify(success=False, error='Authentication required'), 401

    ticket = EventTicket.query.get_or_404(ticket_id)
    event = Event.query.get_or_404(ticket.event_id)
    if event.creator_id != session.get('useronline'):
        return jsonify(success=False, error='Unauthorized'), 403

    db.session.delete(ticket)
    db.session.commit()
    return jsonify(success=True)
