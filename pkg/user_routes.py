import os
import secrets
from flask import render_template, request, abort, redirect, url_for, flash, session, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from pkg import app, csrf
from pkg.forms import LoginForm, PostForm, CommentForm, ProfileForm
from pkg.models import db
from pkg.models import User, State, Event, Post, EventCategory, Comment, Community, Like, CommunityMember


def _build_user_stats():
    return {
        'comment_count': Comment.query.filter(Post.id==Comment.post_id).count(),
        'like_count': Like.query.filter(Post.id==Like.post_id).count()
    }

@app.errorhandler(404)
def page_not_found(error):
    return render_template('user/404.html', error=error),404

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
            
            if_exists = User.query.filter(User.email==usermail).first()
            if if_exists:
                stored_password = if_exists.password
                rsp = check_password_hash(stored_password, userpass)
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

    
@app.route('/index/signup/', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        states = State.query.all()
        return render_template('user/auth_page.html', states=states)
    else:
        user = User()
        fullname = request.form.get('userfullname')
        username = request.form.get('username')
        email = request.form.get('usermail')
        password = request.form.get('userpass')
        confirm_pass = request.form.get('userconfirmpass')
        gender = request.form.get('gender')
        state_id = request.form.get('stateid')
        
        if fullname=="" or username=="" or email=="" or password=="" or gender=="" or state_id=="":
            flash('All fields are compulsory!', category='errormsg')
            return redirect(url_for('signup'))
        elif password != confirm_pass:
            flash('The two passwords must match!', category='errormsg')
            return(redirect(url_for('signup')))
        else:
            hashed_pwd = generate_password_hash(password)
            try:
                user=User(fullname=fullname, username=username, email=email, password=hashed_pwd, gender=gender, state_id=state_id)
                db.session.add(user)
                db.session.commit()
                    
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                print("=" * 50)
                print(e)
                print("=" * 50)
                flash(str(e), "errormsg")
                return redirect(url_for("signup"))
                    
            
        
@app.route('/check/email/')
def check_email():
    email = request.args.get('email')
    check = User.query.filter(User.email==email).first()
    if check:
        return "<span class='text-danger'>This Email is already in use. Please another email.</span>"
    else:
        return "<span class='text-success'>This Email is available.</span>"
       
    
@app.get('/profile/<int:id>/')
def profile(id):
    if session.get('useronline') != None:
        user_id = session.get('useronline')
        user_deets = User.query.get(id)
        posts = Post.query.all()
        events = Event.query.all()
        comms = Community.query.all()
        event = Event.query.filter(Event.id==Post.event_id).first()
        creator = User.query.filter(User.id==Post.creator_id).first()
        state = State.query.filter(User.state_id==State.id).first()
        liked_post_ids = set()
        if session.get('useronline') is not None:
            liked_rows = db.session.query(Like.post_id).filter(Like.user_id == user_id).all()
            liked_post_ids = {r[0] for r in liked_rows}

        return render_template('user/profile.html', title="Profile", user_deets=user_deets, state=state, event=event, creator=creator, posts=posts, events=events, current_page='profile', liked_post_ids=liked_post_ids, comms=comms)
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.route('/edit-profile/')
def edit_profile():
    if session.get('useronline')!=None:
        id = session.get('useronline')
        user_deets = User.query.get(id)
        states = State.query.all()
        profileform = ProfileForm(obj=user_deets)
        profileform.state.choices=[(s.id, s.name) for s in State.query.all()]
        return render_template('user/edit_profile.html', title="Edit Profile", user_deets=user_deets, current_page='profile', states=states, profileform=profileform)
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.post('/change-profile/')
def change_profile():
    if session.get('useronline')!=None:
        id = session.get('useronline')
        user_deets = User.query.get(id)
        profileform = ProfileForm(obj=user_deets)
        fullname = profileform.fullname.data
        username = profileform.username.data
        bio= profileform.bio.data
        state= profileform.state.data
        profile_pic = profileform.profile_pic.data
        
        if profile_pic:
            filename = profile_pic.filename
            fname, ext = os.path.splitext(filename)
            newname = secrets.token_hex(32)
            filename = newname + ext
            upload_path = os.path.join('pkg/static/uploads', filename)
            profile_pic.save(upload_path)
            
            id = session.get('useronline')
            user_deets = User.query.get(id)
            user_deets.fullname = fullname
            user_deets.username = username
            user_deets.bio = bio
            user_deets.state_id = state
            user_deets.profile_pic = filename
        else:
            id = session.get('useronline')
            user_deets = User.query.get(id)
            user_deets.fullname = fullname
            user_deets.username = username
            user_deets.bio = bio
            user_deets.state_id = state
            
        
        db.session.commit()
        return 'Account Updated successfully'
    else:
        return "Access Denied"


@app.route('/home/')
def home():
    if session.get('useronline')!=None:
        
        id = session.get('useronline')
        user = User.query.get(id)
        postform= PostForm()
        posts = Post.query.order_by(Post.created_at.desc()).all()
        events = Event.query.all()
        
        postform.event_id.choices = [(s.id, s.name) for s in events]
        event = Event.query.filter(Event.id==Post.event_id).first()
        creator = User.query.filter(User.id==Post.creator_id).first()
        stats = _build_user_stats()
        # Determine which posts the current user has liked (efficient query)
        liked_rows = db.session.query(Like.post_id).filter(Like.user_id == id).all()
        liked_post_ids = {r[0] for r in liked_rows}

        return render_template('user/home.html', title="Home", postform=postform, user=user, events=events, posts=posts, event=event, creator=creator, current_page='home', stats=stats, liked_post_ids=liked_post_ids)
            
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    

@app.route('/create-post/', methods=['POST', 'GET'])
def create_post():
    if session.get('useronline')!=None:
        
        if request.method == 'GET':
            id = session.get('useronline')
            user = User.query.get(id)
            postform= PostForm()
            events = Event.query.all()
            postform.event_id.choices = [(s.id, s.name) for s in events]
            
            
            return render_template('user/home.html', title="Home", postform=postform, user=user, events=events, current_page='home')
            
        else:
            id = session.get('useronline')
            postform= PostForm()
            if postform:
                creator_id=id
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
                    
                    post = Post(creator_id=creator_id, content=content, media=filename, event_id=event_id)
                else:
                    post = Post(creator_id=creator_id, content=content, event_id=event_id)
                
                db.session.add(post)
                db.session.commit()
                flash('Post Created Successfully')
                return 'Post created'
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))

