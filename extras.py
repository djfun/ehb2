from collections import Counter
from datetime import date, datetime

from flask_login import login_required

from __init__ import *
from extras_form import ExtrasForm, make_extras_from_form, NO_TSHIRT, t_shirt_costs, make_form_from_extras, \
    NO_RESTAURANT, restaurant_names
from extras_roomtypes import Roomtype
from extras_roomtypes import roomtypes, NO_ROOMPARTNER, NO_GUEST

from werkzeug.utils import redirect
from paypal import Paypal, find_payment, ParticipantNotFoundException, PaymentNotFoundException, \
    DuplicatePaymentException, PaymentFailedException
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
roomcost_single = float(conf["extras: room costs"]["1"])
roomcost_double = float(conf["extras: room costs"]["2"])
extra_cost_for_single = number_of_days*(roomcost_single-roomcost_double)
cost_fri_dinner = int(conf["extras"]["cost_fri_dinner"])
cost_sat_lunch = int(conf["extras"]["cost_sat_lunch"])
cost_after_concert = int(conf["extras"]["cost_after_concert"])
cost_sat_dinner = int(conf["extras"]["cost_sat_dinner"])
cost_ticket_regular = int(conf["extras"]["cost_ticket_regular"])
cost_ticket_discounted = int(conf["extras"]["cost_ticket_discounted"])
cost_special_event = int(conf["extras"]["cost_special_event"])
name_special_event = conf["extras"]["name_special_event"]



# variables to be made available to the website template
conf_for_template = {"roomcost_single": roomcost_single,
                     "roomcost_double": roomcost_double,
                     "cost_fri_dinner": cost_fri_dinner,
                     "cost_sat_lunch": cost_sat_lunch,
                     "cost_after_concert": cost_after_concert,
                     "cost_sat_dinner": cost_sat_dinner,
                     "cost_ticket_regular": cost_ticket_regular,
                     "cost_ticket_discounted": cost_ticket_discounted,
                     "cost_special_event": cost_special_event,
                     "shortname": conf["application"]["shortname"],
                     "s_startdate": start_date.strftime("%B %d"),
                     "s_enddate": end_date.strftime("%B %d"),
                     "num_days": number_of_days}


def find_extras(prt_id):
    x = session.query(Extra).filter(Extra.id == prt_id).first()
    return x if x else None

def fd(d:date):
    return d.strftime("%d/%m/%Y")


def meal_costs(extras:Extra):
    return extras.num_dinner_friday*cost_fri_dinner + extras.num_lunch_saturday*cost_sat_lunch + extras.num_after_concert*cost_after_concert

def ticket_costs(extras:Extra):
    return extras.num_show_tickets_regular*cost_ticket_regular + extras.num_show_tickets_discount*cost_ticket_discounted

def s_tshirt_size(extras):
    return "%s, size %s" % (conf["extras: t-shirt sexes"][extras.t_shirt_sex], extras.t_shirt_size)

def restaurant_name(extras):
    if extras.sat_night_restaurant == NO_RESTAURANT:
        return "(none)"
    else:
        return restaurant_names[extras.sat_night_restaurant]

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

    extra_costs_guests = meal_costs(extras) + ticket_costs(extras)

    # Sat night dinner
    cost_sat_night = 0
    # no Sat night dinner now
    #if extras.sat_night_numpeople:
    #    items.append(("Dinner for %d people at %s before the Saturday night show" % (extras.sat_night_numpeople, restaurant_name(extras)), 0, extras.sat_night_numpeople*cost_sat_dinner))
    #    cost_sat_night = extras.sat_night_numpeople*cost_sat_dinner

    # special event
    cost_special = 0
    if extras.special_event_tickets:
        cost_special = cost_special_event * extras.special_event_tickets
        items.append(("%d ticket(s) for the special event (%s)" % (extras.special_event_tickets, name_special_event), 0, cost_special))

    # t-shirt
    cost_tshirt = 0
    if extras.t_shirt_size != NO_TSHIRT:
        cost_tshirt = t_shirt_costs[extras.t_shirt_size]
        items.append(("%s t-shirt (%s, %s)" % (event_shortname, s_tshirt_size(extras), extras.ts_spec.color), 0, cost_tshirt))

    pay_now = extra_costs_guests + cost_sat_night + cost_tshirt + cost_special
    pay_to_hotel = extra_room_cost_ehbdays + room_cost_other_days + guest1_roomcost + guest2_roomcost

    return (pay_now, pay_to_hotel, items)



