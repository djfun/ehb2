import datetime
import re

from sqlalchemy.exc import IntegrityError
from werkzeug.utils import redirect
from wtforms.fields.core import DateField
from wtforms.fields.simple import HiddenField

from __init__ import *
from paypal import Paypal, find_payment
from tables import *
from itertools import groupby
from helpers import *
from flask import request, flash
from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField
from wtforms.validators import ValidationError
from config import conf, end_date, start_date, number_of_days

# todo - fill this in
pp2 = Paypal(2,
             lambda url: redirect(url, code=302),
             lambda id, message: None, #applyWithPaypalError(id, message),
             "/payment-success.html",
             "/payment-cancelled.html")

event_name = conf.get("application", "name")
event_shortname = conf.get("application", "shortname")

# todo
def is_guest_of(guest_id, participant_id):
    return True

class RoomConstraint:
    def __init__(self, name, fn, parameter):
        self.name = name
        self.fn = fn
        self.parameter = parameter

    # person_in_room: person we're checking the constraint for
    # participant_id: participant to whom this person belongs
    # other_people_in_room: the other people in the room (excluding the person_in_room themselves)
    def test(self, person_in_room, participant_id, other_people_in_room):
        if self.parameter:
            return self.fn(self.value, participant_id, self.parameter)
        else:
            return self.fn(self.value, participant_id)

room_constraints = {}
room_constraints["ANYONE"] = RoomConstraint("ANYONE", lambda person, participant, others: True, None)
room_constraints["WITH_PARTICIPANT"] = RoomConstraint("WITH_PARTICIPANT", lambda person, participant, others, para: all(map(lambda x: x==para, others)), None) # all others must be desired partner
room_constraints["WITH_GUEST"] = RoomConstraint("WITH_GUEST", lambda person, participant, others: all(map(lambda x: is_guest_of(x, person), others)), None)
room_constraints["WITH_ME"] = RoomConstraint("WITH_ME", lambda person, participant, others: all(map(lambda x: x == participant)), None)


class Roomtype:
    def __init__(self, id, for_participants, for_guests, people_in_room, constraint):
        self.id = id
        self.for_participants = for_participants
        self.for_guests = for_guests
        self.people_in_room = people_in_room
        self.constraint = constraint

    def __str__(self):
        return "{rt %s, part:%s, guests:%s, people:%d, cstr:%s}" % (self.id, self.for_participants, self.for_guests, self.people_in_room, self.constraint)

    def __repr__(self):
        return self.__str__()


def mybool(s):
    return s.lower() == "true" or s.lower() == "yes"

def dict_to_sel(dict):
    return [(key, dict[key]) for key in dict.keys()]

def parse_constraint(s):
    return room_constraints[s]

# parse room types
roomtype_id = 0
roomtypes = []
for key in conf["extras: roomtypes"].keys():
    values = re.split("\s*,\s*", conf["extras: roomtypes"][key])
    rt = Roomtype(roomtype_id, mybool(values[1]), mybool(values[2]), int(values[0]), parse_constraint(values[3]))
    roomtypes.append(rt)
    roomtype_id += 1

print(roomtypes)


NO_GUEST = 0 # roomtype for "no guest"; this is used when validating the form
# SHARE_WITH_GUEST = 4
# SHARE_WITH_ME = 5

# sorted_roomtype_items = sorted(roomtypes.items(), key=lambda x: x[0])
# sorted_roomtypes = [x[1] for x in sorted_roomtype_items]
# sel_guest_roomtypes = [(str(rt.id), rt.form_description) for rt in sorted_roomtypes if rt.for_guests]

sel_guest_roomtypes = [("A", "B")]
## todo - fix these


# Choices for before-show dinner
sel_restaurants = dict_to_sel(conf["extras: restaurants"])

# Choices for t-shirts
sel_t_shirt_sexes = dict_to_sel(conf["extras: t-shirt sexes"])


t_shirt_sizes = conf["extras: t-shirt sizes"]
t_shirt_costs = {key: int(t_shirt_sizes[key]) for key in t_shirt_sizes}
sel_t_shirt_sizes = [(size, "No t-shirt" if size == "0" else "%s (EUR %d)" % (size, t_shirt_costs[size])) for size in t_shirt_sizes] # iterate over original ordered_dict to preserve order


#
# class TShirt:
#     def __init__(self, size, cost):
#         self.size = size
#         self.cost = cost
#
#     def form_description(self):
#         if self.size == "0":
#             return "No t-shirt"
#         else:
#             return "%s (EUR %d)" % (self.size, self.cost)
#
# t_shirt_sizes = {"0": TShirt("0", 0),
#             "S": TShirt("S", 30),
#             "M": TShirt("M", 30),
#             "L": TShirt("L", 30),
#             "XL": TShirt("XL", 30),
#             "XXL": TShirt("XXL", 35),
#             "XXXL": TShirt("XXXL", 35)}
#
# sel_t_shirt_sizes = [(size, t_shirt_sizes[size].form_description()) for size in ["0", "S", "M", "L", "XL", "XXL", "XXXL"]]



roomcost_single = int(conf["extras: room costs"]["1"])
roomcost_double = int(conf["extras: room costs"]["2"])
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

@app.route("/extras.html", methods=["GET",])
def extras(message=None):
    # todo - check if that person has already submitted and paid for extras

    code = request.args.get('code')
    prt = lc(code)

    form = ExtrasForm(request.form)
    form.code.data = code

    return render_template("extras.html", title="Extras", form=form, prt=prt, conf=conf_for_template)


