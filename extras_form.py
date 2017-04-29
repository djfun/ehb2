import re

from wtforms.fields.core import DateField
from wtforms.fields.simple import HiddenField
from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField
from wtforms.validators import ValidationError
from config import conf, end_date, start_date, number_of_days
from extras_roomtypes import NO_GUEST, roomtypes, NO_ROOMPARTNER
from __init__ import *
from tables import Participant, Extra, TShirtSpec

default_arrival_date = start_date
default_departure_date = end_date



NO_RESTAURANT = "none"
NO_TSHIRT = "0"


def dict_to_sel(dict):
    return [(key, dict[key]) for key in dict.keys()]




# room type lists for SELECT elements
sel_participant_roomtypes = [(rt.id, rt.detailed_description) for rt in roomtypes.values() if rt.for_participants]
sel_guest_roomtypes = [(rt.id, rt.detailed_description) for rt in roomtypes.values() if rt.for_guests]

participants = session.query(Participant).all()
sel_all_participants = [(str(prt.id), prt.fullnameLF()) for prt in sorted(participants, key=lambda prt: prt.fullnameLF())]
sel_all_participants.insert(0, (NO_ROOMPARTNER, "-- no selection --"))





# Choices for before-show dinner
restaurant_names = {}
sel_restaurants = []

for key in conf["extras: restaurants"]:
    parts = re.split("\s*,\s*", conf["extras: restaurants"][key])
    restaurant_names[key] = parts[0]

    if len(parts) > 1: # restaurant has a not, put it in parentheses
        sel_restaurants.append((key, "%s (%s)" % (parts[0], parts[1])))
    else:
        sel_restaurants.append((key, parts[0]))


# Choices for t-shirts
sel_t_shirt_sexes = dict_to_sel(conf["extras: t-shirt sexes"])

t_shirt_sizes = conf["extras: t-shirt sizes"]
t_shirt_costs = {key: int(t_shirt_sizes[key]) for key in t_shirt_sizes}
sel_t_shirt_sizes = [(size, "No t-shirt" if size == NO_TSHIRT else "%s (EUR %d)" % (size, t_shirt_costs[size])) for size in t_shirt_sizes] # iterate over original ordered_dict to preserve order
sel_t_shirt_specs = [(str(row.id), row.color) for row in session.query(TShirtSpec) if row.id]


_taf = {"rows":"5", "cols":"80"}



### Validation of form fields

# checks that departure is after arrival
def dates_check(arrival_field_name):
    def _check(form, departure_field):
        if departure_field.data <= form[arrival_field_name].data:
            raise ValidationError("Departure must be after arrival!")

    return _check

# checks that arrival is <= EHB start date
def start_date_check(form, field):
    if field.data > default_arrival_date:
        raise ValidationError("Your arrival date is after EHB starts!")

# checks that departure is >= EHB end date
def end_date_check(form, field):
    if field.data < default_departure_date:
        raise ValidationError("Your departure date is before EHB ends!")

# checks that guest name is given if and only if guest roomtype is not "no guest"
def guest_consistency_check(guestname_field_name):
    def _check(form, guest_roomtype_field):
        grf = guest_roomtype_field.data

        if grf == NO_GUEST and form[guestname_field_name].data:
            raise ValidationError("You specified a name for a guest, but chose 'no guest' as the room type.")

        if grf != NO_GUEST and not form[guestname_field_name].data:
            raise ValidationError("Please tell us the name of your guest below.")

    return _check

# checks room type constraints for participants
def check_participant_roomtype_formconstraint(fn_participant_roompartner, fn_guest_roomtypes):
    def _check(form, participant_roomtype_field):
        prt_roomtype = participant_roomtype_field.data
        fc = roomtypes[prt_roomtype].form_constraint

        prt_roompartner = form[fn_participant_roompartner].data
        guest_roomtypes = [form[grt].data for grt in fn_guest_roomtypes]

        if fc:
            error = fc(prt_roompartner, guest_roomtypes)
            if error:
                raise ValidationError(error)

    return _check

