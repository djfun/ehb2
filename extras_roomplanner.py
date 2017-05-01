import io
from collections import defaultdict

import itertools
import xlsxwriter
from flask import Response
from flask import flash
from flask import make_response
from flask import request
from flask import send_file
from flask_login import login_required

from __init__ import *
from config import start_date, end_date
from extras import extras_cost
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
flattened_all_rooms = itertools.chain.from_iterable(all_rooms)

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
    data = request.get_json() # type: dict

    for ra in session.query(RoomAssignment).all(): # type: RoomAssignment
        if ra.guest_position:
            key = make_guest_key(ra)
        else:
            key = str(ra.id)

        ra.room = data[key]

    session.commit()
    return "success"



# german_df = "%d.%m.%Y"

@app.route("/room-assignments.xlsx")
@login_required
def send_room_assignemnts_xslx():
    # get data from database
    prt_dict = id_to_participant_dict()
    r_room_assignments = session.query(RoomAssignment).all()
    room_to_ra = defaultdict(list)
    for ra in r_room_assignments:
        room_to_ra[ra.room].append(ra)

    # prepare Excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    df = workbook.add_format({'num_format': 'dd/mm/yy'})
    money = workbook.add_format({'num_format': '€ 0'})
    worksheet = workbook.add_worksheet()

    # header row
    worksheet.write(0, 0, "Nr", bold)
    worksheet.write(0, 1, "Name", bold)
    worksheet.write(0, 2, "Status", bold)
    worksheet.write(0, 3, "Anreise", bold)
    worksheet.write(0, 4, "Abreise", bold)
    worksheet.write(0, 5, "Zahlt", bold)

    # column widths
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 30)

    # fill with data
    row = 2
    nr = 1

    for room in flattened_all_rooms:
        for ra in room_to_ra[room]:
            prt = prt_dict[ra.id] # type: Participant
            worksheet.write(row, 0, nr)
            worksheet.write(row, 1, ra.name)

            if not ra.guest_position:
                # participant
                worksheet.write(row, 2, "T")
                ee = prt.extras
                if ee:
                    e = ee[0] # type: Extra
                    pay_now, pay_to_hotel, items = extras_cost(e)
                    worksheet.write(row, 3, e.arrival_date, df)
                    worksheet.write(row, 4, e.departure_date, df)
                    worksheet.write(row, 5, pay_to_hotel, money)
                else:
                    # no extras
                    worksheet.write(row, 3, start_date, df)
                    worksheet.write(row, 4, end_date, df)
                    worksheet.write(row, 5, 0, money)

            else:
                # guest
                e = prt.extras[0] # type: Extra
                arrival, departure = (e.guest1_arrival, e.guest1_departure) if ra.guest_position == 1 else (e.guest2_arrival, e.guest2_departure)
                worksheet.write(row, 2, "Gast von %s" % prt.fullname())
                worksheet.write(row, 3, arrival, df)
                worksheet.write(row, 4, departure, df)

            nr += 1
            row += 1

        row += 1 # empty row after each room

    workbook.close()

    output.seek(0)

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')



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

            tooltip = rt.tooltip(ee, prt_dict)
            roompartner_code = rt.roompartner_code(ee) # type: str
            guest_id = make_guest_key(ra)

            entries.append(
                '"%s": {"id": "%s", "name": "%s", "arrival": "%s", "departure": "%s", "roomsize": %d, "tooltip": "%s", "extras_submitted": true, "room": "%s", "partner": "%s", "guest_of": "%d"}' % \
                (guest_id, guest_id, ra.name, df_arrival, df_departure, rt.people_in_room, tooltip, ra.room, roompartner_code, prt.id))


    return ",\n".join(entries)

