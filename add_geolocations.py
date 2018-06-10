__author__ = 'koller'

from __init__ import Base, engine
from tables import Participant, Geocoding
from geopy.geocoders import Nominatim
from sqlalchemy.orm import sessionmaker
from add_geolocations import *

# import chardet

# engine = create_engine(config.db_url)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# set up geolocation service
geolocator = Nominatim()


# unknown cities
known = set([geo.city.lower() for geo in session.query(Geocoding)])
all = set([p.city_with_country().lower() for p in session.query(Participant)])
unknown = all - known

print (unknown)

for city in unknown:
    # print "%s is %s" % (city, chardet.detect(city))
    # c = city.decode("iso-8859-2")  # again, for whatever reason (see generate_map)
    c = city
    loc = geolocator.geocode(c)

    if loc:
        g = Geocoding(c, loc.latitude, loc.longitude)
        session.add(g)
        print ("Added: %s -> %s" % (c, loc.raw))
    else:
        print ("*** not found: %s" % c)

session.commit()