# checks room type constraints for guests
def check_guest_roomtype_formconstraint(fn_participant_roomtype, fn_other_guest_roomtype):
     def _check(form, guest_roomtype_field):
         this_guest_roomtype = guest_roomtype_field.data
         other_guest_roomtype = form[fn_other_guest_roomtype].data
         prt_roomtype = form[fn_participant_roomtype].data

         fc = roomtypes[this_guest_roomtype].form_constraint

         if fc:
            error = fc(prt_roomtype, other_guest_roomtype)
            if error:
                raise ValidationError(error)

     return _check

# checks that restaurant selection is consistent with number of people in restaurant
def restaurant_consistency_check(num_restaurant_field_name):
    def _check(form, restaurant_field):
        num_guests = int(form[num_restaurant_field_name].data)

        if restaurant_field.data == NO_RESTAURANT and num_guests > 0:
            raise ValidationError("You specified at least one person for the Saturday night dinner, but did not select a restaurant. If you are going to find dinner on your own, we don't need to know how many people you bring. Either select a restaurant, or enter 0 under 'number of people'.")

        if restaurant_field.data != NO_RESTAURANT and num_guests == 0:
            raise ValidationError("You selected a restaurant for the Saturday night dinner, but are coming with zero people. Either select 'would like to find my own dinner', or enter at least 1 (for yourself) under 'number of people'.")

    return _check


class ExtrasForm(Form):
    code = HiddenField("code")

    participant_roomtype = SelectField("Room type", choices=sel_participant_roomtypes, validators=[check_participant_roomtype_formconstraint("participant_roompartner", ["guest1_roomtype", "guest2_roomtype"])])
    participant_roompartner = SelectField("Share room with", choices=sel_all_participants)

    participant_arrival = DateField("Arrival", format="%d/%m/%Y", default=default_arrival_date, validators=[start_date_check])
    participant_departure = DateField("Departure", format="%d/%m/%Y", default=default_departure_date, validators=[end_date_check, dates_check("participant_arrival")])

    guest1_roomtype = SelectField("Guest 1: room type", choices=sel_guest_roomtypes, validators=[guest_consistency_check("guest1_name"), check_guest_roomtype_formconstraint("participant_roomtype", "guest2_roomtype")])
    guest1_name = StringField("Guest 1: name", render_kw={"placeholder": "Enter the name of Guest 1"})
    guest1_arrival = DateField("Guest 1: arrival date", format="%d/%m/%Y", default=default_arrival_date)
    guest1_departure = DateField("Guest 1: departure date", format="%d/%m/%Y", default=default_departure_date, validators=[dates_check("guest1_arrival")])

    guest2_roomtype = SelectField("Guest 2: room type", choices=sel_guest_roomtypes, validators=[guest_consistency_check("guest2_name"), check_guest_roomtype_formconstraint("participant_roomtype", "guest1_roomtype")])
    guest2_name = StringField("Guest 2: name", render_kw={"placeholder": "Enter the name of Guest 2"})
    guest2_arrival = DateField("Guest 2: arrival date", format="%d/%m/%Y", default=default_arrival_date)
    guest2_departure = DateField("Guest 2: departure date", format="%d/%m/%Y", default=default_departure_date, validators=[dates_check("guest2_arrival")])

    num_dinner_friday = IntegerField("Extra Friday dinners", validators=[validators.NumberRange(min=0)], default=0)
    num_lunch_saturday = IntegerField("Extra Saturday lunches", validators=[validators.NumberRange(min=0)], default=0)
    num_after_concert = IntegerField("Extra after-show snacks", validators=[validators.NumberRange(min=0)], default=0)

    num_show_tickets_regular = IntegerField("Show tickets (regular)", validators=[validators.NumberRange(min=0)], default=0)
    num_show_tickets_discount = IntegerField("Show tickets (discounted)", validators=[validators.NumberRange(min=0)], default=0)

    guest = TextAreaField("Further guest info", default="Room for any other comments regarding your guests.", render_kw=_taf)

    # sat_dinner_restaurant = SelectField("Restaurant", choices=sel_restaurants, validators=[restaurant_consistency_check("sat_dinner_numpeople")])
    # sat_dinner_numpeople = IntegerField("Number of people", validators=[validators.NumberRange(min=0)], default=0)

    special_event_tickets = IntegerField("Tickets to special event", validators=[validators.NumberRange(min=0)], default=0)

    tshirt_sex = SelectField("Style", choices=sel_t_shirt_sexes)
    tshirt_size = SelectField("Size", choices=sel_t_shirt_sizes)
    tshirt_spec = SelectField("Color", choices=sel_t_shirt_specs)

    phone = StringField("Your number (optional)")

    other = TextAreaField("Comments", default="Tell us anything else we need to know here.", render_kw=_taf)


