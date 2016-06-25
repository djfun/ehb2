__author__ = 'koller'

import configparser

# remote; also run ssh  koller@instantquartet.instantquartet.org -L 10000:localhost:3306 -N
#db_url = 'mysql+pymysql://root@127.0.0.1:10000/ehb2016'

# local
db_url = 'mysql+pymysql://root@localhost/ehb2016'


cp = configparser.ConfigParser({"password":""})
cp.read("ehb.conf")

pp_user = cp.get("paypal", "user")
pp_pwd = cp.get("paypal", "password")
pp_signature = cp.get("paypal", "signature")
pp_endpoint = cp.get("paypal", "endpoint") or "https://api-3t.sandbox.paypal.com/nvp"
pp_callback = cp.get("paypal", "callbackhost") or ""
pp_webscr = cp.get("paypal", "webscr") or ""

