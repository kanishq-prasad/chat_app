from env import env

class Config:
    db_credentials = env['db_credentials']
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = "mysql://{}@127.0.0.1/chatapp".format(db_credentials)