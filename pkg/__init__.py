from flask import Flask, session
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy import inspect, text

from pkg.config import LiveConfig

csrf = CSRFProtect()

def create_app():
    from pkg.models import db, Event, Follow, User

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config.from_object(LiveConfig)

    db.init_app(app)
    migrate = Migrate(app, db)
    csrf.init_app(app)

   

    @app.context_processor
    def inject_default_sidebar():
        trending = Event.query.filter_by(status='approved', is_trending=True).order_by(Event.created_at.desc()).limit(3).all()
        if not trending:
            trending = Event.query.filter_by(status='approved').order_by(Event.created_at.desc()).limit(3).all()

        suggested_creators = []
        if session.get('useronline'):
            followed_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=session['useronline']).all()]
            suggested_creators = User.query.filter(
                User.id != session['useronline'],
                ~User.id.in_(followed_ids)
            ).order_by(db.func.rand()).limit(3).all()

        return dict(default_trending_events=trending, suggested_creators=suggested_creators)

    return app


app = create_app()

from pkg import user_routes, admin_routes, creator_routes, ticket_routes, forms, rsvp_routes, follow_routes, qr_routes