from collections import OrderedDict
from __init__ import *
from config import conf, number_of_days
from tables import Participant, Extra

NO_ROOMPARTNER = "-1"
NO_GUEST = "no_guest" # roomtype for "no guest"; this is used when validating the form


roomcost_single = int(conf["extras: room costs"]["1"])
roomcost_double = int(conf["extras: room costs"]["2"])
extra_cost_for_single = number_of_days*(roomcost_single-roomcost_double)

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


#
#
# def fc_double_anyone(prt_roompartner, guest_roomtypes):
#     if prt_roompartner != NO_ROOMPARTNER:
#         return "If you are willing to share with any other participant, please choose '-- no selection --' under 'Share room with' below."
#
#     return None
#
# def fc_single_prt(prt_roompartner, guest_roomtypes):
#     if prt_roompartner != NO_ROOMPARTNER:
#         return "If you would like to book a single room, please choose '-- no selection --' under 'Share room with' below."
#
#     return None
#
#
# def fc_double_participant(prt_roompartner, guest_roomtypes):
#     if prt_roompartner == NO_ROOMPARTNER:
#         return "If you would like to share your room with a specific participant, please choose that participant under 'Share room with' below."
#
#     return None
#
# def fc_double_with_my_guest(prt_roompartner, guest_roomtypes):
#     if prt_roompartner != NO_ROOMPARTNER:
#         return "If you would like to share your room with a guest, please choose '-- no selection --' under 'Share room with' below."
#
#     has_guest_with_me = any([grt == "double_with_me" for grt in guest_roomtypes])
#     if not has_guest_with_me:
#         return "If you would like to share your room with a guest, please specify at least one guest who shares the room with you below."
#
#     return None
#
# def fc_double_with_other_guest(prt_roompartner, other_guest_roomtype):
#     if other_guest_roomtype != "double_with_other_guest":
#         return "If this guest should share their room with the other guest, please specify 'share with other guest' for the other guest as well."
#
#     return None
#
#
# def fc_double_with_me(prt_roomtype, other_guest_roomtype):
#     if other_guest_roomtype == "double_with_me":
#         return "Only one guest can share your double room with you."
#
#     if prt_roomtype != "double_with_my_guest":
#         return "If this guest should share their double room with you, please specify 'share with my guest' for your own room type."
#
#     return None




class Roomtype:
    def __init__(self, id, description, people_in_room, for_participants, for_guests, constraint):
        self.id = id
        self.description = description
        self.for_participants = for_participants
        self.for_guests = for_guests
        self.people_in_room = people_in_room
        self.constraint = constraint

        if self.people_in_room == 1:
            self.detailed_description = "%s (+ %d EUR)" % (self.description, extra_cost_for_single)
        else:
            self.detailed_description = self.description

    def cost_on_ehb_days(self):
        if self.people_in_room == 1:
            return roomcost_single-roomcost_double
        else:
            return 0

    def cost_on_other_days(self):
        if self.people_in_room == 1:
            return roomcost_single
        elif self.people_in_room == 2:
            return roomcost_double
        else:
            return 0

    def description_with_roompartner(self, partner_id):
        if self.id == "double_participant":
            partner = session.query(Participant).filter(Participant.id==partner_id).first()
            return "Double room, shared with %s" % partner.fullname()
        else:
            return self.description

    def __str__(self):
        return "{rt %s, '%s', part:%s, guests:%s, people:%d, cstr:%s}" % (self.id, self.description, self.for_participants, self.for_guests, self.people_in_room, self.constraint)

    def __repr__(self):
        return self.__str__()



# define room types for participants

# roomtypes["double_anyone"]           = Roomtype("double_anyone",            "Double room, would share with anyone", 2, True, False, "ANYONE", fc_double_anyone)
# roomtypes["single_prt"]              = Roomtype("single_prt",               "Single room", 1, True, False, "ANYONE", fc_single_prt)
# roomtypes["double_participant"]      = Roomtype("double_participant",       "Double room, share with specific participant", 2, True, False, "WITH_PARTICIPANT", fc_double_participant)
# roomtypes["double_with_my_guest"]    = Roomtype("double_with_my_guest",     "Double room, share with my guest", 2, True, False, "WITH_GUEST", fc_double_with_my_guest)
#
# # room types for guests
# roomtypes["no_guest"]                = Roomtype("no_guest",                 "No guest", 0, False, True, "ANYONE", None)
# roomtypes["double_anyone_guest"]     = Roomtype("double_anyone_guest",      "Double room, would share with anyone", 2, False, True, "ANYONE", None)
# roomtypes["single_guest"]            = Roomtype("single_guest",             "Single room", 1, False, True, "ANYONE", None)
# roomtypes["double_with_me"]          = Roomtype("double_with_me",           "Double room, share with me", 2, False, True, "WITH_ME", fc_double_with_me)
# roomtypes["double_with_other_guest"] = Roomtype("double_with_other_guest",  "Double room, share with other guest", 2, False, True, "WITH_GUEST", fc_double_with_other_guest)
#




