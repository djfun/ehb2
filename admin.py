from flask import request
from flask.templating import render_template_string
from wtforms import Form, validators
from wtforms.fields.core import IntegerField, SelectField, StringField, BooleanField
from wtforms.fields.simple import TextAreaField

import ehbmail
from __init__ import *
from extras import extras_cost
from tables import *
from helpers import *
from flask_login import login_required, current_user


@app.route('/admin.html')
@login_required
def adminpage():
    return render_template("admin.html")

@app.route("/mailtool.html", methods=["GET",])
@login_required
def mailtool():
    form = MailtoolForm(request.form)
    return render_template("mailtool.html", title="Mail Tool", form=form)

@app.route("/mailtool.html", methods=["POST",])
@login_required
def do_mailtool():
    form = MailtoolForm(request.form)

    if form.validate():
        recipients = [int(form.recipient.data)] # todo - get list
        bodies = []
        participants = []

        for recipient in recipients:
            prt = lp(recipient)  # type: Participant
            ee = prt.extras

            if ee:
                e = ee[0]
                pay_now, pay_to_hotel, items = extras_cost(e)
            else:
                e, pay_now, pay_to_hotel, items = None, None, None, None

            bodies.append(render_template_string(form.body.data, prt=prt, extras=e, pay_now=pay_now, pay_to_hotel=pay_to_hotel, items=items))
            participants.append(prt)

        emails = ehbmail.send(recipients, form.subject.data, bodies, "Mail Tool (%s)" % current_user.id, replyto=form.replyto.data, dryrun=form.dryrun.data)

        if form.dryrun.data:
            message = "The following %d emails were NOT sent (dry-run):" % (len(emails))
        else:
            message = "The following %d emails were sent:" % (len(emails))

        return render_template("email_list.html", title="Mail Tool", message=message, emails_with_participants=zip(emails, participants))

    else:
        return render_template("mailtool.html", title="Mail Tool", form=form)


@app.route("/mailarchive.html")
@login_required
def mailarchive():
    all_emails = session.query(Email).order_by(Email.timestamp.desc()).all()
    prts = [lp(em.recipient) for em in all_emails]

    return render_template("email_list.html", title="Mail Archive", message="All sent email messages, in descending order of time they were sent:", emails_with_participants=zip(all_emails, prts))


prt_select = [(str(prt.id), prt.fullname()) for prt in session.query(Participant).all()]
_taf = {"rows":"20", "cols":"80"}

class MailtoolForm(Form):
    recipient = SelectField("Recipient ID", choices=prt_select)
    subject = StringField("Subject", validators=[validators.InputRequired()], render_kw={"placeholder":"Enter the email subject"})
    replyto = StringField("Reply-To", render_kw={"placeholder": "Enter an alternative reply-to address (optional)"})
    dryrun = BooleanField("Dry-run")
    body = TextAreaField("Body", render_kw=_taf)

