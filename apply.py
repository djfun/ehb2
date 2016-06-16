import datetime

from __init__ import *
from tables import *
from itertools import groupby
from helpers import *
from flask import request
from wtforms import *

@app.route("/apply.html", methods=["GET",])
def apply(message=None):
    data = {"email": "hallo@gmail.com"}
    errors = set()

    return render_template("apply.html", title="Apply!", data=data, errors=errors,
                           countries=country_list)


@app.route("/payment.html", methods=["POST",])
def do_payment(message=None):
    pass