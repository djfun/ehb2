import subprocess
from flask import Flask
import time
from flask import render_template

from flask_sqlalchemy_session import flask_scoped_session
from jinja2 import evalcontextfilter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import conf
from tables import Base
from sqlalchemy.orm.session import Session


__author__ = 'koller'

# set up Flask
app = Flask(__name__, static_url_path='')
app.secret_key = conf.get("server", "secret")
app.config['UPLOAD_FOLDER'] = "/tmp"

start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# set up database connection
db_url = conf.get("database", "url")
engine = create_engine(db_url)

# flask-mysqlalchemy integration
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = flask_scoped_session(DBSession, app) # type: Session


# set up Jinja rendering environment for Latex
# http://flask.pocoo.org/snippets/55/
texenv = app.create_jinja_environment()
# texenv.block_start_string = '((*'
# texenv.block_end_string = '*))'
texenv.variable_start_string = '((('
texenv.variable_end_string = ')))'
# texenv.comment_start_string = '((='
# texenv.comment_end_string = '=))'


# format float as EUR value
@app.template_filter()
@evalcontextfilter
def eur(eval_ctx, value):
    return "%s %.2f" % (conf.get("application", "currency_symbol"), value)


@app.context_processor
def utility_processor():
    def format_price(amount):
        return eur(None, amount)
    return dict(format_price=format_price)



# set up logging
import logging


# find Git revision
git_revision = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])