import os
import random
import secrets
from flask import render_template, request, abort, redirect, url_for, flash, session, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from pkg import app, csrf
from pkg.forms import LoginForm, PostForm, CommentForm, ProfileForm
from pkg.models import db
from pkg.models import (
    User, State, Event, Post, EventCategory, Comment, Community, Like,
    CommunityMember, CommunityPost, Follow, Notification
)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template('user/404.html', error=error), 404


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route('/')
@app.route('/index/')
def landing():
    return render_template('user/index.html')


@app.route('/index/login/', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    if request.method == 'GET':
        return render_template('user/login.html', loginform=loginform)
    else:
        if loginform.validate_on_submit():
            usermail = loginform.usermail.data
            userpass = loginform.userpass.data
            if_exists = User.query.filter(User.email == usermail).first()
            if if_exists:
                rsp = check_password_hash(if_exists.password, userpass)
                if rsp:
                    session['useronline'] = if_exists.id
                    return redirect(url_for('profile', id=if_exists.id))
                else:
                    flash('Wrong Password', category='errormsg')
                    return redirect(url_for('login'))
            else:
                flash('Email does not exist', category='errormsg')
                return redirect(url_for('login'))
        else:
            return render_template('user/login.html', loginform=loginform)


@app.route('/logout/')
def logout():
    if session.get('useronline'):
        session.pop('useronline', None)
        session.clear()
    return redirect('/')


@app.route('/index/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        states = State.query.all()
        return render_template('user/auth_page.html', states=states)
    else:
        fullname = request.form.get('userfullname')
        username = request.form.get('username')
        email = request.form.get('usermail')
        password = request.form.get('userpass')
        confirm_pass = request.form.get('userconfirmpass')
        gender = request.form.get('gender')
        state_id = request.form.get('stateid')

        if not all([fullname, username, email, password, gender, state_id]):
            flash('All fields are compulsory!', category='errormsg')
            return redirect(url_for('signup'))
        elif password != confirm_pass:
            flash('The two passwords must match!', category='errormsg')
            return redirect(url_for('signup'))
        else:
            hashed_pwd = generate_password_hash(password)
            try:
                user = User(fullname=fullname, username=username, email=email,
                            password=hashed_pwd, gender=gender, state_id=state_id)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                print("=" * 50)
                print(e)
                print("=" * 50)
                flash(str(e), 'errormsg')
                return redirect(url_for('signup'))


@app.route('/check/email/')
def check_email():
    email = request.args.get('email')
    check = User.query.filter(User.email == email).first()
    if check:
        return "<span class='text-danger'>This Email is already in use. Please use another email.</span>"
    else:
        return "<span class='text-success'>This Email is available.</span>"


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@app.get('/profile/<int:id>/')
def profile(id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user_deets = User.query.get_or_404(id)
    state = user_deets.state

    # Posts by this profile user
    posts = Post.query.filter_by(creator_id=id).order_by(Post.created_at.desc()).all()

    # Community posts by this profile user — normalize to same interface
    comm_posts = CommunityPost.query.filter_by(user_id=id).order_by(CommunityPost.created_at.desc()).all()
    for cp in comm_posts:
        cp.post_type = 'community'
        cp.creator = cp.user
        cp.creator_id = cp.user_id

    for p in posts:
        p.post_type = 'regular'

    all_posts = sorted(posts + comm_posts, key=lambda p: p.created_at, reverse=True)

    events = Event.query.filter_by(creator_id=id).all()
    comms = Community.query.all()

    liked_rows = db.session.query(Like.post_id).filter(Like.user_id == user_id).all()
    liked_post_ids = {r[0] for r in liked_rows}

    # Follow state
    is_following = False
    if user_id != id:
        is_following = Follow.query.filter_by(follower_id=user_id, followed_id=id).first() is not None

    follower_count = Follow.query.filter_by(followed_id=id).count()
    following_count = Follow.query.filter_by(follower_id=id).count()

    return render_template(
        'user/profile.html',
        title="Profile",
        user_deets=user_deets,
        state=state,
        posts=all_posts,
        events=events,
        comms=comms,
        current_page='profile',
        liked_post_ids=liked_post_ids,
        is_following=is_following,
        follower_count=follower_count,
        following_count=following_count,
    )


@app.route('/edit-profile/')
def edit_profile():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    id = session.get('useronline')
    user_deets = User.query.get(id)
    states = State.query.all()
    profileform = ProfileForm(obj=user_deets)
    profileform.state.choices = [(s.id, s.name) for s in states]
    return render_template('user/edit_profile.html', title="Edit Profile", user_deets=user_deets,
                           current_page='profile', states=states, profileform=profileform)


@app.post('/change-profile/')
def change_profile():
    if session.get('useronline') is None:
        return "Access Denied"
    id = session.get('useronline')
    user_deets = User.query.get(id)
    profileform = ProfileForm(obj=user_deets)
    fullname = profileform.fullname.data
    username = profileform.username.data
    bio = profileform.bio.data
    state = profileform.state.data
    profile_pic = profileform.profile_pic.data

    user_deets.fullname = fullname
    user_deets.username = username
    user_deets.bio = bio
    user_deets.state_id = state

    if profile_pic:
        filename = profile_pic.filename
        fname, ext = os.path.splitext(filename)
        newname = secrets.token_hex(32)
        filename = newname + ext
        upload_path = os.path.join('pkg/static/uploads', filename)
        profile_pic.save(upload_path)
        user_deets.profile_pic = filename

    db.session.commit()
    return 'Account Updated successfully'


# ---------------------------------------------------------------------------
# Home feed  (global, followed-user priority, randomised)
# ---------------------------------------------------------------------------

@app.route('/home/')
def home():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user = User.query.get(user_id)

    # IDs of followed users + self (priority tier)
    followed_ids = {r[0] for r in db.session.query(Follow.followed_id)
                    .filter(Follow.follower_id == user_id).all()}
    followed_ids.add(user_id)

    # Fetch all regular posts
    all_regular = Post.query.order_by(Post.created_at.desc()).all()
    for p in all_regular:
        p.post_type = 'regular'

    # Fetch all community posts — normalise interface
    all_comm = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    for cp in all_comm:
        cp.post_type = 'community'
        cp.creator = cp.user
        cp.creator_id = cp.user_id

    all_posts = all_regular + all_comm

    # Split into priority (followed + self) and the rest
    priority_posts = [p for p in all_posts if p.creator_id in followed_ids]
    other_posts = [p for p in all_posts if p.creator_id not in followed_ids]

    # Shuffle each segment independently then merge
    random.shuffle(priority_posts)
    random.shuffle(other_posts)
    posts = priority_posts + other_posts

    events = Event.query.all()
    postform = PostForm()
    postform.event_id.choices = [(e.id, e.name) for e in events]

    liked_rows = db.session.query(Like.post_id).filter(Like.user_id == user_id).all()
    liked_post_ids = {r[0] for r in liked_rows}

    return render_template(
        'user/home.html',
        title="Home",
        postform=postform,
        user=user,
        events=events,
        posts=posts,
        current_page='home',
        liked_post_ids=liked_post_ids,
    )


# ---------------------------------------------------------------------------
# Create post
# ---------------------------------------------------------------------------

@app.route('/create-post/', methods=['POST', 'GET'])
def create_post():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user = User.query.get(user_id)
    events = Event.query.all()
    postform = PostForm()
    postform.event_id.choices = [(e.id, e.name) for e in events]

    if request.method == 'GET':
        return render_template('user/home.html', title="Home", postform=postform, user=user,
                               events=events, current_page='home')
    else:
        if postform:
            content = postform.content.data
            media = postform.media.data
            event_id = postform.event_id.data

            if media:
                filename = media.filename
                fname, ext = os.path.splitext(filename)
                newname = secrets.token_hex(32)
                filename = newname + ext
                upload_path = os.path.join('pkg/static/uploads', filename)
                media.save(upload_path)
                post = Post(creator_id=user_id, content=content, media=filename, event_id=event_id)
            else:
                post = Post(creator_id=user_id, content=content, event_id=event_id)

            db.session.add(post)
            db.session.commit()
            flash('Post Created Successfully')
            return 'Post created'


# ---------------------------------------------------------------------------
# Discover
# ---------------------------------------------------------------------------

@app.route('/discover/')
def discover():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user = User.query.get(user_id)

    # Trending events — fall back to 6 most recent if none flagged
    trending_events = Event.query.filter_by(is_trending=True).order_by(Event.created_at.desc()).all()
    if not trending_events:
        trending_events = Event.query.order_by(Event.created_at.desc()).limit(6).all()

    # Trending communities — same fallback
    trending_communities = Community.query.filter_by(is_trending=True).order_by(Community.created_at.desc()).all()
    if not trending_communities:
        trending_communities = Community.query.order_by(Community.created_at.desc()).limit(6).all()

    categories = EventCategory.query.all()

    return render_template(
        'user/discover.html',
        title="Discover",
        events=trending_events,
        communities=trending_communities,
        categories=categories,
        user=user,
        current_page='discover',
    )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@app.route('/notifications/')
def notifications():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user = User.query.get(user_id)
    notifs = Notification.query.filter_by(recipient_id=user_id).order_by(Notification.created_at.desc()).all()
    unread_count = sum(1 for n in notifs if not n.is_read)
    is_following = False
    if user_id != id:
        is_following = Follow.query.filter_by(follower_id=user_id, followed_id=user.id).first() is not None


    return render_template(
        'user/notifications.html',
        title="Notifications",
        current_page='notifications',
        user=user,
        notifs=notifs,
        unread_count=unread_count,
        is_following=is_following
    )


@csrf.exempt
@app.post('/notifications/mark-read/')
def mark_notifications_read():
    if session.get('useronline') is None:
        return jsonify(success=False, message='Login required'), 401
    user_id = session.get('useronline')
    notif_id = request.json.get('id') if request.is_json else None
    if notif_id:
        notif = Notification.query.filter_by(id=notif_id, recipient_id=user_id).first()
        if notif:
            notif.is_read = True
    else:
        # Mark all as read
        Notification.query.filter_by(recipient_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify(success=True)


# ---------------------------------------------------------------------------
# Communities
# ---------------------------------------------------------------------------

@app.route('/communities/')
def communities():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    user_id = session.get('useronline')
    user = User.query.get(user_id)
    all_communities = Community.query.order_by(Community.created_at.desc()).all()
    categories = EventCategory.query.all()
    return render_template('user/communities.html', title="Communities", communities=all_communities,
                           categories=categories, user=user, current_page='communities')


@app.route('/communities/all_communities/')
def all_comm():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    user_id = session.get('useronline')
    user = User.query.get(user_id)
    all_communities = Community.query.order_by(Community.created_at.desc()).all()
    categories = EventCategory.query.all()
    return render_template('user/all_communities.html', title="All Communities",
                           communities=all_communities, categories=categories,
                           user=user, current_page='communities')


@app.route('/all_events/')
def all_events():
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    user_id = session.get('useronline')
    user = User.query.get(user_id)
    events = Event.query.order_by(Event.created_at.desc()).all()
    categories = EventCategory.query.all()
    return render_template('user/all_events.html', title="All Events", events=events,
                           categories=categories, user=user, current_page='discover')


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

@app.route('/comments/<int:id>/', methods=['GET', 'POST'])
def comments(id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session.get('useronline')
    user = User.query.get_or_404(user_id)
    post = Post.query.get_or_404(id)
    post.post_type = 'regular'

    commentform = CommentForm()

    if commentform.validate_on_submit():
        comment = Comment(comment=commentform.comment.data, user_id=user_id, post_id=post.id)
        db.session.add(comment)

        # Notify post creator if it's not the commenter themselves
        if post.creator_id != user_id:
            notif = Notification(
                recipient_id=post.creator_id,
                actor_id=user_id,
                type='comment',
                post_id=post.id,
            )
            db.session.add(notif)

        db.session.commit()

    liked_rows = db.session.query(Like.post_id).filter(Like.user_id == user_id).all()
    liked_post_ids = {r[0] for r in liked_rows}

    events = Event.query.all()

    return render_template(
        'user/comments.html',
        title="Comments",
        user=user,
        events=events,
        p=post,
        commentform=commentform,
        comment=post.comments,
        current_page='home',
        liked_post_ids=liked_post_ids,
    )


# ---------------------------------------------------------------------------
# Like
# ---------------------------------------------------------------------------

@csrf.exempt
@app.route('/like-post/<int:id>/', methods=['POST'])
def like(id):
    if not session.get('useronline'):
        return jsonify(success=False, message='Login required'), 401

    user_id = session['useronline']
    post = Post.query.get_or_404(id)

    existing_like = Like.query.filter_by(user_id=user_id, post_id=id).first()

    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        db.session.add(Like(user_id=user_id, post_id=id))
        liked = True

        # Notify post creator (skip if self-like)
        if post.creator_id != user_id:
            # Avoid duplicate like notifications — only fire when newly liking
            notif = Notification(
                recipient_id=post.creator_id,
                actor_id=user_id,
                type='like',
                post_id=post.id,
            )
            db.session.add(notif)

    db.session.commit()

    like_count = Like.query.filter_by(post_id=id).count()
    return jsonify(success=True, liked=liked, like_count=like_count)


# ---------------------------------------------------------------------------
# Toggle join community
# ---------------------------------------------------------------------------

@csrf.exempt
@app.route('/community/<int:comm_id>/join', methods=['POST'])
def toggle_join_community(comm_id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

    user_id = session['useronline']
    community = Community.query.get_or_404(comm_id)

    membership = CommunityMember.query.filter_by(user_id=user_id, comm_id=community.id).first()

    if membership:
        db.session.delete(membership)
        joined = False
    else:
        db.session.add(CommunityMember(user_id=user_id, comm_id=community.id))
        joined = True

        # Notify community creator
        if community.creator_id != user_id:
            notif = Notification(
                recipient_id=community.creator_id,
                actor_id=user_id,
                type='community_invite',
                community_id=community.id,
            )
            db.session.add(notif)

    db.session.commit()

    member_count = CommunityMember.query.filter_by(comm_id=community.id).count()
    return jsonify(success=True, joined=joined, member_count=member_count)
