from flask import Flask
import time
from flask import render_template

from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import conf
from tables import Base


__author__ = 'koller'

# set up Flask
app = Flask(__name__, static_url_path='')
app.secret_key = conf.get("application", "secret")
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# set up database connection
db_url = conf.get("database", "url")
engine = create_engine(db_url)

# flask-mysqlalchemy integration
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = flask_scoped_session(DBSession, app)

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Started at %s" % str(start_time))

