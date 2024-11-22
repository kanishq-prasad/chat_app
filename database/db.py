from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
from threading import Lock
from env import env


db = SQLAlchemy()
session_lock = Lock()  # For thread-safe session management

# Create scoped session factory
engine = create_engine('mysql://{}@127.0.0.1/chatapp'.format(env['db_credentials']))
db_session = scoped_session(sessionmaker(bind=engine))

@contextmanager
def safe_session():
    """Thread-safe database session context manager"""
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()