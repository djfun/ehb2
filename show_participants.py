import datetime

from flask_login import login_required

from __init__ import *
from tables import *
from itertools import groupby
from helpers import *
from flask import request
from auth import *


@app.route("/show-participants.html", methods=["GET", ])
@login_required
def show_participants(message=None):
    participants = session.query(Participant).all()
    paid_participants = session.query(Participant).\
        join(Participant.orders).\
        filter(Order.short_description == "application").\
        filter(Order.status == OrderStatus.paid).all()
    total_donations = sum([p.donation for p in participants])
    part_data = make_part_data(paid_participants)
    country_data = make_country_data(paid_participants)

    return render_template("show_participants.html", title="Show participants", message=message,
                           participants=participants, total_donations=total_donations,
                           part_data=part_data, country_data=country_data)


@app.route("/show-participant.html")
@login_required
def show_participant():
    id = int(request.args.get('id'))
    participant = session.query(Participant).filter(Participant.id == id).first()
    orders = session.query(Order).filter(Order.participant_id == id).all()

    return render_template("show_participant.html", title="Participant details", data=participant, orders=orders)


@app.route("/show-participants.html", methods=["POST", ])
@login_required
def do_show_participants():
    id = int(request.args.get('id'))
    parti = lp(id)

    if 'delete-button' in request.form:
        if request.form['delete-field'] == 'delete!':
            prt = session.query(Participant).filter(
                Participant.id == id).first()  # type: Participant
            deleted_prt = DeletedParticipant(id=prt.id, firstname=prt.firstname, lastname=prt.lastname,
                                             sex=prt.sex, street=prt.street,
                                             city=prt.city, zip=prt.zip,
                                             country=prt.country, part1=prt.part1, part2=prt.part2,
                                             member=prt.member,
                                             email=prt.email, exp_quartet=prt.exp_quartet,
                                             exp_brigade=prt.exp_brigade, exp_chorus=prt.exp_chorus,
                                             exp_musical=prt.exp_musical, exp_reference=prt.exp_reference,
                                             application_time=prt.application_time, comments=prt.comments,
                                             contribution_comment=prt.contribution_comment,
                                             registration_status=prt.registration_status,
                                             donation=prt.donation, iq_username=prt.iq_username,
                                             final_part=prt.final_part,
                                             discounted=prt.discounted,
                                             final_fee=prt.final_fee,
                                             code=prt.code,
                                             deletion_time=datetime.datetime.now())

            session.query(Participant).filter_by(id=id).delete()
            session.query(Extra).filter_by(id=id).delete()
            session.add(deleted_prt)
            session.commit()
            message = "Deleted user %s (%d)." % (parti.fullname(), id)
        else:
            message = "Wrong password, did not delete user %s (%d)." % (parti.fullname(), id)

    return show_participants(message=message)


part_colors = ["000000", "428BCA", "5CB85C", "F0AD4E", "D9534F"]
part_highlight_colors = ["000000", "5DA6E6", "78D077", "FCC671", "E16864"]

country_colors = [
    "262BC0",
    "5226C0",
    "8326C0",
    "B326C0",
    "C0269D",
    "C0266C",
    "C0263C",
    "C04126",
    "C07226",
    "C0A226",
    "AEC026",
    "7EC026",
    "4DC026",
    "26C030",
    "26C061",
    "26C091",
    "26BFC0",
    "268EC0",
    "265EC0"]
country_highlight_colors = [
    "7D7DDB",
    "997DDB",
    "B57DDB",
    "D17DDB",
    "DB7DC9",
    "DB7DAD",
    "DB7D91",
    "DB857D",
    "DBA17D",
    "DBBD7D",
    "DBD97D",
    "C0DB7D",
    "A4DB7D",
    "88DB7D",
    "7DDB8D",
    "7DDBA9",
    "7DDBC5",
    "7DD4DB"]


def participants_by(all_participants, fn):
    s = sorted(all_participants, key=fn)
    return groupby(s, fn)


def make_part_data(all_participants):
    p_by_part = participants_by(all_participants, lambda p: p.final_part)
    return ["{ value: %d, color:'#%s', highlight:'#%s', label:'%s'}" %
            (len(list(people)), part_colors[part], part_highlight_colors[part], lparts[part])
            for (i, (part, people)) in enumerate(p_by_part)]


def make_country_data(all_participants):
    p_by_country = participants_by(all_participants, lambda p: p.country)
    return ["{ value: %d, color:'#%s', highlight:'#%s', label:'%s'}" %
            (len(list(people)), country_colors[i],
             country_highlight_colors[i], countries[country].name_en)
            for (i, (country, people)) in enumerate(p_by_country)]
