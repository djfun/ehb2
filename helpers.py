from logging import Logger

import flask
import jinja2
from jinja2 import evalcontextfilter, Markup

from __init__ import *
from config import conf
from tables import *


# global logger; value is set in main.py
log_file_name = conf["server"]["logfile"]
_logger = None  # type: Logger


def logger() -> Logger:
    return _logger

# lookup participant by ID


def lp(id):
    return session.query(Participant).filter(Participant.id == id).first()


# lookup participant by code
def lc(code):
    return session.query(Participant).filter(Participant.code == code).first()


# returns mapping from participant ids to participants
def id_to_participant_dict():
    all_prts = session.query(Participant).all()
    return {prt.id: prt for prt in all_prts}


# show message on the message.html template
def show_message(message):
    return render_template("message.html", message=message)


# lookup partcipant by oops code - DEPRECATED
def lookup_oops(oops_code):
    oops = session.query(OopsCode).filter(OopsCode.code == oops_code).first()
    return oops.participant


# some useful global variables
parts = ["--", "Tn", "Ld", "Br", "Bs"]
lparts = ["None", "Tenor", "Lead", "Baritone", "Bass"]
reg_statuses = ["--", "applied", "paid"]
countries = {country.code: country for country in session.query(Country)}
country_list = [(c.code, c.name_en) for id, c in sorted(countries.items(), key=lambda x:x[0])]

# base URL from ehb.conf, with or without trailing slash
def base_url(with_slash=False):
    without = conf.get("server", "base_url").rstrip("/")

    if with_slash:
        return without + "/"
    else:
        return without


class TableToShow:
    def __init__(self, header, content, title=None, summaryRow=None):
        self.header = header
        self.content = content
        self.title = title
        self.summaryRow = summaryRow


@app.template_filter()
@evalcontextfilter
def part(eval_ctx, value):
    return parts[value]


@app.template_filter()
@evalcontextfilter
def lpart(eval_ctx, value):
    return lparts[value]


@app.template_filter()
@evalcontextfilter
def order_status_color(eval_ctx, item):
    if item.status == OrderStatus.paid:
        return "lightgreen"
    else:
        return "white"


@app.template_filter()
@evalcontextfilter
def reg_status(eval_ctx, value):
    return reg_statuses[value]


@app.template_filter()
@evalcontextfilter
def mbr(eval_ctx, value):
    if value == True:
        return "Yes"
    else:
        return "No"



@app.template_filter()
@evalcontextfilter
def tf(label, eval_ctx, name):
    # print(eval_ctx)
    # print(label)
    # print(name)
    return Markup("<input id='%s' name='%s' type='text' placeholder='%s' class='input-xlarge' />" % (name, name, label))


@app.template_filter()
@evalcontextfilter
def gitrev(eval_ctx, value):
    return git_revision.strip().decode("UTF-8")


@app.template_filter()
@evalcontextfilter
def ehbrev(eval_ctx, value):
    return conf.get("application", "name")

# format time


@app.template_filter()
@evalcontextfilter
def ft(eval_ctx, value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)


# format date
@app.template_filter()
@evalcontextfilter
def fd(eval_ctx, value, format='%Y-%m-%d'):
    return value.strftime(format)


# convert all newlines (\n) to HTML <br/>
@app.template_filter()
@evalcontextfilter
def nlbr(eval_ctx, value, format='%Y-%m-%d'):
    return value.replace("\n", "<br/>\n")


http_types = set(["GET", "POST"])
ignored_prefixes = ["Request[", "Response[", "PayPal-Request-Id:", " * "]

# convert all newlines (\n) to HTML <br/>


@app.template_filter()
@evalcontextfilter
def format_log_message(eval_ctx, message, level='INFO'):
    if level == 'ERROR':
        return Markup("<font color='red'>%s</font>" % message)
    elif "started at" in message:
        return Markup("<strong>%s</strong>" % message)
    else:
        return Markup("<font color='gray'>%s</font>" % message)

    # parts = message.split()
    # if len(parts) >= 3 and parts[1] in http_types:
    #     return Markup("<font color='gray'>%s</font>" % message)
    # elif any(message.startswith(prefix) for prefix in ignored_prefixes):
    #     return Markup("<font color='gray'>%s</font>" % message)
    # elif "started at" in message:
    #     return Markup("<strong>%s</strong>" % message)
    # else:
    #     return Markup("<font color='red'>%s</font>" % message)
