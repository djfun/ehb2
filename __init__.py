from flask import Flask
import time
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from tables import Base

__author__ = 'koller'


# set up Flask
app = Flask(__name__, static_url_path='')
app.secret_key = 'HbKGev1Z0G0h3J'
# app.config.from_pyfile("alto-studio.cfg")
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# set up database connection
# engine = create_engine('mysql://%s:%s@%s/%s' % (app.config["MYSQL_USER"], app.config["MYSQL_PASSWORD"], app.config["MYSQL_SERVER"], app.config["MYSQL_DB"]))
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)

# flask-sqlalchemy-session: create fresh session for each HTTP request and then close it automatically
# session = flask_scoped_session(DBSession, app)

# def DEBUG_MODE():
#     if not "DEBUG_FLASK" in app.config:
#         return False
#     else:
#         return app.config["DEBUG_FLASK"].lower() == "true"
