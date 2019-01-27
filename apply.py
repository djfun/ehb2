import datetime
import hashlib

from sqlalchemy.exc import IntegrityError
# pymysql.err
from werkzeug.utils import redirect

import ehbmail
from __init__ import *
from paypal import Paypal, find_payment, ParticipantNotFoundException, PaymentFailedException, PaymentNotFoundException, DuplicatePaymentException
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

pp1 = Paypal(1,
             lambda url: redirect(url, code=302),
             lambda id, message: applyWithPaypalError(id, message),
             "/payment-success.html",
             "/payment-cancelled.html")

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
        new_prt = Participant(firstname=form.firstname.data, lastname=form.lastname.data,
                              sex=form.gender.data, street=form.street.data,
                              city=form.city.data, zip=form.zip.data,
                              country=form.country.data, part1=int(form.part1.data), part2=int(form.part2.data),
                              email=form.email.data, member=form.member.data, exp_quartet=form.exp_quartet.data,
                              exp_brigade=form.exp_brigade.data, exp_chorus=form.exp_chorus.data,
                              exp_musical=form.exp_musical.data, exp_reference=form.exp_reference.data,
                              application_time=datetime.datetime.now(), comments=form.comments.data,
                              registration_status=1,  # TODO - what is this for?
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

            pp1.log(new_prt.id, PP_UNINITIALIZED, "")

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


def confirmation_render(prt):
    if pp1.did_pay_before(prt):
        fee = 0
        items = []
    else:
        items = [PaymentItem("Application fee", application_fee)]
        fee = prt.final_fee

        if prt.donation > 0:
            items.append(PaymentItem("Donation", prt.donation))

    return render_template("confirm.html", prt=prt, payment_items=items, total_amount=fee, conf_data=conf_data)


@app.route('/confirm_email/<confirmation_code>')
def confirm_email(confirmation_code):
    try:
        email = confirm_token(confirmation_code)
    except:
        flash('The confirmation link is invalid.', 'danger')
        return redirect("/")
    prt = session.query(Participant).filter(Participant.email == email).first()
    if prt.confirmed:
        flash('Account already confirmed.', 'success')
    else:
        prt.confirmed = True
        prt.confirmed_on = datetime.datetime.now()
        session.add(prt)
        session.commit()
        flash('You have confirmed your account. Thanks!', 'success')

    flask_session['sn_code'] = generate_confirmation_token(prt.email)
    return redirect("confirm.html")


@app.route("/confirm.html", methods=["GET", ])
def confirmation_page():
    code = flask_session.get('sn_code')
    if code:
        try:
            email = confirm_token(code)
            prt = session.query(Participant).filter(Participant.email == email).first()
        except:
            return redirect("/")
        return confirmation_render(prt)
    return redirect("/")



def applyWithPaypalError(id, message):
    prt = session.query(Participant).filter(Participant.id == id).first()
    form = application_form(prt)
    flash(message)
    flask_session['sn_code'] = generate_confirmation_token(prt.email)
    return redirect("confirm.html")


@app.route("/payment-cancelled.html", methods=["GET", ])
def paymentCancelled():
    print(request.args)
    print(request.form)
    token = request.args.get('token')
    prt = pp1.find_by_token(token)

    pp1.log(prt.id, PP_CANCELLED, "(payment cancelled on Paypal website)")

    flash("You have cancelled payment. Your application has not been processed. Please complete payment to apply for EHB.")
    flask_session['sn_code'] = generate_confirmation_token(prt.email)
    return redirect("confirm.html")


@app.route("/payment-success.html", methods=["GET", ])
def paymentSuccess():
    # Paypal redirects the user to this URL once the user has approved the payment.
    # Now we still need to execute the payment.

    try:
        payment, prt = pp1.execute_payment(request.args)

        # amount = payment["transactions"][0]["amount"]["total"]  # get total amount from the Paypal return message
        amount = prt.final_fee + prt.donation

        # send confirmation email
        body = render_template("application_confirmation.txt", amount=int(amount), prt=prt, eventname=event_name,
                               shortname=event_shortname, final_fee=int(prt.final_fee), currency_symbol=currency_symbol)
        print(body)
        ehbmail.send([prt.id], "Application confirmed", [body], "Application page")

        return render_template("payment_confirmation.html", title="Apply!", amount=int(amount), data=prt, name=event_name, shortname=event_shortname, application_fee=int(application_fee))

    except ParticipantNotFoundException as e:
        # print("pnfe " + e.token)
        return "Unable to resolve the Paypal token '%s' to a participant. Please try resubmitting your application, or contact the organizers." % e.token
    except PaymentNotFoundException as e:
        # print("pm nfe " + e.paymentId)
        flash("Unable to resolve the Paypal payment ID '%s' to a payment. Please try resubmitting your application, or contact the organizers." % e.paymentId)
        flask_session['sn_code'] = generate_confirmation_token(prt.email)
        return redirect("confirm.html")
    except DuplicatePaymentException as e:
        amount = application_fee + e.prt.donation
        return render_template("payment_confirmation.html", title="Apply!", amount=amount, data=e.prt, name=event_name, shortname=event_shortname, application_fee=("%.2f" % application_fee))
    except PaymentFailedException as e:
        flash("Something went wrong with your Paypal payment. Please contact the organizers.")
        flask_session['sn_code'] = generate_confirmation_token(prt.email)
        return redirect("confirm.html")


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
    ret.comments.data = prt.comments
    ret.discount_code.data = prt.discounted
    ret.gdpr = prt.gdpr
    return ret


################################################
#
# for fixing the billing disaster of EHB 2017
#
################################################


@app.route("/execute-payment.html", methods=["GET", ])
def executePaymentOops():
    oops_code = request.args.get("code")
    prt = lookup_oops(oops_code)

    if prt.last_paypal_status == PP_OOPS:
        items = [PaymentItem("Application fee", application_fee)]

        if prt.donation > 0:
            items.append(PaymentItem("Donation", prt.donation))

        total_amount = application_fee + prt.donation - discount

        return render_template("oops.html", prt=prt, payment_items=items, total_amount=total_amount)
    else:
        return render_template("no_oops.html", prt=prt)


@app.route("/execute-payment.html", methods=["POST", ])
def doExecutePaymentOops():
    amount = float(request.form["amount"])
    id = int(request.form["id"])
    prt = lp(id)

    return pp1.pay(prt.id, "%s Application Fee: %s %s" % (event_shortname, prt.firstname, prt.lastname), amount)


class PaymentItem:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount
