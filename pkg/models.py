from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
   

class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), nullable=False)
    bio = db.Column(db.Text)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    verified_status = db.Column(db.Enum('verified', 'not verified'), server_default='not verified')
    account_status = db.Column(db.Enum('active', 'suspended', 'banned'), server_default='active', nullable=False)
    joined_at = db.Column(db.DateTime(), default=datetime.utcnow)

    state = db.relationship('State', back_populates='users', lazy='select')
    events = db.relationship('Event', back_populates='creator', lazy='select')
    commPosts = db.relationship('CommunityPost', back_populates='user', lazy='select')
    posts = db.relationship('Post', back_populates='creator', lazy='select')
    comments = db.relationship('Comment', back_populates='user', lazy='select')
    likes = db.relationship(
            'Like',
            back_populates='user',
            cascade='all, delete-orphan',
            lazy='select'
        )
    created_communities = db.relationship('Community', back_populates='creator', lazy='select')
    community_memberships = db.relationship('CommunityMember', back_populates='user', cascade='all, delete-orphan', lazy='select')
    event_attendances = db.relationship('EventAttendees', back_populates='user', cascade='all, delete-orphan', lazy='select')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', back_populates='follower', cascade='all, delete-orphan', lazy='select')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', back_populates='followed', cascade='all, delete-orphan', lazy='select')


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    users = db.relationship('User', back_populates='state', lazy='select')
    lgas = db.relationship('Lga', back_populates='state', lazy='select')
    events = db.relationship('Event', back_populates='state', lazy='select')


class Lga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    name = db.Column(db.String(100), nullable=False)

    state = db.relationship('State', back_populates='lgas', lazy='select')
    events = db.relationship('Event', back_populates='lga', lazy='select')
    
#Event Tables

class Event(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    banner = db.Column(db.Text, default='default.jpg')
    address = db.Column(db.String(255))
    lga_id = db.Column(db.Integer, db.ForeignKey('lga.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    map_link = db.Column(db.Text)
    cat_id = db.Column(db.Integer, db.ForeignKey('event_category.id'))
    comm_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    event_start = db.Column(db.DateTime(), default=datetime.utcnow)  
    event_end = db.Column(db.DateTime())  
    status = db.Column(db.Enum('pending','approved', 'rejected'), server_default='pending')
    visibility = db.Column(db.Enum('public', 'private'), server_default='public')
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)  
    is_trending = db.Column(db.Boolean, nullable=False, server_default='0')

    creator = db.relationship('User', back_populates='events', lazy='select')
    state = db.relationship('State', back_populates='events', lazy='select')
    lga = db.relationship('Lga', back_populates='events', lazy='select')
    category = db.relationship('EventCategory', back_populates='events', lazy='select')
    community = db.relationship('Community', back_populates='events', lazy='select')
    posts = db.relationship(
        'Post',
        back_populates='event',
        cascade='all, delete-orphan',
        lazy='select'
    )
    tickets = db.relationship(
        'EventTicket',
        back_populates='event',
        cascade='all, delete-orphan',
        lazy='select'
    )
    lineups = db.relationship(
        'EventLineup',
        back_populates='event',
        cascade='all, delete-orphan',
        lazy='select'
    )
    attendees = db.relationship(
        'EventAttendees',
        back_populates='event',
        cascade='all, delete-orphan',
        lazy='select'
    )
    community_posts = db.relationship(
        'CommunityPost',
        back_populates='event',
        cascade='all, delete-orphan',
        lazy='select'
    )


class EventCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(255))
    image = db.Column(db.Text)

    events = db.relationship('Event', back_populates='category', lazy='select')
    communities = db.relationship('Community', back_populates='category', lazy='select')


class EventTicket(db.Model):
    __tablename__ = 'event_ticket'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Enum('free', 'paid', 'table', name='ticket_category'), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    sold = db.Column(db.Integer, nullable=False, default=0)
    max_per_order = db.Column(db.Integer, nullable=False, default=1)
    seats_per_ticket = db.Column(db.Integer, nullable=True)
    sales_start = db.Column(db.DateTime())
    sales_end = db.Column(db.DateTime())
    active = db.Column(db.Boolean(), nullable=False, server_default='1')

    event = db.relationship('Event', back_populates='tickets', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'name': self.name,
            'category': self.category,
            'description': self.description or '',
            'price': float(self.price or 0),
            'quantity': self.quantity or 0,
            'sold': self.sold or 0,
            'max_per_order': self.max_per_order or 1,
            'seats_per_ticket': self.seats_per_ticket or 0,
            'sales_start': self.sales_start.strftime('%Y-%m-%dT%H:%M') if self.sales_start else '',
            'sales_end': self.sales_end.strftime('%Y-%m-%dT%H:%M') if self.sales_end else '',
            'active': bool(self.active),
        }


class EventLineup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('event_role.id'))

    event = db.relationship('Event', back_populates='lineups', lazy='select')
    role = db.relationship('EventRole', back_populates='lineups', lazy='select')


class EventRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    lineups = db.relationship('EventLineup', back_populates='role', lazy='select')


class EventAttendees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    event = db.relationship('Event', back_populates='attendees', lazy='select')
    user = db.relationship('User', back_populates='event_attendances', lazy='select')
    
    
#POSTS

class Post(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    media = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)  

    event = db.relationship('Event', back_populates='posts', lazy='select')
    creator = db.relationship('User', back_populates='posts', lazy='select')
    comments = db.relationship(
        'Comment',
        back_populates='post',
        cascade='all, delete-orphan',
        order_by='Comment.created_at.desc()',
        lazy='select'
    )
    likes = db.relationship(
        'Like',
        back_populates='post',
        cascade='all, delete-orphan',
        order_by='Like.created_at.desc()',
        lazy='select'
    )


class Comment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship('User', back_populates='comments', lazy='select')
    post = db.relationship('Post', back_populates='comments', lazy='select')


class Like(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='ux_like_user_post'),
    )

    user = db.relationship('User', back_populates='likes', lazy='select')
    post = db.relationship('Post', back_populates='likes', lazy='select')


class Community(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    banner = db.Column(db.Text)
    cat_id = db.Column(db.Integer, db.ForeignKey('event_category.id'))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)  
    verified_status = db.Column(db.Enum('verified', 'not verified'), server_default='not verified')
    is_trending = db.Column(db.Boolean, nullable=False, server_default='0')

    creator = db.relationship('User', back_populates='created_communities', lazy='select')
    category = db.relationship('EventCategory', back_populates='communities', lazy='select')
    members = db.relationship('CommunityMember', back_populates='community', cascade='all, delete-orphan', lazy='select')
    posts = db.relationship('CommunityPost', back_populates='community', cascade='all, delete-orphan', lazy='select')
    events = db.relationship('Event', back_populates='community', lazy='select')


class CommunityMember(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comm_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


    user = db.relationship('User', back_populates='community_memberships', lazy='select')
    community = db.relationship('Community', back_populates='members', lazy='select')
    
    comments = db.relationship('CommunityComment', back_populates='member', cascade='all, delete-orphan', lazy='select')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'comm_id', name='ux_community_member_user_comm'),
    )


class CommunityPost(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comm_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    content = db.Column(db.Text, nullable=False)
    media = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    created_at = db.Column(db.DateTime(), default=datetime.utcnow)  

    
    user = db.relationship('User', back_populates='commPosts', lazy='select')
    community = db.relationship('Community', back_populates='posts', lazy='select')
    event = db.relationship('Event', back_populates='community_posts', lazy='select')
    comments = db.relationship(
        'CommunityComment',
        back_populates='post',
        cascade='all, delete-orphan',
        order_by='CommunityComment.created_at.desc()',
        lazy='select'
    )


class CommunityComment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('community_member.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    member = db.relationship('CommunityMember', back_populates='comments', lazy='select')
    post = db.relationship('CommunityPost', back_populates='comments', lazy='select')


class Follow(db.Model):
    __tablename__ = 'follow'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='ux_follow_follower_followed'),
    )

    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following')
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers')


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.Enum('like', 'comment', 'follow', 'event_join', 'community_invite', name='notif_type'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id', ondelete='CASCADE'), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, server_default='0')
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    recipient = db.relationship('User', foreign_keys=[recipient_id])
    actor = db.relationship('User', foreign_keys=[actor_id])
    post = db.relationship('Post')
    event = db.relationship('Event')
    community = db.relationship('Community')
    

    
    



class TicketOrder(db.Model):
    __tablename__ = 'ticket_order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'paid', 'failed', name='order_status'), server_default='pending', nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    paid_at = db.Column(db.DateTime())

    user = db.relationship('User')
    event = db.relationship('Event')
    items = db.relationship('TicketOrderItem', back_populates='order', cascade='all, delete-orphan')


class TicketOrderItem(db.Model):
    __tablename__ = 'ticket_order_item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('ticket_order.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('event_ticket.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('TicketOrder', back_populates='items')
    ticket = db.relationship('EventTicket')