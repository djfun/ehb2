import re
from flask import request
from werkzeug.utils import redirect
from wtforms import Form, StringField, PasswordField, HiddenField, validators
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user

from __init__ import *
import helpers
from config import conf


class User():
    def __init__(self, id, name, passwd):
        self.id = id
        self.name = name
        self.passwd = passwd

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __str__(self):
        return "%s: %s (pw %s)" % (self.id, self.name, self.passwd)


# initialize list of users who can log in
users = {}
for id, value in conf.items("users"):
    name, passwd = re.split("\s*,\s*", value)
    users[id] = User(id, name, passwd)

# set up login manager
baseurl = helpers.base_url(with_slash=True)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = baseurl + "login"
login_manager.login_message = None


@login_manager.user_loader
def load_user(user_id):
    return users[user_id]


@app.route('/login', methods=['GET', ])
def unauthorized():
    # flask-login gave us a "next" argument when it first called us;
    # after that, we hide it in a hidden field
    form = LoginForm(request.form, next=request.args.get("next"))
    return render_template('login.html', form=form, baseurl=baseurl)


@app.route('/login', methods=['POST', ])
def do_unauthorized():
    form = LoginForm(request.form)

    if form.validate():
        user = None
        for key, value in users.items():
            if form.name.data == value.id and form.passwd.data == value.passwd:
                user = value
                break

        if user:
            login_user(user)
            return redirect(form.next.data[1:])  # strip leading /

    return render_template('login.html', form=form, baseurl=baseurl)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(baseurl)


class LoginForm(Form):
    name = StringField("User name", validators=[validators.InputRequired()])
    passwd = PasswordField("Password", validators=[validators.InputRequired()])
    next = HiddenField("next")
