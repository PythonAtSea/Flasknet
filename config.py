import os
basedir = os.getcwd()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "nope"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
