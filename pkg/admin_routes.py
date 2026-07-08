from flask import render_template, request, abort, redirect, url_for, flash, session

from werkzeug.security import generate_password_hash, check_password_hash

from pkg import app, csrf
from pkg.forms import LoginForm
from pkg.models import db
from pkg.models import Admin
from pkg.models import User, Event, EventCategory, EventLineup, State, Lga, Post, Community, Like

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('user/404.html', error=error),404


def _build_admin_stats():
    return {
        'users_count': User.query.count(),
        'events_count': Event.query.count(),
        'communities_count': Community.query.count(),
        'recent_users': User.query.order_by(User.joined_at.desc()).limit(5).all(),
        'recent_events': Event.query.order_by(Event.created_at.desc()).limit(5).all(),
    }


@app.route('/admin/login/', methods=['GET', 'POST'])
def adminlogin():
    loginform = LoginForm()
    if request.method == 'GET':
        return render_template('admin/admin_login.html', loginform=loginform)
    else:
        if loginform.validate_on_submit():
            email = loginform.usermail.data
            password = loginform.userpass.data
            
            if_exists = Admin.query.filter(Admin.email==email).first()
            if if_exists:
                stored_password = if_exists.password
                rsp = check_password_hash(stored_password, password)
                if rsp:
                    session['adminonline'] = if_exists.id
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Wrong Password', category='errormsg')
                    return redirect(url_for('adminlogin'))
            else:
                flash('Email does not exist', category='errormsg')
                return redirect(url_for('adminlogin'))
        else:
            return render_template('admin/admin_login.html', loginform=loginform)


@app.route('/admin/logout/')
def adminlogout():
    if session.get('adminonline'):
        session.pop('adminonline', None)
        session.clear()
    return redirect('/')

    
@app.route('/admin/signup/', methods=['GET','POST'])
def adminsignup():
    if request.method == 'GET':
        return render_template('admin/admin_register.html')
    else:
        admin = Admin()
        adminname = request.form.get('adminname')
        email = request.form.get('adminmail')
        password = request.form.get('adminpass')
        confirm_pass = request.form.get('adminconfirmpass')
        
        
        if adminname=="" or email=="" or password=="":
            flash('All fields are compulsory!', category='errormsg')
            return redirect(url_for('adminsignup'))
        elif password != confirm_pass:
            flash('The two passwords must match!', category='errormsg')
            return(redirect(url_for('adminsignup')))
        else:
            hashed_pwd = generate_password_hash(password)
            try:
                admin=Admin(admin_name=adminname, email=email, password=hashed_pwd)
                db.session.add(admin)
                db.session.commit()
                    
                return redirect(url_for('adminlogin'))
            except:
                flash('Error creating account, choose another email', category='errormsg')
                return redirect(url_for('adminsignup'))

            
        
@app.route('/admin/check/email/')
def admin_check_email():
    email = request.args.get('email')
    check = Admin.query.filter(Admin.email==email).first()
    if check:
        return "<span class='text-danger'>This Email is already in use. Please choose another email.</span>"
    else:
        return "<span class='text-success'>This Email is available.</span>"
       
@app.get('/admin/dashboard/')
def admin_dashboard():
    if session.get('adminonline') is not None:
        admin_id = session.get('adminonline')
        admin_deets = Admin.query.get(admin_id)
        stats = _build_admin_stats()
        return render_template('admin/admin_dashboard.html', title='Dashboard', admin_deets=admin_deets, stats=stats, current_page='dashboard')
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('adminlogin'))


@app.get('/admin/users/')
def admin_users():
    if session.get('adminonline') is not None:
        admin_id = session.get('adminonline')
        admin_deets = Admin.query.get(admin_id)
        stats = _build_admin_stats()
        users = User.query.order_by(User.joined_at.desc()).all()
        return render_template('admin/admin_users.html', title='Users', admin_deets=admin_deets, stats=stats, users=users, current_page='users')
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('adminlogin'))


@app.post('/admin/verify-user/<int:id>/')
def admin_verify_user(id):
    if session.get('adminonline') is not None:
        user = User.query.get_or_404(id)
        user.verified_status = 'verified'
        user.account_status = 'active'
        db.session.commit()
        flash('User verified successfully', category='success')
        return redirect(request.referrer or url_for('admin_users'))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))

@app.post('/admin/remove-verify/<int:id>/')
def admin_remove_verify(id):
    if session.get('adminonline') is not None:
        user = User.query.get_or_404(id)
        user.verified_status = 'not verified'
        user.account_status = 'active'
        db.session.commit()
        flash('User verification removed', category='success')
        return redirect(request.referrer or url_for('admin_users'))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))

@app.post('/admin/suspend-user/<int:id>/')
def admin_suspend_user(id):
    if session.get('adminonline') is not None:
        user = User.query.get_or_404(id)
        user.account_status = 'suspended'
        db.session.commit()
        flash('User suspended successfully', category='success')
        return redirect(request.referrer or url_for('admin_users'))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))


