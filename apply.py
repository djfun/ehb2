import datetime
import hashlib

from sqlalchemy.exc import IntegrityError
# pymysql.err
from werkzeug.utils import redirect

import ehbmail
from __init__ import *
from tables import *
from itertools import groupby
from helpers import *
from flask import request, flash
from flask import session as flask_session
from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField, BooleanField
from config import conf, currency_symbol
from discount import *
from confirmation_token import generate_confirmation_token, confirm_token
import urllib.parse

application_fee = float(conf.get("paypal", "fee"))
event_name = conf.get("application", "name")
event_shortname = conf.get("application", "shortname")
base_url = conf.get("server", "base_url")

conf_data = {"name": event_name,
             "shortname": event_shortname,
             "s_application_fee": str(application_fee),
             }

# @app.route("/apply.html", methods=["GET",])


class CodeNotFoundException(Exception):
    def __init__(self, code):
        self.code = code


class CodeInUseException(Exception):
    def __init__(self, code):
        self.code = code


def apply(message=None):
    form = ApplicationForm(request.form)
    return render_template("apply.html", title="Apply!", form=form, conf_data=conf_data)


def make_code(id):
    s = "%s #%d" % (event_shortname, id)  # generate different hashes for each new EHB instance
    return hashlib.sha224(s.encode()).hexdigest()[:16]


def apply_discount(d_code, prt_code):  # lookup discount code amount, update participant id
    if d_code == "":
        return 0
    else:
        c = session.query(DiscountCode).filter(DiscountCode.code == d_code).first()

        if c.user_id is None:
            try:
                session.query(DiscountCode).filter(DiscountCode.code ==
                                                   d_code).update({'user_id': prt_code})
                session.commit()
                return c.amount

            except AttributeError:
                raise CodeNotFoundException(d_code)

        else:
            raise CodeInUseException(d_code)


@app.route("/apply.html", methods=["POST", ])
def do_apply():
    form = ApplicationForm(request.form)

    if form.validate():
        new_prt = Participant(firstname=form.firstname.data.strip(), lastname=form.lastname.data.strip(),
                              sex=form.gender.data, street=form.street.data.strip(),
                              city=form.city.data.strip(), zip=form.zip.data.strip(),
                              country=form.country.data, part1=int(form.part1.data), part2=int(form.part2.data),
                              email=form.email.data, member=form.member.data, exp_quartet=form.exp_quartet.data,
                              exp_brigade=form.exp_brigade.data, exp_chorus=form.exp_chorus.data,
                              exp_musical=form.exp_musical.data, exp_reference=form.exp_reference.data,
                              application_time=datetime.datetime.now(), comments=form.comments.data,
                              contribution_comment=form.contribution_comment.data,
                              registration_status=1,  # (= new application)
                              donation=form.donation.data, iq_username=form.iq_username.data,
                              discounted=form.discount_code.data, confirmed=False, gdpr=form.gdpr.data
                              )

        try:
            session.add(new_prt)
            session.commit()

            new_prt.code = make_code(new_prt.id)
            session.commit()

            new_prt.final_fee = application_fee - apply_discount(new_prt.discounted, new_prt.code)
            session.commit()

            token = generate_confirmation_token(new_prt.email)
            confirmation_url = urllib.parse.urljoin(base_url, "/confirm_email/")
            confirmation_url = urllib.parse.urljoin(confirmation_url, token)

            amount = new_prt.final_fee + new_prt.donation
            # TODO2020: Create new order
            # * new_prt.id
            # * amount
            # * "application"
            # * "Application %s %s" % new_prt.firstname, new_prt.lastname
            # pp1.log(new_prt.id, PP_UNINITIALIZED, "")

            # send email with confirmation token
            body = render_template("application_confirm_email.txt", amount=int(amount), prt=new_prt, eventname=event_name,
                               shortname=event_shortname, final_fee=int(new_prt.final_fee), currency_symbol=currency_symbol,
                               confirmation_token=token, confirmation_url=confirmation_url)
            print(body)
            ehbmail.send([new_prt.id], "Application confirmed", [body], "Application page")

            return render_template("confirmation_email_sent.html", title="Apply!", amount=int(amount), data=new_prt, name=event_name,
                                shortname=event_shortname, currency_symbol=currency_symbol, application_fee=int(application_fee))

        except IntegrityError as e:
            # TODO - if participant exists AND HAS PAID, reject application for same email
            logger().error("Duplicate email in application: %s" % form.email.data)
            flash("A user with the email address '%s' already exists. Please sign up with a different email address, or contact the organizers for help." % form.email.data)
            return render_template("apply.html", title="Apply!", form=form, conf_data=conf_data)

        except CodeNotFoundException as e:
            logger().error("Cannot find discount code : %s" % form.discount_code.data)
            flash("The scholarship code you entered is not valid: '%s'. Please try again." %
                  form.discount_code.data)
            return render_template("apply.html", title="Apply!", form=form, conf_data=conf_data)

        except CodeInUseException as e:
            logger().error("Discount code already in use : %s" % form.discount_code.data)
            flash("The scholarship code you entered is already in use: '%s'." %
                  form.discount_code.data)
            return render_template("apply.html", title="Apply!", form=form, conf_data=conf_data)

        except Exception as e:
            logger().error("Exception in do_apply: %s" % str(e))
            flash("A database error occurred. Please resubmit your application in a few minutes. If the problem persists, please contact the organizers.")
            return render_template("apply.html", title="Apply!", form=form, conf_data=conf_data)

    else:
        return render_template("apply.html", title="Apply!", form=form, conf_data=conf_data)


