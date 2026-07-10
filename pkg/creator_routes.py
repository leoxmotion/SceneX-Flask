import os
import secrets
from flask import render_template, request, abort, redirect, url_for, flash, session, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from pkg import app, csrf
from pkg.forms import LoginForm, EventForm, CommForm, PostForm, CommPostForm
from pkg.models import db
from pkg.models import User, Event, EventCategory, EventLineup, State, Lga, Community, Post, CommunityPost, CommunityMember, CommunityComment, EventTicket, Like

@app.route('/creator/events/')
def creator_events():
    if session.get('useronline') is not None:
        user_id = session.get('useronline')
        user = User.query.get(user_id)
        events = Event.query.filter_by(creator_id=user_id).order_by(Event.created_at.desc()).all()
        return render_template('creator/creator_events.html', events=events, user=user, current_page='events')
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.route('/creator/communities/')
def creator_comms():
    if session.get('useronline') is not None:
        user_id = session.get('useronline')
        user = User.query.get(user_id)
        comms = Community.query.filter_by(creator_id=user_id).order_by(Community.created_at.desc()).all()
        return render_template('creator/creator_comm.html', comms=comms, user=user, current_page='communities')
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.route('/create_event/', methods=['POST', 'GET'])
def create_event_page():
    if session.get('useronline') is not None:
        if request.method == 'GET':
            id = session.get('useronline')
            eventform= EventForm()
            state = State.query.all()
            eventform.cat_id.choices = [(c.id, c.name) for c in EventCategory.query.all()]
            eventform.comm_id.choices = [(c.id, c.name) for c in Community.query.all()]
            eventform.state_id.choices = [(s.id, s.name) for s in state]
            eventform.lga_id.choices = [(l.id, l.name) for l in Lga.query.all()]
            
            return render_template('creator/create_event.html', title="Create Event", eventform=eventform, current_page='events')
        else:
            id = session.get('useronline')
            eventform= EventForm()
            if eventform:
                creator_id=id
                name = eventform.name.data
                description = eventform.description.data
                banner = eventform.banner.data
                address = eventform.address.data
                state_id = eventform.state_id.data
                lga_id = eventform.lga_id.data
                map_link = eventform.map_link.data
                cat_id = eventform.cat_id.data
                event_start = eventform.event_start.data
                event_end = eventform.event_end.data
                
                if banner:
                    filename = banner.filename
                    fname, ext = os.path.splitext(filename)
                    newname = secrets.token_hex(32)
                    filename = newname + ext
                    upload_path = os.path.join('pkg/static/uploads', filename)
                    banner.save(upload_path)
                    event = Event(creator_id=creator_id, name=name, description=description, banner=filename, address=address, lga_id=lga_id, state_id=state_id, map_link=map_link, cat_id=cat_id, event_start=event_start, event_end=event_end)
                else:
                    event = Event(creator_id=creator_id, name=name, description=description, address=address, lga_id=lga_id, state_id=state_id, map_link=map_link, cat_id=cat_id, event_start=event_start, event_end=event_end)
                
                db.session.add(event)
                db.session.commit()
                flash('Event Created Successfully')
                return 'Successful'
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.route('/state-lgas/', methods=['POST'])
def state_lgas():
    state_id = request.form.get('state_id')
    lgas = Lga.query.filter(Lga.state_id == state_id).all()
    return jsonify([{'id': l.id, 'name': l.name} for l in lgas])


@app.route('/creator/view-event/<int:id>/')
def creator_view_event(id):
    if session.get('useronline') is not None:
        user_id = session.get('useronline')
        user = User.query.get(user_id)
        event = Event.query.get_or_404(id)
        
        category = EventCategory.query.get(event.cat_id)
        creator = User.query.get(event.creator_id)
        state = State.query.get(event.state_id)
        lga = Lga.query.get(event.lga_id)
        posts = Post.query.filter(Post.event_id==event.id).all()
        tickets = EventTicket.query.filter_by(event_id=event.id).all()

        liked_post_ids = set()
        liked_rows = db.session.query(Like.post_id).filter(Like.user_id == user_id).all()
        liked_post_ids = {r[0] for r in liked_rows}

        return render_template('creator/creator_view_event.html', title="View Event", event=event, category=category, creator=creator, state=state, lga=lga, user=user, posts=posts, tickets=tickets, current_page='events', liked_post_ids=liked_post_ids)
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))


