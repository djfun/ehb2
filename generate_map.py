from __future__ import print_function
from jinja2.loaders import FileSystemLoader
import sys

from __init__ import Base, engine
from tables import Participant, Geocoding
from sqlalchemy.orm import sessionmaker
from random import random
from jinja2 import Environment

# set up database connection
# engine = create_engine('mysql+pymysql://root@localhost/ehb2016')
# engine = create_engine(config.db_url)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# set up Jinja
loader = FileSystemLoader("templates")
env = Environment(loader=loader)
template = env.get_template("googlemap.html")


latlng = list()
names = list()
parts = list()


for p in session.query(Participant):
    loc = session.query(Geocoding).filter(Geocoding.city == p.city_with_country()).first()
    if loc:
        latlng.append("new google.maps.LatLng(%f, %f)" % (float(loc.lat) +
                                                          (random() - 0.5) * 0.1, float(loc.long) + (random() - 0.5) * 0.1))
        names.append(p.makeMapLabel())
        parts.append(str(p.final_part))
    else:
        print("Warning: unknown location for %s %s (%d)" %
              (p.firstname, p.lastname, p.id), file=sys.stderr)


ll = u", ".join(latlng)
nn = u", ".join(names)
pp = u", ".join(parts)


# template is rendered with UTF-8, web page needs to reflect that
# mapcontent = template.render(latlongs=ll, names=nn, parts=pp)
