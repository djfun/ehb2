import datetime

from __init__ import *
from tables import *
from itertools import groupby
from helpers import *
from flask import request
from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField


@app.route("/apply.html", methods=["GET",])
def apply(message=None):
    form = ApplicationForm(request.form)
    return render_template("apply.html", title="Apply!", form=form)

_taf = {"rows":"5", "cols":"80"}


class ApplicationForm(Form):
    email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter your email address"})
    firstname = StringField("First Name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your first name"})
    lastname = StringField("Last Name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your last name"})
    gender = SelectField("Gender", choices=[("M", "male"), ("F", "female")])

    street = StringField("Street", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your street address"})
    city = StringField("City", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the city you live in"})
    zip = StringField("Zip / Post code", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the zip/post code of your city"})
    country = SelectField("Country", choices=country_list)

    donation = IntegerField("Donation (optional)", validators=[validators.NumberRange(min=0)], default=0)

    part1 = SelectField("Preferred voice part", choices=[("1", "Tenor"), ("2", "Lead"), ("3", "Baritone"), ("4", "Bass")])
    part2 = SelectField("Alternative voice part", choices=[("0", "None"), ("1", "Tenor"), ("2", "Lead"), ("3", "Baritone"), ("4", "Bass")])

    exp_quartet = TextAreaField("Quartetting experience", default="List your Barbershop QUARTET experience(s) here. If applicable, include representative contest scores.", render_kw=_taf)
    exp_brigade= TextAreaField("Brigade experience", default="List any other Harmony Brigade or Extreme Quartetting events in which you have participated.", render_kw=_taf)
    exp_chorus = TextAreaField("Barbershop chorus experience", default="List your Barbershop CHORUS experience(s) here.", render_kw=_taf)
    exp_musical = TextAreaField("Performance experience", default="Describe any performance experience, musical education, and/or accomplishments.", render_kw=_taf)
    exp_reference = TextAreaField("Musical reference", default="Please provide the name and e-mail address of someone we can contact who is familiar with your singing ability (e.g., your chorus director or section leader, coach, judge, etc.). Feel free to list multiple names.", render_kw=_taf)

    iq_username = StringField("IQ account", render_kw={"placeholder": "Enter your IQ account name (optional)"})
    comments = TextAreaField("Comments", default="Room for anything else you would like to say.", render_kw=_taf)


@app.route("/payment.html", methods=["POST",])
def do_payment():
    form = ApplicationForm(request.form)

    if form.validate():
        return str(form.data)
    else:
        return render_template("apply.html", title="Apply!", form=form)
