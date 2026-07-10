import hmac, hashlib
import io
import qrcode
from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from decimal import Decimal
from datetime import datetime
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from pkg import app, csrf
from pkg.models import db, Event, EventTicket, EventAttendees, TicketOrder, TicketOrderItem, Notification

def sign_reference(reference):
    sig = hmac.new(app.config['SECRET_KEY'].encode(), reference.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{reference}.{sig}"

def verify_ticket_token(token):
    try:
        reference, sig = token.rsplit('.', 1)
    except ValueError:
        return None
    expected = hmac.new(app.config['SECRET_KEY'].encode(), reference.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(sig, expected):
        return None
    return reference




@app.get('/rsvp/ticket/<reference>/download/')
def download_ticket(reference):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    order = TicketOrder.query.filter_by(reference=reference).first_or_404()
    if order.user_id != session.get('useronline'):
        flash('Unauthorized', category='errormsg')
        return redirect(url_for('home'))
    if order.status != 'paid':
        flash('This order has not been completed yet', category='errormsg')
        return redirect(url_for('rsvp', event_id=order.event_id))

    event = order.event
    attendee = order.user

    # Generate QR code image in memory
    qr_token = sign_reference(order.reference)
    qr_img = qrcode.make(qr_token)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Build the PDF
    pdf_buffer = io.BytesIO()
    width, height = A5
    c = canvas.Canvas(pdf_buffer, pagesize=A5)

    # Header band
    c.setFillColorRGB(0.09, 0.09, 0.13)
    c.rect(0, height - 30*mm, width, 30*mm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica-Bold', 18)
    c.drawString(15*mm, height - 18*mm, 'SceneX')
    c.setFont('Helvetica', 10)
    c.drawString(15*mm, height - 25*mm, 'Event Ticket')

    # Event details
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(15*mm, height - 45*mm, event.name[:45])

    c.setFont('Helvetica', 11)
    event_date = event.event_start.strftime('%a, %b %d, %Y  •  %I:%M %p') if event.event_start else 'Date TBD'
    c.drawString(15*mm, height - 53*mm, event_date)
    c.drawString(15*mm, height - 60*mm, (event.address or 'Venue TBD')[:60])

    # Divider
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(15*mm, height - 66*mm, width - 15*mm, height - 66*mm)

    # Attendee + order info
    c.setFont('Helvetica-Bold', 10)
    c.drawString(15*mm, height - 74*mm, 'Attendee')
    c.setFont('Helvetica', 10)
    c.drawString(15*mm, height - 79*mm, attendee.username if hasattr(attendee, 'username') else order.email)
    c.drawString(15*mm, height - 84*mm, order.email)

    c.setFont('Helvetica-Bold', 10)
    c.drawString(15*mm, height - 92*mm, 'Order Reference')
    c.setFont('Helvetica', 10)
    c.drawString(15*mm, height - 97*mm, order.reference)

    # Ticket line items
    y = height - 108*mm
    c.setFont('Helvetica-Bold', 10)
    c.drawString(15*mm, y, 'Tickets')
    y -= 6*mm
    c.setFont('Helvetica', 10)
    for item in order.items:
        c.drawString(15*mm, y, f"{item.ticket.name}  x{item.quantity}")
        y -= 5.5*mm

    # QR code
    qr_size = 45*mm
    c.drawImage(ImageReader(qr_buffer), width - qr_size - 15*mm, 15*mm, width=qr_size, height=qr_size)
    c.setFont('Helvetica', 7)
    c.drawCentredString(width - qr_size/2 - 15*mm, 12*mm, 'Scan at entrance')

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"scenex-ticket-{order.reference}.pdf"
    )