def make_extras_from_form(prt, form):
    return Extra(id=prt.id,
                 roomtype = form.participant_roomtype.data,
                 roompartner = int(form.participant_roompartner.data),

                 arrival_date = form.participant_arrival.data,
                 departure_date = form.participant_departure.data,

                 guest1_roomtype = form.guest1_roomtype.data,
                 guest1_name = form.guest1_name.data,
                 guest1_arrival = form.guest1_arrival.data,
                 guest1_departure = form.guest1_departure.data,

                 guest2_roomtype = form.guest2_roomtype.data,
                 guest2_name = form.guest2_name.data,
                 guest2_arrival = form.guest2_arrival.data,
                 guest2_departure = form.guest2_departure.data,

                 num_dinner_friday = form.num_dinner_friday.data,
                 num_lunch_saturday = form.num_lunch_saturday.data,
                 num_after_concert = form.num_after_concert.data,

                 num_show_tickets_regular = form.num_show_tickets_regular.data,
                 num_show_tickets_discount = form.num_show_tickets_discount.data,

                 guest = form.guest.data,

                 special_event_tickets = form.special_event_tickets.data,

                 # sat_night_restaurant = form.sat_dinner_restaurant.data,
                 # sat_night_numpeople = form.sat_dinner_numpeople.data,

                 t_shirt_sex = form.tshirt_sex.data,
                 t_shirt_size = form.tshirt_size.data,
                 t_shirt_spec = form.tshirt_spec.data,

                 phone = form.phone.data,
                 other = form.other.data
                 )


def make_form_from_extras(extras:Extra):
    ret = ExtrasForm() # type: ExtrasForm

    ret.participant_roomtype.data = extras.roomtype
    ret.participant_roompartner.data = extras.roompartner

    ret.participant_arrival.data = extras.arrival_date
    ret.participant_departure.data = extras.departure_date

    ret.guest1_roomtype.data = extras.guest1_roomtype
    ret.guest1_name.data = extras.guest1_name
    ret.guest1_arrival.data = extras.guest1_arrival
    ret.guest1_departure.data = extras.guest1_departure

    ret.guest2_roomtype.data = extras.guest2_roomtype
    ret.guest2_name.data = extras.guest2_name
    ret.guest2_arrival.data = extras.guest2_arrival
    ret.guest2_departure.data = extras.guest2_departure

    ret.num_dinner_friday.data = extras.num_dinner_friday
    ret.num_lunch_saturday.data = extras.num_lunch_saturday
    ret.num_after_concert.data = extras.num_after_concert

    ret.num_show_tickets_regular.data = extras.num_show_tickets_regular
    ret.num_show_tickets_discount.data = extras.num_show_tickets_discount

    ret.guest.data = extras.guest

    # ret.sat_dinner_restaurant.data = extras.sat_night_restaurant
    # ret.sat_dinner_numpeople.data = extras.sat_night_numpeople

    ret.tshirt_sex.data = extras.t_shirt_sex
    ret.tshirt_size.data = extras.t_shirt_size
    ret.tshirt_spec.data = extras.t_shirt_spec

    ret.special_event_tickets.data = extras.special_event_tickets

    ret.phone.data = extras.phone
    ret.other.data = extras.other

    return ret
