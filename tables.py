# coding: utf-8
from sqlalchemy import Column, DateTime, Float, Integer, SmallInteger, String, Table, text, ForeignKey, Unicode, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import Text, UnicodeText

Base = declarative_base()
metadata = Base.metadata


class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    code = Column(String(2))
    name_en = Column(String(100))
    name_fr = Column(String(100))


class Geocoding(Base):
    __tablename__ = 'geocoding'

    id = Column(Integer, primary_key=True)
    city = Column(String(100), nullable=False, index=True, server_default=text("''"))
    lat = Column(Float(asdecimal=True))
    long = Column(Float(asdecimal=True))

    def __init__(self, city, lat, long):
        self.city = city
        self.lat = lat
        self.long = long

    def __repr__(self):
        return "%s (%f, %f)" % (self.city, self.lat, self.long)


class GuestQuartet(Base):
    __tablename__ = 'guest_quartet'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    city = Column(String(100))
    country = Column("country", String(2), ForeignKey('countries.code'))
    final_part = Column(SmallInteger, ForeignKey('parts.id'))
    iq_username = Column(String(100))

    def fullname(self):
        return "%s %s" % (self.firstname, self.lastname)


class Participant(Base):
    __tablename__ = 'participant'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    sex = Column(String(10))
    street = Column(String(100))
    city = Column(String(100))
    zip = Column(String(20))
    country = Column("country", String(2), ForeignKey('countries.code'))
    final_part = Column(SmallInteger, ForeignKey('parts.id'))
    part1 = Column(SmallInteger)
    part2 = Column(SmallInteger)
    member = Column(Boolean)
    paypal_token = Column(String(30), index=True)
    last_paypal_status = Column("last_paypal_status", SmallInteger,
                                ForeignKey("paypal_statuses.id"))
    email = Column(String(100), unique=True)
    exp_quartet = Column(String)
    exp_brigade = Column(String)
    exp_chorus = Column(String)
    exp_musical = Column(String)
    exp_reference = Column(String)
    application_time = Column(DateTime)
    contribution_comment = Column(String)
    comments = Column(String)
    registration_status = Column(SmallInteger)
    donation = Column(Integer)
    discounted = Column(String(8))
    final_fee = Column(Integer)
    confirmed = Column(Boolean)
    gdpr = Column(Boolean)

    iq_username = Column(String(100))
    code = Column(String(16))

    s_final_part = relationship("Part", backref=backref("participants"), lazy="joined")
    ccountry = relationship("Country", backref=backref("participants"), lazy="joined")
    paypal_status = relationship("PaypalStatus", backref=backref("participants"), lazy="joined")

    def city_with_country(self):
        return "%s, %s" % (self.city, self.country)

    def makeMapLabel(self):
        line1 = "%s %s (%s / %s)" % (self.firstname, self.lastname,
                                     self.shortsex(), self.s_final_part)
        line2 = "<a href=\'mailto:%s\'>%s</a>" % (self.email, self.email)
        return '"%s<br/>%s"' % (line1, line2)

    def shortsex(self):
        return self.sex[0].upper()

    def shortpart(self):
        return self.s_final_part.short()

    def fullname(self):
        return "%s %s" % (self.firstname, self.lastname)

    def fullnameLF(self):
        return "%s, %s" % (self.lastname, self.firstname)

    def paypalStatus(self):
        return "xx"

    def __repr__(self):
        return "%s %s (%d)" % (self.firstname, self.lastname, self.id)


class DeletedParticipant(Base):
    __tablename__ = 'deleted_participants'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100))
    lastname = Column(String(100))
    sex = Column(String(10))
    street = Column(String(100))
    city = Column(String(100))
    zip = Column(String(20))
    country = Column("country", String(2), ForeignKey('countries.code'))
    final_part = Column(SmallInteger, ForeignKey('parts.id'))
    part1 = Column(SmallInteger)
    part2 = Column(SmallInteger)
    member = Column(Boolean)
    paypal_token = Column(String(30), index=True)
    last_paypal_status = Column("last_paypal_status", SmallInteger,
                                ForeignKey("paypal_statuses.id"))
    email = Column(String(100), unique=True)
    exp_quartet = Column(String)
    exp_brigade = Column(String)
    exp_chorus = Column(String)
    exp_musical = Column(String)
    exp_reference = Column(String)
    application_time = Column(DateTime)
    contribution_comment = Column(String)
    comments = Column(String)
    registration_status = Column(SmallInteger)
    donation = Column(Integer)
    member = Column(Boolean)
    discounted = Column(String(8))
    final_fee = Column(Integer)
    iq_username = Column(String(100))
    code = Column(String(16))
    deletion_time = Column(DateTime)


class Part(Base):
    __tablename__ = 'parts'
    shortparts = ["--", "Tn", "Ld", "Br", "Bs"]

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(10))

    def short(self):
        return self.shortparts[self.id]

    def __repr__(self):
        return self.name


class PaypalHistory(Base):
    __tablename__ = 'paypal_history'

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer)
    timestamp = Column(DateTime)
    _paypal_status = Column("paypal_status", Integer, ForeignKey("paypal_statuses.id"))
    data = Column(String)
    payment_step = Column(SmallInteger, nullable=False, server_default=text("'1'"))

    paypal_status = relationship("PaypalStatus", backref=backref("history_items"), lazy="joined")


