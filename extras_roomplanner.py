from flask import Response
from flask import flash
from flask import request
from flask_login import login_required

from __init__ import *
from config import start_date, end_date
from extras_roomtypes import roomtypes, NO_GUEST
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

# Write room planner entries to database.
# The current room assignments are sent as part of the POST request; see make_submit_button_handler in room_planner_script.js.
# The method returns the string "success" if successful to indicate to the Ajax
# callback that everything worked well.
@app.route("/room-planner.html", methods=["POST",])
@login_required
def save_room_planner():
    data = request.get_json() # Python dictionary of assignment_* and pos_* to values

    for ra in session.query(RoomAssignment).all(): # type: RoomAssignment
        if ra.guest_position:
            key = "assignment_" + make_guest_key(ra)
        else:
            key = "assignment_%d" % ra.id

        ra.room = data[key]

    session.commit()
    return "success"




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
            if extras.guest1_roomtype != NO_GUEST:
                entries.append(RoomAssignment(name=extras.guest1_name, id=extras.id, guest_position=1, room=mkrm(row, col)))
                row, col = inc_rowcol(row, col)

        if not extras.guest2_name in name_to_ra:
            if extras.guest2_roomtype != NO_GUEST:
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

# date format for roomplanner cards
rp_df = "%d/%m"

def make_guest_key(ra:RoomAssignment):
    return "%d_g%d" % (ra.id, ra.guest_position)

def make_people_string():
    """
    Returns a string of comma-separated entries, one per person who should be displayed in the room planner.
    See below for the formats for participants and guests.
    :return:
    """

    prt_dict = id_to_participant_dict()
    entries = []

    df_startdate = start_date.strftime(rp_df)
    df_enddate   = end_date.strftime(rp_df)

    for ra in session.query(RoomAssignment).all(): # type: RoomAssignment
        prt = prt_dict[ra.id] # type: Participant

        if not ra.guest_position:
            # Room assignment for a participant. This produces a string of the following form:
            # "19": {"id": "19", "name": "Simone Knoop", "arrival": "09/06", "departure": "12/06","roomsize": 2, "tooltip":"shared with Marquis, Mira", "extras_submitted":true, "room":"4_1", "partner": "35", "gender": "F"}

            ee = prt.extras
            if ee:
                # prt submitted extras
                e = ee[0] # type: Extra
                arrival = e.arrival_date.strftime(rp_df)
                departure = e.departure_date.strftime(rp_df)
                rt = roomtypes[e.roomtype] # type: Roomtype
                tooltip = rt.tooltip(e, prt_dict)
                roompartner_code = rt.roompartner_code(e) # type: str

                entries.append('"%d": {"id": "%d", "name": "%s", "arrival": "%s", "departure": "%s", "roomsize": %d, "tooltip": "%s", "extras_submitted": true, "room": "%s", "partner": "%s", "gender": "%s"}' % \
                               (prt.id,     prt.id,    prt.fullname(),     arrival,         departure,    rt.people_in_room,     tooltip,                               ra.room,    roompartner_code,   prt.sex))

            else:
                entries.append(
                    '"%d": {"id": "%d", "name": "%s", "arrival": "%s", "departure": "%s", "roomsize": %d, "tooltip": "%s", "extras_submitted": false, "room": "%s", "partner": "", "gender": "%s"}' % \
                    (prt.id, prt.id,         prt.fullname(),    df_startdate,      df_enddate,            2,   "** no extras submitted **",                    ra.room,                         prt.sex))


        else:
            # Room assignment for a guest. This produces a string of the following form:
            # "124_g1": {"id": "124_g1", "name": "x", "arrival": "16/06", "departure": "18/06", "roomsize": 2, "tooltip": "(guest of Alexander Koller) share with participant", "extras_submitted": true, "room": "18_1", "partner": "3", "guest_of": "124"}

            ee = prt.extras[0] # type: Extra
            arrival, departure, rt_id = (ee.guest1_arrival, ee.guest1_departure, ee.guest1_roomtype) if ra.guest_position == 1 else (ee.guest2_arrival, ee.guest2_departure, ee.guest2_roomtype)
            df_arrival, df_departure = [date.strftime(rp_df) for date in (arrival, departure)]
            rt = roomtypes[rt_id] # type: Roomtype

            tooltip = rt.tooltip(e, prt_dict)
            roompartner_code = rt.roompartner_code(e) # type: str
            guest_id = make_guest_key(ra)

            entries.append(
                '"%s": {"id": "%s", "name": "%s", "arrival": "%s", "departure": "%s", "roomsize": %d, "tooltip": "%s", "extras_submitted": true, "room": "%s", "partner": "%s", "guest_of": "%d"}' % \
                (guest_id, guest_id, ra.name, df_arrival, df_departure, rt.people_in_room, tooltip, ra.room, roompartner_code, prt.id))


    return ",\n".join(entries)