class ApplicationForm(Form):
    email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={
                        "placeholder": "Enter your email address"})
    firstname = StringField("First Name", validators=[validators.InputRequired()], render_kw={
                            "placeholder": "Enter your first name"})
    lastname = StringField("Last Name", validators=[validators.InputRequired()], render_kw={
                           "placeholder": "Enter your last name"})
    gender = SelectField("Gender", choices=[("M", "male"), ("F", "female")])

    street = StringField("Street", validators=[validators.InputRequired()], render_kw={
                         "placeholder": "Enter your street address"})
    city = StringField("City", validators=[validators.InputRequired()], render_kw={
                       "placeholder": "Enter the city you live in"})
    zip = StringField("Zip / Post code", validators=[validators.InputRequired()], render_kw={
                      "placeholder": "Enter the zip/post code of your city"})
    country = SelectField("Country", choices=country_list)

    donation = IntegerField("Donation (optional)", validators=[
                            validators.NumberRange(min=0)], default=0)

    part1 = SelectField("Preferred voice part", choices=[
                        ("1", "Tenor"), ("2", "Lead"), ("3", "Baritone"), ("4", "Bass")])
    part2 = SelectField("Alternative voice part", choices=[
                        ("0", "None"), ("1", "Tenor"), ("2", "Lead"), ("3", "Baritone"), ("4", "Bass")])

    member = BooleanField("I am a member of EHB.")

    exp_quartet = TextAreaField(
        "Quartetting experience", render_kw={"rows": "5", "cols": "80", "placeholder": "List your Barbershop QUARTET experience(s) here. If applicable, include representative contest scores."})
    exp_brigade = TextAreaField(
        "Brigade experience", render_kw={"rows": "5", "cols": "80", "placeholder": "List any other Harmony Brigade or Extreme Quartetting events in which you have participated."})
    exp_chorus = TextAreaField("Barbershop chorus experience", render_kw={
                               "rows": "5", "cols": "80", "placeholder": "List your Barbershop CHORUS experience(s) here."})
    exp_musical = TextAreaField(
        "Performance experience", render_kw={"rows": "5", "cols": "80", "placeholder": "Describe any performance experience, musical education, and/or accomplishments."})
    exp_reference = TextAreaField("Musical reference",  render_kw={
                                  "rows": "5", "cols": "80", "placeholder": "Please provide the name and e-mail address of someone we can contact who is familiar with your singing ability (e.g., your chorus director or section leader, coach, judge, etc.). Feel free to list multiple names."})

    iq_username = StringField("IQ account", render_kw={
                              "placeholder": "Enter your IQ account name (optional)"})

    contribution_comment = TextAreaField("Your contribution", render_kw={
        "rows": "5", "cols": "80", "placeholder": "Besides coming fully prepared on your music, what can you do to help make the %s rally a success?" % event_shortname})

    comments = TextAreaField("Comments", render_kw={
                             "rows": "5", "cols": "80", "placeholder": "Room for anything else you would like to say."})

    discount_code = StringField("Scholarship code", [validators.Length(min=0, max=8, message="Code must be %(min)d digits long.")], render_kw={
        "placeholder": "Enter your discount code (optional)"})

    gdpr = BooleanField("I agree", validators=[validators.DataRequired()])


def application_form(prt):
    ret = ApplicationForm()
    ret.email.data = prt.email
    ret.firstname.data = prt.firstname
    ret.lastname.data = prt.lastname
    ret.gender.data = prt.shortsex()
    ret.street.data = prt.street
    ret.city.data = prt.city
    ret.zip.data = prt.zip
    ret.country.data = prt.country
    ret.donation.data = prt.donation
    ret.part1.data = prt.part1
    ret.part2.data = prt.part2
    ret.member.data = prt.member
    ret.exp_quartet.data = prt.exp_quartet
    ret.exp_brigade.data = prt.exp_brigade
    ret.exp_chorus.data = prt.exp_chorus
    ret.exp_musical.data = prt.exp_musical
    ret.exp_reference.data = prt.exp_reference
    ret.iq_username.data = prt.iq_username
    ret.contribution_comment = prt.contribution_comment
    ret.comments.data = prt.comments
    ret.discount_code.data = prt.discounted
    ret.gdpr = prt.gdpr
    return ret