# Functions for validating the form, given the different participant roomtypes.
# For each roomtype that can be selected for the participant, define a function here
# that returns a string that evaluates to true if a validation error occurred.

# Validation of participant roomtypes. The functions are passed two arguments: prt_roompartner is the value of the
# "Share room with" field of the form; guest_roomtypes is a list of values of the
# "Guest 1/2: room type" fields of the form.

# Validation of guest roomtypes. The functions are passed two arguments:
# prt_roomtype is the roomtype of the participant, an other_guest_roomtype
# is the roomtype of the other guest.

# room types for participants

class DoubleAnyoneRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_anyone", "Double room, would share with anyone", 2, True, False, "ANYONE")

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner != NO_ROOMPARTNER:
            return "If you are willing to share with any other participant, please choose '-- no selection --' under 'Share room with' below."

        return None

    @staticmethod
    def tooltip(extras:Extra, prt_dict):
        return "share with anyone"

class SingleRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "single_prt", "Single room", 1, True, False, "ANYONE")

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner != NO_ROOMPARTNER:
            return "If you would like to book a single room, please choose '-- no selection --' under 'Share room with' below."

        return None

    @staticmethod
    def tooltip(extras:Extra, prt_dict):
        return None


class DoubleParticipantRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_participant", "Double room, share with specific participant", 2, True, False, "WITH_PARTICIPANT")

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner == NO_ROOMPARTNER:
            return "If you would like to share your room with a specific participant, please choose that participant under 'Share room with' below."

        return None

    @staticmethod
    def tooltip(extras:Extra, prt_dict):
        partner = prt_dict[extras.roompartner] # type: Participant
        return "share with " + partner.fullname()


class DoubleWithGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_with_my_guest", "Double room, share with my guest", 2, True, False, "WITH_GUEST")

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner != NO_ROOMPARTNER:
            return "If you would like to share your room with a guest, please choose '-- no selection --' under 'Share room with' below."

        has_guest_with_me = any([grt == "double_with_me" for grt in guest_roomtypes])
        if not has_guest_with_me:
            return "If you would like to share your room with a guest, please specify at least one guest who shares the room with you below."

        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        return "share with guest"


# room types for guests

class NoGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "no_guest", "No guest", 0, False, True, "ANYONE")

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        return None


class DoubleAnyoneGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_anyone_guest", "Double room, would share with anyone", 0, False, True, "ANYONE")

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) share with anyone" % prt.fullname()

class SingleGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "single_guest", "Single room", 1, False, True, "ANYONE")

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) single" % prt.fullname()

class DoubleWithMeRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_with_me", "Double room, share with me", 2, False, True, "WITH_ME")

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        if other_guest_roomtype == "double_with_me":
            return "Only one guest can share your double room with you."

        if prt_roomtype != "double_with_my_guest":
            return "If this guest should share their double room with you, please specify 'share with my guest' for your own room type."

        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) share with participant" % prt.fullname()


class DoubleWithOtherGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_with_other_guest", "Double room, share with other guest", 2, False, True, "WITH_GUEST")

    @staticmethod
    def form_constraint(prt_roompartner, other_guest_roomtype):
        if other_guest_roomtype != "double_with_other_guest":
            return "If this guest should share their room with the other guest, please specify 'share with other guest' for the other guest as well."

        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) share with other guest" % prt.fullname()



roomtypes = OrderedDict()

for rt in [DoubleAnyoneRoomtype(), SingleRoomtype(), DoubleParticipantRoomtype(), DoubleWithGuestRoomtype(), NoGuestRoomtype(), DoubleAnyoneGuestRoomtype(), SingleGuestRoomtype(), DoubleWithMeRoomtype(), DoubleWithOtherGuestRoomtype()]:
    roomtypes[rt.id] = rt