@app.route("/extras.html", methods=["GET",])
def show_extras_form(id=None, message=None):
    if not conf.getboolean("application", "accept_extras"):
        return show_message("Booking of extras is not available at this time. Please check back later.")

    # look up participant
    if id:
        prt = lp(id)
    else:
        code = request.args.get('code')
        prt = lc(code)

    if prt:
        previous_extras = find_extras(prt.id)

        if previous_extras:
            if is_extras_paid(previous_extras):
                # extras entered previously, and fully paid => show confirmation page
                return show_page_for_extras(prt, previous_extras)
            else:
                # extras entered previously, but not paid yet => show form and let them edit and resubmit
                form = make_form_from_extras(previous_extras)
        else:
            # no extras entered previously => show empty form
            form = ExtrasForm(request.form)

        if message:
            flash(message)

        form.code.data = prt.code
        return render_template("extras.html", title="Extras", form=form, prt=prt, conf=conf_for_template)

    else:
        return show_message("Unknown code. Please check that you clicked on the link in your email correctly (no characters missing from the link, etc.). If this problem persists, please contact the organizers.")


@app.route("/extras.html", methods=["POST",])
def do_extras():
    form = ExtrasForm(request.form)
    prt = lc(form.code.data)

    if prt:
        # do not overwrite previously paid extras by accident
        previous_extras = find_extras(prt.id)
        if previous_extras and is_extras_paid(previous_extras):
            return show_page_for_extras(prt, previous_extras)

        if form.validate():
            # if form is valid => insert or update extras in database
            extras = make_extras_from_form(prt, form)
            insert_or_overwrite(extras)

            # then redirect to confirmation page
            pay_now, pay_to_hotel, items = extras_cost(extras)
            return render_template("extras_confirm.html", prt=prt, extras=extras, pay_now=pay_now, pay_to_hotel=pay_to_hotel, items=items, conf=conf_for_template)
        else:
            # form not valid => do not touch database and ask for corrections
            return render_template("extras.html", title="Extras", form=form, prt=prt, conf=conf_for_template)

    else:
        return show_message("Unknown code. Please check that you clicked on the link in your email correctly (no characters missing from the link, etc.). If this problem persists, please contact the organizers.")


# Insert new extras row into database. If an extras row for this participant
# already existed, move it to the "overwritten_extras" table and then
# overwrite it in "extras".
def insert_or_overwrite(extras:Extra):
    previous_extras = session.query(Extra).filter(Extra.id == extras.id).first()

    if previous_extras:
        # move previous extra to overwritten_extras
        oe = OverwrittenExtra(id=extras.id, roomtype=extras.roomtype, roompartner=extras.roompartner, arrival_date=extras.arrival_date, departure_date=extras.departure_date,
                              num_show_tickets_regular=extras.num_show_tickets_regular, num_show_tickets_discount=extras.num_show_tickets_discount,
                              t_shirt_sex=extras.t_shirt_sex, t_shirt_size=extras.t_shirt_size, other=extras.other, guest=extras.guest,
                              num_after_concert=extras.num_after_concert, num_lunch_saturday=extras.num_lunch_saturday, num_dinner_friday=extras.num_dinner_friday,
                              guest1_name=extras.guest1_name, guest1_arrival=extras.guest1_arrival, guest1_departure=extras.guest1_departure,
                              guest2_name=extras.guest2_name, guest2_arrival=extras.guest2_arrival, guest2_departure=extras.guest2_departure,
                              last_paypal_status=extras.last_paypal_status, sat_night_restaurant=extras.sat_night_restaurant, sat_night_numpeople=extras.sat_night_numpeople,
                              phone=extras.phone, paypal_token=extras.paypal_token, special_event_tickets=extras.special_event_tickets, t_shirt_spec=extras.t_shirt_spec,
                              timestamp=datetime.now())

        session.add(oe)
        session.delete(previous_extras)

    session.add(extras)
    session.commit()


def is_extras_paid(extras:Extra):
    return extras.last_paypal_status == PP_SUCCESS


# Call this when an extras entry already exists in the database.
# This will show the select extras items, and either display a payment
# confirmation (if the payment was successful) or a Paypal button.
def show_page_for_extras(prt:Participant, extras:Extra, message=None):
    all_paid = extras.last_paypal_status == PP_SUCCESS
    pay_now, pay_to_hotel, items = extras_cost(extras)
    return render_template("extras_page.html", prt=prt, extras=extras, message=message, all_paid=all_paid, conf=conf_for_template, pay_now=pay_now, pay_to_hotel=pay_to_hotel, items=items)