paypal_shortnames = ["", "uninit", "token", "callback",
                     "approved", "paid", "cancelled", "error", "oops"]


class PaypalStatus(Base):
    __tablename__ = 'paypal_statuses'

    id = Column(Integer, primary_key=True)
    paypal_status_name = Column(String(20))

    def shortname(self):
        return paypal_shortnames[self.id]

    def __repr__(self):
        return "%d-%s" % (self.id, self.paypal_status_name)

    def clone(self): # ugly hack around the lazy loading issue
        ret = PaypalStatus()
        ret.id = int(self.id)
        ret.paypal_status_name = str(self.paypal_status_name)
        return ret


class RegistrationStatus(Base):
    __tablename__ = 'registration_statuses'

    id = Column(Integer, primary_key=True)
    registration_status = Column(String(100))


class Sex(Base):
    __tablename__ = 'sexes'

    id = Column(Integer, primary_key=True)
    name = Column(String(10))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    password = Column(String(100))


class Extra(Base):
    __tablename__ = 'extras'

    uid = Column(Integer, primary_key=True)
    id = Column(Integer, ForeignKey('participant.id'), nullable=False)
    roomtype = Column(String(100), nullable=False)
    roompartner = Column(Integer)
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)
    num_show_tickets_regular = Column(SmallInteger, nullable=False)
    num_show_tickets_discount = Column(SmallInteger, nullable=False)
    t_shirt_sex = Column(String(1), nullable=False)
    t_shirt_size = Column(String(5))
    other = Column(String(1000), nullable=False, server_default=text("''"))
    guest = Column(String(1000), nullable=False, server_default=text("''"))
    num_after_concert = Column(SmallInteger, nullable=False)
    num_lunch_saturday = Column(SmallInteger, nullable=False)
    num_dinner_friday = Column(SmallInteger, nullable=False)
    guest1_name = Column(String(200))
    guest1_arrival = Column(Date)
    guest1_departure = Column(Date)
    guest1_roomtype = Column(String(100))
    guest2_name = Column(String(200))
    guest2_arrival = Column(Date)
    guest2_departure = Column(Date)
    guest2_roomtype = Column(String(100))
    last_paypal_status = Column(SmallInteger)
    sat_night_restaurant = Column(String(100))
    sat_night_numpeople = Column(SmallInteger)
    phone = Column(String(100))
    paypal_token = Column(String(30))
    special_event_tickets = Column(SmallInteger, nullable=False)
    t_shirt_spec = Column(SmallInteger, ForeignKey('t_shirt_specs.id'))

    participant = relationship("Participant", backref=backref("extras"), lazy="joined")
    ts_spec = relationship("TShirtSpec", backref=backref("extras"), lazy="joined")


class TShirtSpec(Base):
    __tablename__ = 't_shirt_specs'

    id = Column(SmallInteger, primary_key=True)
    color = Column(String(100), nullable=False)


class OverwrittenExtra(Base):
    __tablename__ = 'overwritten_extras'

    uid = Column(Integer, primary_key=True)
    id = Column(Integer, ForeignKey('participant.id'), nullable=False)
    roomtype = Column(String(100), nullable=False)
    roompartner = Column(Integer)
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)
    num_show_tickets_regular = Column(SmallInteger, nullable=False)
    num_show_tickets_discount = Column(SmallInteger, nullable=False)
    t_shirt_sex = Column(String(1), nullable=False)
    t_shirt_size = Column(String(5))
    other = Column(String(1000), nullable=False, server_default=text("''"))
    guest = Column(String(1000), nullable=False, server_default=text("''"))
    num_after_concert = Column(SmallInteger, nullable=False)
    num_lunch_saturday = Column(SmallInteger, nullable=False)
    num_dinner_friday = Column(SmallInteger, nullable=False)
    guest1_name = Column(String(200))
    guest1_arrival = Column(Date)
    guest1_departure = Column(Date)
    guest1_roomtype = Column(String(100))
    guest2_name = Column(String(200))
    guest2_arrival = Column(Date)
    guest2_departure = Column(Date)
    guest2_roomtype = Column(String(100))
    last_paypal_status = Column(SmallInteger)
    sat_night_restaurant = Column(String(100))
    sat_night_numpeople = Column(SmallInteger)
    phone = Column(String(100))
    paypal_token = Column(String(30))
    special_event_tickets = Column(SmallInteger, nullable=False)
    t_shirt_spec = Column(SmallInteger)

    timestamp = Column(DateTime)

    participant = relationship("Participant", backref=backref("overwritten_extras"), lazy="joined")


class RoomAssignment(Base):
    __tablename__ = 'room_assignments'

    uid = Column(Integer, primary_key=True)
    name = Column(String(100))
    id = Column(Integer)
    guest_position = Column(SmallInteger)
    room = Column(String(10))

    def __repr__(self):
        return "[%d %s, guestpos=%d, room=%s]" % (self.id, self.name, self.guest_position, self.room)


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    recipient = Column(Integer, ForeignKey('participant.id'))
    subject = Column(String(200))
    body = Column(UnicodeText)
    replyto = Column(String(200))
    sent_from = Column(String(500))

    participant = relationship("Participant", backref=backref("emails"), lazy="joined")


class OopsCode(Base):
    __tablename__ = "oops_code"

    id = Column(Integer, ForeignKey('participant.id'), primary_key=True)
    code = Column(String(16))

    participant = relationship("Participant", backref=backref("oops_code"), lazy="joined")
