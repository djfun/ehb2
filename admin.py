import io
from collections import Set

import xlsxwriter
from flask import request
from flask import send_file
from flask.templating import render_template_string
from sqlalchemy import inspect
from wtforms import Form, validators
from wtforms.fields.core import IntegerField, SelectField, StringField, BooleanField
from wtforms.fields.simple import TextAreaField, HiddenField

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
    prts = session.query(Participant).all()
    return render_template("mailtool.html", title="Mail Tool", form=form, participants=prts)

@app.route("/mailtool.html", methods=["POST",])
@login_required
def do_mailtool():
    form = MailtoolForm(request.form)

    if form.validate():
        submit_button_label = request.form['submit']

        if not form.recipients.data:
            # no recipients selected
            prts = session.query(Participant).all()
            return render_template("mailtool.html", title="Mail Tool", form=form, participants=prts)

        if submit_button_label == "revise":
            # "revise" button clicked on confirm page
            prts = session.query(Participant).all()
            return render_template("mailtool.html", title="Mail Tool", form=form, participants=prts)

        # dryrun = True: "Send" button clicked on confirm page
        # dryrun = False: "Preview" button clicked on first Mailtool page
        dryrun = (submit_button_label != "send")

        recipients = [int(rec) for rec in form.recipients.data.split(",")]
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

        emails = ehbmail.send(recipients, form.subject.data, bodies, "Mail Tool (%s)" % current_user.id, replyto=form.replyto.data, dryrun=dryrun)

        if dryrun:
            return render_template("confirm_emails.html", title="Mail Tool", emails_with_participants=zip(emails, participants), form=form, num_emails=len(emails))

        else:
            return render_template("admin.html", message="%d email(s) were sent." % (len(emails)))



    else:
        prts = session.query(Participant).all()
        return render_template("mailtool.html", title="Mail Tool", form=form, participants=prts)


@app.route("/mailarchive.html")
@login_required
def mailarchive():
    all_emails = session.query(Email).order_by(Email.timestamp.desc()).all()
    prts = [lp(em.recipient) for em in all_emails]

    return render_template("email_list.html", title="Mail Archive", message="All sent email messages, in descending order of time they were sent:", emails_with_participants=zip(all_emails, prts))


prt_select = [(str(prt.id), prt.fullname()) for prt in session.query(Participant).all()]
_taf = {"rows":"20", "cols":"80"}

class MailtoolForm(Form):
    recipients = HiddenField()
    subject = StringField("Subject", render_kw={"placeholder":"Enter the email subject"})
    replyto = StringField("Reply-To", render_kw={"placeholder": "Enter an alternative reply-to address (optional)"})
    dryrun = BooleanField("Dry-run")
    body = TextAreaField("Body", render_kw=_taf)




@app.route("/offline-participants.html", methods=["GET",])
@login_required
def offline_participants():
    return render_template("offline-participants.html")


@app.route("/participants.xlsx")
@login_required
def participants_spreadsheet():
    # prepare Excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    df = workbook.add_format({'num_format': 'dd/mm/yy'})
    money = workbook.add_format({'num_format': '€ 0'})
    worksheet = workbook.add_worksheet()

    mapper = inspect(Participant)
    print(Participant.__table__.columns)

    for column in Participant.__table__.columns:
        print(column.key)

    fields = ["id", "firstname", "lastname", "sex", "street", "city", "zip", "country", "final_part", "part1", "part2", \
              "paypal_token", "last_paypal_status", "email", "exp_quartet", "exp_brigade", "exp_chorus", "exp_musical", "exp_reference", "application_time", "comments", "donation", "iq_username", "code"]
    date_fields = set(["application_time"])
    money_fields = set(["donation"])


    for i, f in enumerate(fields):
        worksheet.write(0, i, f, bold)

    for i, prt in enumerate(session.query(Participant)):
        row = i+1

        for col, f in enumerate(fields):
            if f in date_fields:
                worksheet.write(row, col, getattr(prt, f), df)
            elif f in money_fields:
                worksheet.write(row, col, getattr(prt, f), money)
            else:
                worksheet.write(row, col, getattr(prt, f))

    workbook.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
