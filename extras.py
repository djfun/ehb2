
from __init__ import *
from extras_form import ExtrasForm
from extras_roomtypes import roomtypes, NO_ROOMPARTNER, NO_GUEST

from werkzeug.utils import redirect
from paypal import Paypal, find_payment
from helpers import *
from flask import request, flash
from config import conf, end_date, start_date, number_of_days

pp2 = Paypal(2,
             lambda url: redirect(url, code=302),
             lambda id, message: None,
             "/extras-payment-success.html",
             "/extras-payment-cancelled.html")



# Extract information from config file
event_name = conf.get("application", "name")
event_shortname = conf.get("application", "shortname")
roomcost_single = int(conf["extras: room costs"]["1"])
roomcost_double = int(conf["extras: room costs"]["2"])
extra_cost_for_single = number_of_days*(roomcost_single-roomcost_double)
cost_fri_dinner = int(conf["extras"]["cost_fri_dinner"])
cost_sat_lunch = int(conf["extras"]["cost_sat_lunch"])
cost_after_concert = int(conf["extras"]["cost_after_concert"])
cost_sat_dinner = int(conf["extras"]["cost_sat_dinner"])
cost_ticket_regular = int(conf["extras"]["cost_ticket_regular"])
cost_ticket_discounted = int(conf["extras"]["cost_ticket_discounted"])



# variables to be made available to the website template
conf_for_template = {"roomcost_single": roomcost_single,
                     "roomcost_double": roomcost_double,
                     "cost_fri_dinner": cost_fri_dinner,
                     "cost_sat_lunch": cost_sat_lunch,
                     "cost_after_concert": cost_after_concert,
                     "cost_sat_dinner": cost_sat_dinner,
                     "cost_ticket_regular": cost_ticket_regular,
                     "cost_ticket_discounted": cost_ticket_discounted,
                     "shortname": conf["application"]["shortname"],
                     "s_startdate": start_date.strftime("%B %d"),
                     "s_enddate": end_date.strftime("%B %d"),
                     "num_days": number_of_days}


def find_extras(prt_id):
    x = session.query(Extra).filter(Extra.id == prt_id).first()
    return x if x else None

@app.route("/extras.html", methods=["GET",])
def extras(message=None):
    # todo - reject if extras not accepted yet
    code = request.args.get('code')
    prt = lc(code)

    if prt:
        previous_extras = find_extras(prt.id)

        if previous_extras:
            # todo - also check if they paid yet
            return render_template("show_extras.html", prt=prt, extras=previous_extras)

        else:
            form = ExtrasForm(request.form)
            form.code.data = code
            return render_template("extras.html", title="Extras", form=form, prt=prt, conf=conf_for_template)

    else:
        # todo - make this pretty
        return "unknown code"


@app.route("/extras.html", methods=["POST",])
def do_extras():
    form = ExtrasForm(request.form)
    prt = lc(form.code.data)

    if prt:
        if form.validate():
            print(form.data)

            # todo - accept payment
            # todo - generate Extra object and insert it into database
            extras = None

            return render_template("show_extras.html", prt=prt, extras=extras)

        else:
            return render_template("extras.html", title="Extras", form=form, prt=prt, conf=conf_for_template)

    else:
        # todo - make this pretty
        return "unknown code"