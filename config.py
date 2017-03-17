__author__ = 'koller'

import configparser
from datetime import datetime


conf = configparser.RawConfigParser()
conf.optionxform = lambda option: option
# conf = configparser.ConfigParser({ }) # "password":""
conf.read("ehb.conf")

# start and end date of this event
start_date = datetime.strptime(conf["application"]["start_date"], "%Y-%m-%d").date()
end_date = datetime.strptime(conf["application"]["end_date"], "%Y-%m-%d").date()
number_of_days = (end_date-start_date).days  # number of days = number of nights

currency_symbol = conf.get("application", "currency_symbol")