@app.route('/discover/')
def discover():
    if session.get('useronline')!=None:
        

        events = Event.query.filter(Event.id==Event.id).order_by(Event.created_at.desc()).all()
        category = EventCategory.query.filter(EventCategory.id==Event.cat_id).first()
        creator = User.query.filter(User.id==Event.creator_id).first()
        
        return render_template('user/discover.html', title="Discover", events=events, category=category, creator=creator, current_page='discover')
            
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))


@app.route('/notifications/')
def notifications():
    return render_template('user/notifications.html', title="Notifications", current_page='notifications')


@app.route('/communities/')
def communities():
    if session.get('useronline')!=None:
        id = session.get('useronline')
        user = User.query.get(id)
        communities = Community.query.all()
        category = EventCategory.query.filter(EventCategory.id==Community.cat_id).first()
        creator = User.query.filter(User.id==Community.creator_id).first()  
        
        return render_template('user/communities.html', title=".Communities", communities=communities, category=category, creator=creator, user=user, current_page='communities')
            
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))



@app.route('/communities/all_communities/')
def all_comm():
    if session.get('useronline')!=None:
        id = session.get('useronline')
        user = User.query.get(id)
        communities = Community.query.all()
        category = EventCategory.query.filter(EventCategory.id==Community.cat_id).first()
        creator = User.query.filter(User.id==Community.creator_id).first()  
        
        return render_template('user/all_communities.html', title="All Communities", communities=communities, category=category, creator=creator, user=user, current_page='communities')
            
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    
@app.route('/all_events/')
def all_events():
    if session.get('useronline')!=None:
        id = session.get('useronline')
        user = User.query.get(id)
        events = Event.query.all()
        category = EventCategory.query.filter(EventCategory.id==Event.cat_id).first()
        creator = User.query.filter(User.id==Event.creator_id).first()
        
        return render_template('user/all_events.html', title="All Events", events=events, category=category, creator=creator, user=user, current_page='discover')
            
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))


