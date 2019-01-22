import codecs

import sys

import os

__author__ = 'koller'

import configparser
from datetime import datetime
import re

conf = configparser.RawConfigParser()
conf.optionxform = lambda option: option
conf.read_file(codecs.open("ehb-public.conf", "r", "utf8"))


# add private values
if os.path.isfile("ehb-private.conf"):
    conf_private = configparser.RawConfigParser()
    conf_private.optionxform = lambda option: option
    conf_private.read_file(codecs.open("ehb-private.conf", "r", "utf8"))

    for section in conf_private.sections():
        if section not in conf.sections():
            conf.add_section(section)

        for key, value in conf_private.items(section):
            conf.set(section, key, value)

# add values from environment variables
env_to_conf_entries = [
    ("SERVER_SECRET", "server", "secret"),
    ("SERVER_PORT", "server", "port"),
    ("SERVER_BASEURL", "server", "base_url"),
    ("SERVER_TORNADO", "server", "use_tornado"),
    ("SERVER_LOGFILE", "server", "logfile"),
    ("SERVER_PASSWORD_SALT", "server", "password_salt"),
    #
    ("ACCEPT_APPLICATIONS", "application", "accept_applications"),
    #
    ("DB_URL", "database", "url"),
    #
    ("EMAIL_SERVER", "email", "server"),
    ("EMAIL_SENDER", "email", "sender"),
    ("EMAIL_NAME", "email", "name"),
    ("EMAIL_PASSWORD", "email", "password"),
    ("EMAIL_DELAY", "email", "delay_between_messages"),
    #
    ("PAYPAL_MODE", "paypal", "mode"),
    ("PAYPAL_CLIENT_ID", "paypal", "client_id"),
    ("PAYPAL_CLIENT_SECRET", "paypal", "client_secret")
]

for var, section, key in env_to_conf_entries:
    if var in os.environ:
        if section not in conf.sections():
            conf.add_section(section)
        conf.set(section, key, os.environ[var])

userid = 1
while ("EHB_USER_%d" % userid) in os.environ:
    if "users" not in conf.sections():
        conf.add_section("users")

    x = os.environ["EHB_USER_%d" % userid]
    username, longname, password = re.split(r"\s*,\s*", x)
    conf.set("users", username, "%s, %s" % (longname, password))
    userid += 1


# start and end date of this event
start_date = datetime.strptime(conf["application"]["start_date"], "%Y-%m-%d").date()
end_date = datetime.strptime(conf["application"]["end_date"], "%Y-%m-%d").date()
number_of_days = (end_date - start_date).days  # number of days = number of nights

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