@app.post('/admin/ban-user/<int:id>/')
def admin_ban_user(id):
    if session.get('adminonline') is not None:
        user = User.query.get_or_404(id)
        user.account_status = 'banned'
        db.session.commit()
        flash('User banned successfully', category='success')
        return redirect(request.referrer or url_for('admin_users'))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))


@app.get('/admin/user-details/<int:id>/')
def admin_user_details(id):
    if session.get('adminonline') is not None:
        admin_id = session.get('adminonline')
        admin_deets = Admin.query.get(admin_id)
        user = User.query.get_or_404(id)
        stats = _build_admin_stats()
        state = State.query.get(user.state_id)
        posts_count = Post.query.filter(Post.creator_id == user.id).count()
        events_count = Event.query.filter(Event.creator_id == user.id).count()
        communities_count = Community.query.filter(Community.creator_id == user.id).count()

        return render_template(
            'admin/admin_user_details.html',
            title='User Details',
            admin_deets=admin_deets,
            user=user,
            state=state,
            posts_count=posts_count,
            events_count=events_count,
            communities_count=communities_count,
            current_page='users',
            stats = stats
        )
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('adminlogin'))


@app.get('/admin/all-events/')
def admin_events():
    if session.get('adminonline') is not None:
        admin_id = session.get('adminonline')
        admin_deets = Admin.query.get(admin_id)
        stats = _build_admin_stats()
        events = Event.query.order_by(Event.created_at.desc()).all()
        return render_template('admin/admin_event.html', title='All Events', admin_deets=admin_deets, stats=stats, events=events, current_page='events')
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('adminlogin'))


@app.get('/admin/communities/')
def admin_communities():
    if session.get('adminonline') is not None:
        admin_id = session.get('adminonline')
        admin_deets = Admin.query.get(admin_id)
        stats = _build_admin_stats()
        communities = Community.query.order_by(Community.created_at.desc()).all()
        return render_template('admin/admin_comm.html', title='Communities', admin_deets=admin_deets, stats=stats, communities=communities, current_page='communities')
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('adminlogin'))


@app.get('/admin/event-categories/')
def admin_event_categories():
    if session.get('adminonline') is not None:
        admin_id = session.get('adminonline')
        admin_deets = Admin.query.get(admin_id)
        stats = _build_admin_stats()
        categories = EventCategory.query.order_by(EventCategory.id.asc()).all()
        return render_template('admin/admin_event_categories.html', title='Categories', admin_deets=admin_deets, stats=stats, categories=categories, current_page='categories')
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))


@app.post('/admin/event-categories/')
def admin_add_event_category():
    if session.get('adminonline') is not None:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if name:
            category = EventCategory(name=name, desc=description or None)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully', category='success')
        else:
            flash('Category name is required', category='errormsg')
        return redirect(url_for('admin_event_categories'))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))


@app.post('/admin/delete-category/<int:id>/')
def admin_delete_event_category(id):
    if session.get('adminonline') is not None:
        category = EventCategory.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        flash('Category removed successfully', category='success')
        return redirect(url_for('admin_event_categories'))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))
    
    
@app.route('/admin/view-event/<id>/')
def admin_view_event(id):
    if session.get('adminonline')!=None:
        event = Event.query.get_or_404(id)
        
        category = EventCategory.query.filter(EventCategory.id==Event.cat_id).first()
        creator = User.query.filter(User.id==Event.creator_id).first()
        state = State.query.filter(State.id==Event.state_id).first()
        lga = Lga.query.filter(Lga.id==Event.lga_id).first()
        
        posts = Post.query.filter(Post.event_id==event.id).all()
        liked_post_ids = set()
        if session.get('useronline') is not None:
            uid = session.get('useronline')
            liked_rows = db.session.query(Like.post_id).filter(Like.user_id == uid).all()
            liked_post_ids = {r[0] for r in liked_rows}

        return render_template('admin/admin_view_event.html', title="View Event", event=event, category=category, creator=creator, state=state, lga=lga, posts=posts, liked_post_ids=liked_post_ids)
                
         
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    
    
@app.post('/admin/approve-event/<int:id>/')
def admin_approve_event(id):
    if session.get('adminonline') is not None:
        event = Event.query.get_or_404(id)
        event.status = 'approved'
        db.session.commit()
        flash('Event Approved successfully', category='success')
        return redirect(url_for('admin_view_event', id=event.id))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))

@app.post('/admin/reject-event/<int:id>/')
def admin_reject_event(id):
    if session.get('adminonline') is not None:
        event = Event.query.get_or_404(id)
        event.status = 'rejected'
        db.session.commit()
        flash('Event has been rejected', category='errormsg')
        return redirect(url_for('admin_view_event', id=event.id))
    flash('You must be logged in to view this page', category='errormsg')
    return redirect(url_for('adminlogin'))

    
@app.post('/admin/delete-event/<int:id>/')
def admin_delete_event(id):
    event = Event.query.get_or_404(id)

    db.session.delete(event)
    db.session.commit()
    flash('Event removed successfully', category='success')
    return redirect('/admin/all-events/')

