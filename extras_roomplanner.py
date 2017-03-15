from flask_login import login_required

from __init__ import *
from helpers import *


all_rooms = [["%d_%d".format(row, col) for col in range(1,6)] for row in range(1,21)]

@app.route("/room-planner.html", method=["GET",])
@login_required
def room_planner():
    return ""


def make_tooltip(extras:Extra, prt_dict):
    pass


# returns string with comma-separated entries like this:
# "19": {"id": "19", "name": "Simone Knoop", "arrival": "09/06", "departure": "12/06","roomsize": 2, "tooltip":"shared with Marquis, Mira", "extras_submitted":true, "room":"4_1", "partner": "35", "gender": "F"}
# with one entry per person who needs a room
def make_people_string():
    prt_dict = id_to_participant_dict()
    entries = []

    for ra in session.query(RoomAssignment).all():
        prt = prt_dict[ra.id] # type: Participant

        if prt:
            # room assignment for a participant
            e = prt.extras # type: Extra

            if e:
                # prt submitted extras
                arrival = time.strftime("%d/%m", e.arrival_date)
                departure = time.strftime("%d/%m", e.departure_date)
                tooltip = make_tooltip(e, prt_dict)


        else:
            # room assignment for a guest
            pass



    pass