@app.route("/extras_payment.html", methods=["POST",])
def do_extras_payment():
    code = request.form.get('code')
    pay_now = float(request.form.get('pay_now'))
    prt = lc(code) # type: Participant
    extras = find_extras(prt.id) # type: Extra

    if extras.last_paypal_status == PP_SUCCESS:
        return show_page_for_extras(prt, extras)
    else:
        pp2.log(prt.id, PP_UNINITIALIZED, "")
        return pp2.pay(prt.id, "%s Extras Payment: %s" % (event_shortname, prt.fullname()), pay_now)


@app.route("/extras-payment-cancelled.html", methods=["GET",])
def paymentCancelledExtras():
    token = request.args.get('token')
    extras = pp2.find_by_token(token)

    pp2.log(extras.id, PP_CANCELLED, "(payment cancelled on Paypal website)")

    return show_extras_form(id=extras.id, message="You have cancelled payment. Your extras booking is not valid until we have received your payment.")


@app.route("/extras-payment-success.html", methods=["GET",])
def paymentSuccessExtras():
    # Paypal redirects the user to this URL once the user has approved the payment.
    # Now we still need to execute the payment.

    try:
        payment, extras = pp2.execute_payment(request.args)
        prt = lp(extras.id)
        return show_page_for_extras(prt, extras)

    # note that in the exceptions, e.prt is actually an Extras item

    except ParticipantNotFoundException as e:
        return show_message("Unable to resolve the Paypal token '%s' to a participant. Please try paying for your extras again, or contact the organizers." % e.token)
    except PaymentNotFoundException as e:
        prt = lp(e.prt.id)
        return show_page_for_extras(prt, e.prt, message="Unable to resolve the Paypal payment ID '%s' to a payment. Please try paying for your extras again, or contact the organizers." % e.paymentId)
    except DuplicatePaymentException as e:
        prt = lp(e.prt.id)
        return show_page_for_extras(prt, e.prt)
    except PaymentFailedException as e:
        prt = lp(e.prt.id)
        return show_page_for_extras(prt, e.prt, message = "Something went wrong with your Paypal payment. Please contact the organizers.")



##############################################################
#
# Admin access
#
##############################################################

@app.route("/show-extras.html", methods=["GET",])
@login_required
def show_extras(message=None):
    if message:
        flash(message)

    all_participants = session.query(Participant).all()

    missing_participants = []
    prt_with_data = []

    for prt in all_participants:
        extras = find_extras(prt.id)

        if extras:
            pay_now, pay_to_hotel, items = extras_cost(extras)
            prt_with_data.append((prt, extras, pay_now, pay_to_hotel))
        else:
            missing_participants.append(prt)

    return render_template("show_extras.html", prt_with_data=prt_with_data, missing_prts=missing_participants)


@app.route("/show-extra.html", methods=["GET",])
@login_required
def show_extra():
    id = int(request.args.get('id'))
    prt = lp(id)
    extras = find_extras(id)

    if not prt:
        return show_message("Cannot resolve ID %d to a participant." % id)

    if not extras:
        return show_message("Participant %s has not booked any extras yet." % prt.fullname())

    pay_now, pay_to_hotel, items = extras_cost(extras)

    payment_steps = session.query(PaypalHistory).filter(PaypalHistory.participant_id == id).\
        filter(PaypalHistory.payment_step == 2).order_by(PaypalHistory.timestamp).all()
    ps = [(id, p.shortname()) for (id,p) in sorted(paypal_statuses.items())]

    return render_template("show_extra.html", prt=prt,
                           items=items, pay_now=pay_now, pay_to_hotel=pay_to_hotel,
                           paypal_history=payment_steps, paypal_statuses=ps)

@app.route("/change-extras.html", methods=["POST",])
@login_required
def change_extras():
    id = int(request.args.get('id'))
    prt = lp(id)
    extras = find_extras(id)

    if not prt or not extras:
        return show_message("Could not process extras change for id '%s'" % request.args.get('id'))

    if 'pp-change-button' in request.form:
        reason = request.form['pp-change-reason']
        value = int(request.form['sp-paypal-change-field'])

        pp2.log(id, value, reason)

        message="Changed PP status of %s (%d) to %d (%s; reason: %s)." % (prt.fullname(), prt.id, value, paypal_statuses[value].shortname(), reason)
        return show_extras(message)

    return show_message("Undefined command")




