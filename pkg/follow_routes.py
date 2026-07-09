from flask import jsonify, session, flash, redirect, url_for, render_template
from pkg import app, csrf
from pkg.models import db, User, Follow

@csrf.exempt
@app.route('/follow/<int:user_id>/', methods=['POST'])
def toggle_follow(user_id):
    if session.get('useronline') is None:
        return jsonify(success=False, message='Login required'), 401

    follower_id = session['useronline']
    if follower_id == user_id:
        return jsonify(success=False, message="You can't follow yourself"), 400

    User.query.get_or_404(user_id)
    existing = Follow.query.filter_by(follower_id=follower_id, followed_id=user_id).first()

    if existing:
        db.session.delete(existing)
        following = False
    else:
        db.session.add(Follow(follower_id=follower_id, followed_id=user_id))
        following = True

    db.session.commit()

    # Notification hook
    if following:
        from pkg.models import Notification
        db.session.add(Notification(recipient_id=user_id, actor_id=follower_id, type='follow'))
        db.session.commit()

    follower_count = Follow.query.filter_by(followed_id=user_id).count()
    return jsonify(success=True, following=following, follower_count=follower_count)


@app.get('/profile/<int:id>/followers/')
def followers_list(id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    user = User.query.get_or_404(id)
    followers = [f.follower for f in user.followers]
    return render_template('user/followers.html', user=user, followers=followers, current_page='profile')


@app.get('/profile/<int:id>/following/')
def following_list(id):
    if session.get('useronline') is None:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('login'))
    user = User.query.get_or_404(id)
    following = [f.followed for f in user.following]
    return render_template('user/following.html', user=user, following=following, current_page='profile')
