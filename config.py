__author__ = 'koller'

import configparser


conf = configparser.RawConfigParser()
conf.optionxform = lambda option: option
# conf = configparser.ConfigParser({ }) # "password":""
conf.read("ehb.conf")


