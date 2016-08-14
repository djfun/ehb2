from jinja2 import evalcontextfilter, Markup

from __init__ import *
from config import conf
from tables import *

@app.template_filter()
@evalcontextfilter
def ft(eval_ctx, value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)

# lookup participant
def lp(id):
    return session.query(Participant).filter(Participant.id==id).first()


# some useful global variables
parts = ["--", "Tn", "Ld", "Br", "Bs"]
lparts = ["None", "Tenor", "Lead", "Baritone", "Bass"]
countries = {country.id: country for country in session.query(Country).all()}
country_list = [(c.code, c.name_en) for id, c in sorted(countries.items(), key=lambda x:x[0])]
paypal_statuses = { pp.id : pp for pp in session.query(PaypalStatus).all() }

PP_UNINITIALIZED = 1
PP_TOKEN = 2
PP_CALLBACK = 3
PP_DETAILS = 4
PP_SUCCESS = 5
PP_CANCELLED = 6
PP_ERROR = 7


# base URL from ehb.conf, with or without trailing slash
def base_url(with_slash=False):
    without = conf.get("server", "base_url").rstrip("/")

    if with_slash:
        return without + "/"
    else:
        return without


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
def paypal_status_color(eval_ctx, item):
    if item._paypal_status == PP_SUCCESS:
        return "lightgreen"
    elif item._paypal_status == PP_CANCELLED or item._paypal_status == PP_ERROR:
        return "Pink"
    else:
        return "white"


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

