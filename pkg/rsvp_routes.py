import os
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from pkg import app
from pkg.forms import TicketForm
from pkg.models import db, Event, EventTicket


@app.route('/rsvp/')
def rsvp():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    
    return render_template('rsvp/rsvp.html')