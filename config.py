import codecs

__author__ = 'koller'

import configparser
from datetime import datetime
import re

conf = configparser.RawConfigParser()
conf.optionxform = lambda option: option
conf.read_file(codecs.open("ehb.conf", "r", "utf8"))

# start and end date of this event
start_date = datetime.strptime(conf["application"]["start_date"], "%Y-%m-%d").date()
end_date = datetime.strptime(conf["application"]["end_date"], "%Y-%m-%d").date()
number_of_days = (end_date-start_date).days  # number of days = number of nights

currency_symbol = conf.get("application", "currency_symbol")


# returns list of songs as (songid, name, key, start)
def read_songs():
    items = dict(conf.items('songs'))
    sorted_keys = sorted(items.keys(), key=int)

    ret = []
    for k in sorted_keys:
        parts = re.split("\s*\|\s*", items[k])
        key = parts[1].replace("->", "$\\rightarrow$").replace("#", "\\#")
        start = parts[2].replace("...", "\\ldots")
        ret.append((k, parts[0], key, start))

    return ret