@app.route('/comments/<int:id>/', methods=['GET', 'POST'])
def comments(id):
    if session.get('useronline')!=None:
        user_id = session.get('useronline')
        user = User.query.get_or_404(user_id)
        posts = Post.query.get(id)
        events = Event.query.all()
        commentform = CommentForm()
        comments = Comment.query.all()
        event = Event.query.filter(Event.id==Post.event_id).first()
        creator = User.query.filter(User.id==Post.creator_id).first()
        
        if commentform.validate_on_submit():
            comment = Comment(comment=commentform.comment.data, user_id=user_id, post_id=posts.id)
            
            db.session.add(comment)
            db.session.commit()
            
           
            
        liked_post_ids = set()
        if session.get('useronline') is not None:
            liked_rows = db.session.query(Like.post_id).filter(Like.user_id == user_id).all()
            liked_post_ids = {r[0] for r in liked_rows}

        return render_template('user/comments.html', title="Comments",  user=user, events=events, p=posts, event=event, creator=creator, commentform=commentform, comment=comments, current_page='home', liked_post_ids=liked_post_ids)
            
        
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    
from flask import jsonify

@csrf.exempt
@app.route('/like-post/<int:id>/', methods=['POST'])
def like(id):

    if not session.get("useronline"):

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    else:
        user_id = session["useronline"]

        post = Post.query.get_or_404(id)

        existing_like = Like.query.filter_by(
            user_id=user_id,
            post_id=id
        ).first()

        if existing_like:

            db.session.delete(existing_like)

            liked = False

        else:

            db.session.add(

                Like(
                    user_id=user_id,
                    post_id=id
                )

            )

            liked = True

        db.session.commit()

        like_count = Like.query.filter_by(
            post_id=id
        ).count()

        return jsonify({

            "success": True,

            "liked": liked,

            "like_count": like_count

        })

@app.post('/post-comment')
def post_comment():
    # Toggle like/unlike via JSON API
    if session.get('useronline') is None:
        return jsonify(success=False, message='Authentication required'), 401

    user_id = session.get('useronline')
    user = User.query.get_or_404(user_id)
    post = Post.query.get(id)
    if not post:
        return jsonify(success=False, message='Post not found'), 404

    existing = Like.query.filter_by(user_id=user.id, post_id=post.id).first()
    try:
        if existing:
            db.session.delete(existing)
            db.session.commit()
            liked = False
        else:
            new_like = Like(user_id=user.id, post_id=post.id)
            db.session.add(new_like)
            db.session.commit()
            liked = True

        like_count = Like.query.filter_by(post_id=post.id).count()
        return jsonify(success=True, liked=liked, like_count=like_count), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))


@csrf.exempt
@app.route("/community/<int:comm_id>/join", methods=["POST"])
def toggle_join_community(comm_id):
    
    if session.get('useronline') != None:
        user_id = session["useronline"]
        community = Community.query.get_or_404(comm_id)
        
        membership = CommunityMember.query.filter_by(
        user_id=user_id,
        comm_id=community.id
        ).first()
        
        if membership:

            db.session.delete(membership)
            joined = False

        else:
            commjoined = CommunityMember(
                    user_id=user_id,
                    comm_id=community.id
                )
            db.session.add(commjoined)
            joined = True

        db.session.commit()
        
        member_count = CommunityMember.query.filter_by(
                comm_id=community.id
            ).count()

        return jsonify({

                "success": True,

                "joined": joined,

                "member_count": member_count

            })
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
 