##############################################################
#
# Tables
#
##############################################################

@app.route("/show-meals.html")
@login_required
def show_meals():
    header = ["Nr", "Participant", "Dinner Fri", "Lunch Sat", "Midnight snack", "Cost (EUR)"]
    content = []

    for prt in session.query(Participant).all():
        extras = find_extras(prt.id) # type: Extra

        if extras:
            costs = meal_costs(extras)
            if costs > 0:
                content.append([prt.fullnameLF(), extras.num_dinner_friday, extras.num_lunch_saturday, extras.num_after_concert, costs])

    summaryRow = sortIdSummarize(content)
    return render_template("show_table.html", tables=[TableToShow(header, content, title="Prepaid Extra Meals - %s" % event_shortname, summaryRow=summaryRow)])

@app.route("/show-tickets.html")
@login_required
def show_tickets():
    header = ["Nr", "Gast", "Regulär", "Ermäßigt", "Preis (EUR)"]
    content = []

    for prt in session.query(Participant).all():
        extras = find_extras(prt.id) # type: Extra

        if extras:
            costs = ticket_costs(extras)
            if costs > 0:
                content.append([prt.fullnameLF(), extras.num_show_tickets_regular, extras.num_show_tickets_discount, costs])

    summaryRow = sortIdSummarize(content)
    return render_template("show_table.html", tables=[TableToShow(header, content, title="Bezahlte Tickets - %s" % event_shortname, summaryRow=summaryRow)])

@app.route("/show-shirts.html")
@login_required
def show_tshirts():
    # Table with individual t-shirts
    header = ["Nr", "Name", "Size", "Cost (EUR)"]
    content = []
    all_sizes = [] # list of all t-shirt sizes for all participants, with duplicates

    for prt in session.query(Participant).all():
        extras = find_extras(prt.id) # type: Extra

        if extras:
            if extras.t_shirt_size != NO_TSHIRT:
                content.append([prt.fullnameLF(), s_tshirt_size(extras), t_shirt_costs[extras.t_shirt_size]])
                all_sizes.append(s_tshirt_size(extras))

    summaryRow = sortIdSummarize(content, columns=set([2]))
    table = TableToShow(header, content, title="T-Shirts - %s" % event_shortname, summaryRow=summaryRow)

    # Table with t-shirt quantities
    size_counter = Counter(all_sizes)
    keys = list(size_counter.keys())
    keys.sort()

    qt_header = ["Size", "Quantity"]
    qt_content = [[key, size_counter[key]] for key in keys]
    qt_table = TableToShow(qt_header, qt_content, title="Order Summary", summaryRow=["Total", len(all_sizes)])

    # render template
    return render_template("show_table.html", tables=[table, qt_table])


@app.route("/show-checkin.html")
@login_required
def show_checkin():
    header = ["Nr", "Name", "T-Shirt", "Sat Dinner", "Tickets", "Meals", "Checked In"]
    content = []

    for prt in session.query(Participant).all():
        extras = find_extras(prt.id) # type: Extra

        if extras:
            content.append([
                prt.fullnameLF(),
                "--" if extras.t_shirt_size == NO_TSHIRT else s_tshirt_size(extras),
                "--" if extras.sat_night_numpeople == 0 else "%s (x %d)" % (restaurant_name(extras), extras.sat_night_numpeople),
                "--" if ticket_costs(extras) == 0 else "%d / %d" % (extras.num_show_tickets_regular, extras.num_show_tickets_discount),
                "--" if meal_costs(extras) == 0 else "%d / %d / %d" % (extras.num_dinner_friday, extras.num_lunch_saturday, extras.num_after_concert),
                ""
            ])
        else:
            content.append([prt.fullnameLF(), "--", "--", "--", "--", ""])

    sortIdSummarize(content, columns=set())
    return render_template("show_table.html", tables=[TableToShow(header, content, title="Check-In - %s" % event_shortname)])



def sortIdSummarize(content, columns=None):
    if len(content) > 0:
        content.sort(key=lambda x:x[0])          # sort by names

        summary_values = [0] * (len(content[0])-1) # make accumulators
        if columns == None:
            columns = set(range(1,len(content[0]))) # if no columns specified, summarize over all except the first one
        nr = 1

        for row in content:
            for i in range(1,len(row)):
                if i in columns:
                    summary_values[i-1] += row[i]
            row.insert(0, str(nr))
            nr += 1

        summary_values.insert(0, "Total")
        summary_values.insert(0, "")

        return summary_values
    else:
        return None