@app.route("/extras.html", methods=["POST",])
def do_extras():
    form = ExtrasForm(request.form)
    prt = lc(form.code.data)

    if form.validate():
        print(form.data)
        return "ok"

    else:
        return render_template("extras.html", title="Extras", form=form, prt=prt)


default_arrival_date = start_date
default_departure_date = end_date


_taf = {"rows":"5", "cols":"80"}

# validate the field for the departure date with this, and
# specify the name of the field for the arrival date as an argument
def dates_check(arrival_field_name):
    def _check(form, departure_field):
        if departure_field.data <= form[arrival_field_name].data:
            raise ValidationError("Departure must be after arrival!")

    return _check

def start_date_check(form, field):
    if field.data > default_arrival_date:
        raise ValidationError("Your arrival date is after EHB starts!")

def end_date_check(form, field):
    if field.data < default_departure_date:
        raise ValidationError("Your departure date is before EHB ends!")

def guest_consistency_check(guestname_field_name):
    def _check(form, guest_roomtype_field):
        grf = int(guest_roomtype_field.data)

        if grf == NO_GUEST and form[guestname_field_name].data:
            raise ValidationError("You specified a name for your guest, but chose 'no guest' as the room type.")

        if grf != NO_GUEST and not form[guestname_field_name].data:
            raise ValidationError("You specified in the room type that you want a room for your guest, but did not tell us the name of your guest.")

    return _check


# TODO - implement this once participant roomtypes work
def reciprocal_guest_check(fn_guest1_roomtype, fn_guest2_roomtype):
    def _check(form, part_roomtype_field):
        pass

    return _check

# ).verifying(
#     "You specified that you want to share your room with a guest, but you have not specified a guest who will share a room with you.",
#     extrasForm= >
# ! (
# extrasForm.participantRoomBooking.roompartnerCode == -2 & & extrasForm.guest1Room.roomtype != 3 & & extrasForm.guest2Room.roomtype != 3)
# )
# )
#



def restaurant_consistency_check(num_restaurant_field_name):
    def _check(form, restaurant_field):
        num_guests = int(form[num_restaurant_field_name].data)

        if restaurant_field.data == "None" and num_guests > 0:
            raise ValidationError("You selected a restaurant for the Saturday night dinner, but are coming with zero people. Either select 'would like to find my own dinner', or enter at least 1 under 'number of people'.")

        if restaurant_field.data != "None" and num_guests == 0:
            raise ValidationError("You specified at least one person for the Saturday night dinner, but did not select a restaurant. If you are going to find dinner on your own, we don't need to know how many people you bring. Either select a restaurant, or enter 0 under 'number of people'.")

    return _check

class ExtrasForm(Form):
    code = HiddenField("code")

    roompartner_code = SelectField("Share room with", choices=[("1", "foo"), ("2", "bar")], validators=[reciprocal_guest_check("guest1_roomtype", "guest2_roomtype")])
    # TODO - fix this

    participant_arrival = DateField("Arrival", format="%d/%m/%Y", default=default_arrival_date, validators=[start_date_check])
    participant_departure = DateField("Departure", format="%d/%m/%Y", default=default_departure_date, validators=[end_date_check, dates_check("participant_arrival")])

    guest1_roomtype = SelectField("Guest 1: room type", choices=sel_guest_roomtypes, validators=[guest_consistency_check("guest1_name")])
    guest1_name = StringField("Guest 1: name", render_kw={"placeholder": "Enter the name of Guest 1"})
    guest1_arrival = DateField("Guest 1: arrival date", format="%d/%m/%Y", default=default_arrival_date)
    guest1_departure = DateField("Guest 1: departure date", format="%d/%m/%Y", default=default_departure_date, validators=[dates_check("guest1_arrival")])

    guest2_roomtype = SelectField("Guest 2: room type", choices=sel_guest_roomtypes, validators=[guest_consistency_check("guest2_name")])
    guest2_name = StringField("Guest 2: name", render_kw={"placeholder": "Enter the name of Guest 2"})
    guest2_arrival = DateField("Guest 2: arrival date", format="%d/%m/%Y", default=default_arrival_date)
    guest2_departure = DateField("Guest 2: departure date", format="%d/%m/%Y", default=default_departure_date, validators=[dates_check("guest2_arrival")])

    num_dinner_friday = IntegerField("Extra Friday dinners", validators=[validators.NumberRange(min=0)], default=0)
    num_lunch_saturday = IntegerField("Extra Saturday lunches", validators=[validators.NumberRange(min=0)], default=0)
    num_after_concert = IntegerField("Extra after-show snacks", validators=[validators.NumberRange(min=0)], default=0)

    num_show_tickets_regular = IntegerField("Show tickets (regular)", validators=[validators.NumberRange(min=0)], default=0)
    num_show_tickets_discount = IntegerField("Show tickets (discounted)", validators=[validators.NumberRange(min=0)], default=0)

    guest = TextAreaField("Further guest info", default="Room for any other comments regarding your guests.", render_kw=_taf)

    sat_dinner_restaurant = SelectField("Restaurant", choices=sel_restaurants, validators=[restaurant_consistency_check("sat_dinner_numpeople")])
    sat_dinner_numpeople = IntegerField("Number of people", validators=[validators.NumberRange(min=0)], default=0)

    tshirt_sex = SelectField("Style", choices=sel_t_shirt_sexes)
    tshirt_size = SelectField("Size", choices=sel_t_shirt_sizes)

    phone = StringField("Your number (optional)")

    other = TextAreaField("Comments", default="Tell us anything else we need to know here.", render_kw=_taf)