@app.route('/creator/edit-event/<int:id>/', methods=['POST', 'GET'])
def creator_edit_event(id):
    if session.get('useronline') is not None:
        user_id = session.get('useronline')
        event = Event.query.get_or_404(id)
        if event.creator_id != user_id:
            flash('Unauthorized', category='errormsg')
            return redirect(url_for('creator_events'))
            
        eventform = EventForm(obj=event)
        eventform.cat_id.choices = [(c.id, c.name) for c in EventCategory.query.all()]
        eventform.state_id.choices = [(s.id, s.name) for s in State.query.all()]
        eventform.lga_id.choices = [(l.id, l.name) for l in Lga.query.all()]
        
        if request.method == 'GET':
            category = EventCategory.query.filter(EventCategory.id==event.cat_id).first()
            return render_template('creator/creator_edit_event.html', title="Edit Event", eventform=eventform, event=event, category=category, current_page='events')
        else:
            if eventform:
                name = eventform.name.data
                description = eventform.description.data
                banner = eventform.banner.data
                address = eventform.address.data
                lga_id = eventform.lga_id.data
                state_id = eventform.state_id.data
                map_link = eventform.map_link.data
                cat_id = eventform.cat_id.data
                event_start = eventform.event_start.data
                event_end = eventform.event_end.data
                
                event.name = name
                event.description = description
                event.address = address
                event.lga_id = lga_id
                event.state_id = state_id
                event.map_link = map_link
                event.cat_id = cat_id
                event.event_start = event_start
                event.event_end = event_end
                
                if banner:
                    filename = banner.filename
                    fname, ext = os.path.splitext(filename)
                    newname = secrets.token_hex(32)
                    filename = newname + ext
                    upload_path = os.path.join('pkg/static/uploads', filename)
                    banner.save(upload_path)
                    event.banner = filename
                    
                db.session.commit()
                flash('Changes made Successfully')
                return redirect(url_for('creator_view_event', id=event.id))
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))


