from collections import OrderedDict
from __init__ import *
from config import conf, number_of_days
from tables import Participant, Extra

NO_ROOMPARTNER = "-1"
NO_GUEST = "no_guest" # roomtype for "no guest"; this is used when validating the form


roomcost_single = float(conf["extras: room costs"]["1"])
roomcost_double = float(conf["extras: room costs"]["2"])
extra_cost_for_single_per_night = (roomcost_single-roomcost_double)
extra_cost_for_single = number_of_days*extra_cost_for_single_per_night



class Roomtype:
    def __init__(self, id, description, people_in_room, for_participants):
        self.id = id
        self.description = description
        self.for_participants = for_participants
        self.for_guests = not for_participants    # each room type is either for participants or for guests, never both
        self.people_in_room = people_in_room

        if self.people_in_room == 1:
            self.detailed_description = "%s (+ %.2f EUR / night)" % (self.description, extra_cost_for_single_per_night)
        else:
            self.detailed_description = self.description

    def cost_on_ehb_days(self):
        if self.people_in_room == 1:
            return extra_cost_for_single_per_night
        else:
            return 0

    def cost_on_other_days(self):
        if self.people_in_room == 1:
            return roomcost_single
        elif self.people_in_room == 2:
            return roomcost_double
        else:
            return 0

    # Returns description with the concrete room partner filled in (if applicable).
    # This is overridden in some subclasses.
    def description_with_roompartner(self, partner_id):
        return self.description

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        """Generates the tooltip string for the room planner, given an extras entry and a participant_id -> Participant dictionary.
        May return None to indicate no tooltip."""
        raise NotImplementedError("called unimplemented abstract method")

    @staticmethod
    def roompartner_code(extras: Extra):
        """Generates a roompartner code for the room planner. These codes are interpreted in the 'is_desired_partner' function
        of /static/room_planner_script.js, and are used to check the room assignments for validity. See the documentation there
        for the correct codes that should be returned here."""
        raise NotImplementedError("called unimplemented abstract method")


    # Each subclass will define a method "form_constraint" which is called to validate the extras form
    # (see extras_form.py). The method takes different arguments depending on whether the roomtype is for
    # a participant or for a guest. It should return a string that evaluates to true if a validation error occurred.
    # This string will then be displayed on the form as an error message. If everything is fine, return None.

    def __str__(self):
        return "{rt %s, '%s', part:%s, guests:%s, people:%d}" % (self.id, self.description, self.for_participants, self.for_guests, self.people_in_room)

    def __repr__(self):
        return self.__str__()




###############################################################################################################
#
# Room types for participants
#
# The "form_constraint" validation functions are passed two arguments: prt_roompartner is the value of the
# "Share room with" field of the form; guest_roomtypes is a list of values of the
# "Guest 1/2: room type" fields of the form.
#
###############################################################################################################


class DoubleAnyoneRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_anyone", "Double room, would share with anyone", 2, True)

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner != NO_ROOMPARTNER:
            return "If you are willing to share with any other participant, please choose '-- no selection --' under 'Share room with' below."

        return None

    @staticmethod
    def tooltip(extras:Extra, prt_dict):
        return "share with anyone"

    @staticmethod
    def roompartner_code(extras:Extra):
        return ""



class SingleRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "single_prt", "Single room", 1, True)

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner != NO_ROOMPARTNER:
            return "If you would like to book a single room, please choose '-- no selection --' under 'Share room with' below."

        return None

    @staticmethod
    def tooltip(extras:Extra, prt_dict):
        return ""

    @staticmethod
    def roompartner_code(extras:Extra):
        return ""



class DoubleParticipantRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_participant", "Double room, share with specific participant", 2, True)

    def description_with_roompartner(self, partner_id):
        partner = session.query(Participant).filter(Participant.id == partner_id).first()
        return "Double room, shared with %s" % partner.fullname()

    @staticmethod
    def form_constraint(prt_roompartner, guest_roomtypes):
        if prt_roompartner == NO_ROOMPARTNER:
            return "If you would like to share your room with a specific participant, please choose that participant under 'Share room with' below."

        return None

    @staticmethod
    def tooltip(extras:Extra, prt_dict):
        partner = prt_dict[extras.roompartner] # type: Participant
        return "share with " + partner.fullname()

    @staticmethod
    def roompartner_code(extras:Extra):
        return str(extras.roompartner)



class DoubleWithGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_with_my_guest", "Double room, share with my guest", 2, True)

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

    @staticmethod
    def roompartner_code(extras:Extra):
        return "-2" # share with guest





###############################################################################################################
#
# Room types for guests
#
# The "form_constraint" validation functionsare passed two arguments:
# prt_roomtype is the roomtype of the participant, and other_guest_roomtype
# is the roomtype of the other guest.
#
###############################################################################################################


class NoGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, NO_GUEST, "No guest", 0, False)

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        return ""

    @staticmethod
    def roompartner_code(extras:Extra):
        return ""



class DoubleAnyoneGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_anyone_guest", "Double room, would share with anyone", 2, False)

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) share with anyone" % prt.fullname()

    @staticmethod
    def roompartner_code(extras:Extra):
        return ""



class SingleGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "single_guest", "Single room", 1, False)

    @staticmethod
    def form_constraint(prt_roomtype, other_guest_roomtype):
        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) single" % prt.fullname()

    @staticmethod
    def roompartner_code(extras:Extra):
        return ""



class DoubleWithMeRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_with_me", "Double room, share with me", 2, False)

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

    @staticmethod
    def roompartner_code(extras:Extra):
        return "3"



class DoubleWithOtherGuestRoomtype(Roomtype):
    def __init__(self):
        Roomtype.__init__(self, "double_with_other_guest", "Double room, share with other guest", 2, False)

    @staticmethod
    def form_constraint(prt_roompartner, other_guest_roomtype):
        if other_guest_roomtype != "double_with_other_guest":
            return "If this guest should share their room with the other guest, please specify 'share with other guest' for the other guest as well."

        return None

    @staticmethod
    def tooltip(extras: Extra, prt_dict):
        prt = prt_dict[extras.id] # type: Participant
        return "(guest of %s) share with other guest" % prt.fullname()

    @staticmethod
    def roompartner_code(extras:Extra):
        return "4"





###############################################################################################################
#
# Collect all room types in a dictionary
#
###############################################################################################################

roomtypes = OrderedDict()

for rt in [DoubleAnyoneRoomtype(), SingleRoomtype(), DoubleParticipantRoomtype(), DoubleWithGuestRoomtype(), NoGuestRoomtype(), DoubleAnyoneGuestRoomtype(), SingleGuestRoomtype(), DoubleWithMeRoomtype(), DoubleWithOtherGuestRoomtype()]:
    roomtypes[rt.id] = rt