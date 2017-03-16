from flask import flash
from flask_login import login_required

from __init__ import *
from extras_roomtypes import roomtypes
from extras_roomtypes import Roomtype

from helpers import *


def mkrm(row, col):
    return "%d_%d" % (row, col)

# This generates the list of all room names. It is important that there are at least as many
# room names as participants + guests combined, because everyone is initially placed into
# a separate room (before you then put them together in the room planner). If you ever need more
# space than 150, increase the rows below.
ROOM_ROWS = 30
ROOM_COLS = 5
all_rooms = [[mkrm(row, col) for col in range(1,ROOM_COLS+1)] for row in range(1,ROOM_ROWS+1)]

@app.route("/room-planner.html", methods=["GET",])
@login_required
def room_planner():
    return render_template("roomplanner.html", peopleString=make_people_string(), rooms=all_rooms)

@app.route("/initialize-room-assignments.html")
@login_required
def initialize_room_assignments():
    r_room_assignments = session.query(RoomAssignment).all()
    name_to_ra = {ra.name : ra for ra in r_room_assignments}
    occupied_rooms = [ra.room for ra in r_room_assignments]

    # find first empty row
    rows_of_occupied_rooms = [int(r.split("_")[0]) for r in occupied_rooms]
    last_occupied_row = max(rows_of_occupied_rooms) if rows_of_occupied_rooms else 0
    if last_occupied_row == ROOM_ROWS:
        flash("Could not find an empty row in which to place the new participants and guests. The room planner tries to place new entries in an empty line below the lowest occupied room, but you have occupied a room in the bottom row of your room plan. Please move some people up and retry initializing. The database has not been changed.")
        return render_template("admin.html")
        # todo - test this

    # collect people to add
    row = last_occupied_row + 1
    col = 1
    entries = []

    for prt in session.query(Participant).all(): # type: Participant
        if not prt.fullname() in name_to_ra:
            entries.append(RoomAssignment(name=prt.fullname(), id=prt.id, guest_position=0, room=mkrm(row, col)))
            row, col = inc_rowcol(row, col)

    for extras in session.query(Extra).all(): # type: Extra
        if not extras.guest1_name in name_to_ra:
            entries.append(RoomAssignment(name=extras.guest1_name, id=extras.id, guest_position=1, room=mkrm(row, col)))
            row, col = inc_rowcol(row, col)

        if not extras.guest2_name in name_to_ra:
            entries.append(RoomAssignment(name=extras.guest2_name, id=extras.id, guest_position=2, room=mkrm(row, col)))
            row, col = inc_rowcol(row, col)

    # do all these people fit into the room planner?
    if len(entries) > (ROOM_ROWS-last_occupied_row) * ROOM_COLS:
        flash(("Not enough room in the room planner for the %d people who need to be added. The room planner tries to place new entries in empty rows below the lowest occupied room, but there are " + \
              "only %d free row(s) (with %d columns each) in that area. Please move some people up in your room table and try again. The database has not been changed.") % (len(entries), ROOM_ROWS-last_occupied_row, ROOM_COLS))
        return render_template("admin.html")

    # update the database
    for e in entries:
        session.add(e)
    session.commit()

    return render_template("admin.html", message="Added %d people to the room planner." % len(entries))



def inc_rowcol(row, col):
    col += 1
    if col > ROOM_COLS:
        col = 1
        row += 1

    return (row, col)



# returns string with comma-separated entries like this:
# "19": {"id": "19", "name": "Simone Knoop", "arrival": "09/06", "departure": "12/06","roomsize": 2, "tooltip":"shared with Marquis, Mira", "extras_submitted":true, "room":"4_1", "partner": "35", "gender": "F"}
# with one entry per person who needs a room
def make_people_string():
    prt_dict = id_to_participant_dict()
    entries = []

    for ra in session.query(RoomAssignment).all(): # type: RoomAssignment
        prt = prt_dict[ra.id] # type: Participant

        if not ra.guest_position:
            # room assignment for a participant
            ee = prt.extras # type: Extra

            if ee:
                e = ee[0]
                print("aaa %s" % type(e.arrival_date))

                # prt submitted extras
                arrival = e.arrival_date.strftime("%d/%m")
                departure = e.departure_date.strftime("%d/%m")
                rt = roomtypes[e.roomtype] # type: Roomtype
                tooltip = rt.tooltip(e, prt_dict) # todo - avoid "None" in js
                roompartner_code = e.roompartner if e.roompartner >= 0 else -2

                entries.append('"%d": {"id": "%d", "name": "%s", "arrival": "%s", "departure": "%s", "roomsize": %d, "tooltip": "%s", "extras_submitted": true, "room": "%s", "partner": "%d", "gender": "%s"}' % \
                               (prt.id, prt.id, prt.fullname(), arrival, departure, rt.people_in_room, tooltip, ra.room, roompartner_code, prt.sex))

            else:
                entries.append(
                    '"%d": {"id": "%d", "name": "%s", "arrival": "%s", "departure": "%s", "roomsize": %d, "tooltip": "%s", "extras_submitted": false, "room": "%s", "partner": "", "gender": "%s"}' % \
                    (prt.id, prt.id,         prt.fullname(),    arrival,         departure,            2,   "** no extras submitted **",                    ra.room,                         prt.sex))

                ## xx default arrival departure

        else:
            # room assignment for a guest
            pass

    return ",\n".join(entries)