@app.post('/creator/delete-event/<int:id>/')
def delete_event(id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    event = Event.query.get_or_404(id)
    if event.creator_id != session.get('useronline'):
        flash('Unauthorized', category='errormsg')
        return redirect(url_for('creator_events'))
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully', category='success')
    return redirect(url_for('creator_events'))


@app.route('/create_community/', methods=['GET', 'POST'])
def create_comm():
    if session.get('useronline')!=None:
        
        if request.method == 'GET':
            id = session.get('useronline')
            commform= CommForm()
            
            commform.cat_id.choices = [(c.id, c.name) for c in EventCategory.query.all()]
           
            
            return render_template('creator/create_comm.html', title="Create Community", commform=commform, current_page='community')
            
        else:
            id = session.get('useronline')
            commform= CommForm()
            if commform:
                creator_id=id
                name = commform.name.data
                description = commform.description.data
                banner = commform.banner.data
                cat_id = commform.cat_id.data
                
                
                if banner:
                    filename = banner.filename
                    fname, ext = os.path.splitext(filename)
                    newname = secrets.token_hex(32)
                    filename = newname + ext
                    upload_path = os.path.join('pkg/static/uploads', filename)
                    banner.save(upload_path)
                    
                    comm = Community(creator_id=creator_id, name=name, description=description, banner=filename, cat_id=cat_id, )
                else:
                    comm = Community(creator_id=creator_id, name=name, description=description, cat_id=cat_id )
                
                try:
                    db.session.add(comm)
                    db.session.flush()

                    membership = CommunityMember(
                        user_id=creator_id,
                        comm_id=comm.id
                    )

                    db.session.add(membership)
                    db.session.commit()
                    flash('Community Created Successfully')
                    return f'Community {name} successfully created'

                except Exception:
                    db.session.rollback()
                    raise
                
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.route('/comm_detail/<int:id>/')
def comm_detail(id):
    joined = False
    if session.get('useronline')!=None:
        user_ide = session.get('useronline')
        user = User.query.get(user_ide)
        comm = Community.query.get_or_404(id)
        events = Event.query.all()
        postform= PostForm()
        postform.event_id.choices = [(s.id, s.name) for s in events]
        category = EventCategory.query.filter(EventCategory.id==comm.cat_id).first()
        admin = User.query.filter(User.id==comm.creator_id).first()
        posts = CommunityPost.query.filter(CommunityPost.comm_id==comm.id).order_by(CommunityPost.created_at.desc()).all()
        event = Event.query.filter(Event.id==CommunityPost.event_id).first()
        creator = User.query.filter(User.id==comm.creator_id).first()
        member = CommunityMember.query.filter_by(
                        user_id=user_ide,
                        comm_id=comm.id
                    ).first()
        
        
        joined = CommunityMember.query.filter_by(
            user_id=session["useronline"],
            comm_id=comm.id
        ).first() is not None
        return render_template('creator/comm_detail.html', title="Community Details", user=user, category=category, creator=creator, comm=comm, current_page='communities', posts=posts, event=event, admin=admin, postform=postform, joined=joined, member=member)
                
         
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    
@app.route('/create-comm-post/<int:id>/', methods=['POST', 'GET'])
def create_comm_post(id):
    if session.get('useronline')!=None:
        
        if request.method == 'GET':
            user_id = session.get('useronline')
            user = User.query.get(user_id)
            postform= CommPostForm()
            events = Event.query.all()
            postform.event_id.choices = [(s.id, s.name) for s in events]
            comm = Community.query.get_or_404(id)
            
            return render_template('user/home.html', title="Home", postform=postform, user=user, events=events, comm=comm, current_page='home')
            
        else:
            user_id = session.get('useronline')
            postform= CommPostForm()
            comm = Community.query.get_or_404(id)

            
            if postform:
                
                content = postform.content.data
                media = postform.media.data
                event_id = postform.event_id.data
                comm_id=comm.id
                member = CommunityMember.query.filter_by(
                        user_id=user_id,
                        comm_id=comm.id
                    ).first()

                if member is None:
                    flash("Join the community before posting.")
                    return redirect(url_for("comm_detail", id=comm.id))
                
                
                if media:
                    filename = media.filename
                    fname, ext = os.path.splitext(filename)
                    newname = secrets.token_hex(32)
                    filename = newname + ext
                    upload_path = os.path.join('pkg/static/uploads', filename)
                    media.save(upload_path)
                    
                    
                    
                    post = CommunityPost(user_id=user_id,comm_id=comm_id, content=content, media=filename, event_id=event_id)
                else:
                    post = CommunityPost(user_id=user_id, comm_id=comm_id, content=content, event_id=event_id)
                
                db.session.add(post)
                db.session.commit()
                flash('Post Created Successfully')
                return redirect(url_for('comm_detail', id=comm_id))
            else:
                print(postform.errors)
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    
@app.route('/creator/edit-community/<int:id>/', methods=['GET', 'POST'])
def edit_comm(id):
    if session.get('useronline') is not None:
        user_id = session.get('useronline')
        comm = Community.query.get_or_404(id)
        if comm.creator_id != user_id:
            flash('Unauthorized', category='errormsg')
            return redirect(url_for('creator_comms'))
            
        commform = CommForm(obj=comm)
        commform.cat_id.choices = [(c.id, c.name) for c in EventCategory.query.all()]
        
        if request.method == 'GET':
            user = User.query.get_or_404(user_id)
            category = EventCategory.query.filter(EventCategory.id==comm.cat_id).first()
            return render_template('creator/creator_edit_comm.html', title="Edit Community", commform=commform, category=category, comm=comm, current_page='events', user=user)
        else:
            if commform:
                name = commform.name.data
                description = commform.description.data
                banner = commform.banner.data
                cat_id = commform.cat_id.data
                
                comm.name = name
                comm.description = description
                comm.cat_id = cat_id
                
                if banner:
                    filename = banner.filename
                    fname, ext = os.path.splitext(filename)
                    newname = secrets.token_hex(32)
                    filename = newname + ext
                    upload_path = os.path.join('pkg/static/uploads', filename)
                    banner.save(upload_path)
                    comm.banner = filename
                    
                db.session.commit()
                return f'Community {name} successfully edited'
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))