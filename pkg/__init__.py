from flask import Flask
from flask_wtf import CSRFProtect #form 
from flask_migrate import Migrate
from sqlalchemy import inspect, text

from pkg.config import LiveConfig

csrf = CSRFProtect()
def create_app():
    from pkg.models import db
    app=Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config.from_object(LiveConfig)
    
    
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('user')]
        if 'account_status' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN account_status VARCHAR(20) NOT NULL DEFAULT 'active'"))
            db.session.commit()

        event_columns = [column['name'] for column in inspector.get_columns('event')]
        if 'is_trending' not in event_columns:
            db.session.execute(text("ALTER TABLE event ADD COLUMN is_trending BOOLEAN NOT NULL DEFAULT 0"))
            db.session.commit()

        community_columns = [column['name'] for column in inspector.get_columns('community')]
        if 'is_trending' not in community_columns:
            db.session.execute(text("ALTER TABLE community ADD COLUMN is_trending BOOLEAN NOT NULL DEFAULT 0"))
            db.session.commit()
    
    return app

   
app = create_app()

from pkg import user_routes, admin_routes, creator_routes, ticket_routes, forms, rsvp_routes, follow_routes