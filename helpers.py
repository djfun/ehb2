from jinja2 import evalcontextfilter

from __init__ import *
from tables import *

@app.template_filter()
@evalcontextfilter
def ft(eval_ctx, value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)

parts = ["--", "Tn", "Ld", "Br", "Bs"]
lparts = ["None", "Tenor", "Lead", "Baritone", "Bass"]

@app.template_filter()
@evalcontextfilter
def part(eval_ctx, value):
    return parts[value]



countries = {country.id: country for country in session.query(Country).all()}