from datetime import date

from __init__ import *
from extras_form import ExtrasForm, make_extras_from_form, NO_TSHIRT, t_shirt_costs
from extras_roomtypes import Roomtype
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

def fd(d:date):
    return d.strftime("%d/%m/%Y")


# returns (pay_now, pay_to_hotel, items), where items is a list of entries (item description, pay_to_hotel, pay_to_ehb)
def extras_cost(extras:Extra):
    prt_roomtype = roomtypes[extras.roomtype] # type: Roomtype
    items = []

    # room costs for participant
    extra_room_cost_ehbdays = number_of_days * prt_roomtype.cost_on_ehb_days()
    room_cost_other_days = ((extras.departure_date-extras.arrival_date).days - number_of_days) * prt_roomtype.cost_on_other_days()
    items.append(("Your room (%s), %s to %s" % (prt_roomtype.description_with_roompartner(extras.roompartner), fd(extras.arrival_date), fd(extras.departure_date)), extra_room_cost_ehbdays+room_cost_other_days, 0))

    # room costs for guests
    guest1_roomcost = 0
    if extras.guest1_roomtype != NO_GUEST:
        g1rt = roomtypes[extras.guest1_roomtype] # type: Roomtype
        guest1_roomcost = (extras.guest1_departure-extras.guest1_arrival).days * g1rt.cost_on_other_days()
        items.append(("Guest: %s (%s), %s to %s" % (extras.guest1_name, g1rt.description, fd(extras.guest1_arrival), fd(extras.guest1_departure)), guest1_roomcost, 0))

    guest2_roomcost = 0
    if extras.guest2_roomtype != NO_GUEST:
        g2rt = roomtypes[extras.guest2_roomtype] # type: Roomtype
        guest2_roomcost = (extras.guest2_departure-extras.guest2_arrival).days * g2rt.cost_on_other_days()
        items.append(("Guest: %s (%s), %s to %s" % (extras.guest2_name, g2rt.description, fd(extras.guest2_arrival), fd(extras.guest2_departure)), guest2_roomcost, 0))

    # other costs for guests
    if extras.num_dinner_friday:
        items.append(("%d extra dinner(s) on Friday night" % extras.num_dinner_friday, 0, extras.num_dinner_friday*cost_fri_dinner))

    if extras.num_lunch_saturday:
        items.append(("%d extra lunch(es) on Saturday" % extras.num_lunch_saturday, 0, extras.num_lunch_saturday*cost_sat_lunch))

    if extras.num_after_concert:
        items.append(("%d extra after-concert snack(s) on Saturday" % extras.num_after_concert, 0, extras.num_after_concert*cost_after_concert))

    if extras.num_show_tickets_regular:
        items.append(("%d regular ticket(s) for the Saturday night show" % extras.num_show_tickets_regular, 0, extras.num_show_tickets_regular*cost_ticket_regular))

    if extras.num_show_tickets_discount:
        items.append(("%d discounted ticket(s) for the Saturday night show" % extras.num_show_tickets_discount, 0, extras.num_show_tickets_discount*cost_ticket_discounted))

    extra_costs_guests = extras.num_dinner_friday*cost_fri_dinner + extras.num_lunch_saturday*cost_sat_lunch + extras.num_after_concert*cost_after_concert + extras.num_show_tickets_regular*cost_ticket_regular + extras.num_show_tickets_discount*cost_ticket_discounted

    # Sat night dinner
    cost_sat_night = 0
    if extras.sat_night_numpeople:
        items.append(("Dinner for %d people at %s before the Saturday night show" % (extras.sat_night_numpeople, conf["extras: restaurants"][extras.sat_night_restaurant]), 0, extras.sat_night_numpeople*cost_sat_dinner))
        cost_sat_night = extras.sat_night_numpeople*cost_sat_dinner

    # t-shirt
    cost_tshirt = 0
    if extras.t_shirt_size != NO_TSHIRT:
        cost_tshirt = t_shirt_costs[extras.t_shirt_size]
        items.append(("%s t-shirt (%s, size %s)" % (event_shortname, conf["extras: t-shirt sexes"][extras.t_shirt_sex], extras.t_shirt_size), 0, cost_tshirt))

    pay_now = extra_costs_guests + cost_sat_night + cost_tshirt
    pay_to_hotel = extra_room_cost_ehbdays + room_cost_other_days + guest1_roomcost + guest2_roomcost

    return (pay_now, pay_to_hotel, items)



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
            extras = make_extras_from_form(prt, form)
            pay_now, pay_to_hotel, items = extras_cost(extras)

            # todo - accept payment

            return render_template("show_extras.html", prt=prt, extras=extras, pay_now=pay_now, pay_to_hotel=pay_to_hotel, items=items, conf=conf_for_template)

        else:
            return render_template("extras.html", title="Extras", form=form, prt=prt, conf=conf_for_template)

    else:
        # todo - make this pretty
        return "unknown code"