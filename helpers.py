from jinja2 import evalcontextfilter

from __init__ import *

@app.template_filter()
@evalcontextfilter
def ft(eval_ctx, value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)

_parts = ["--", "Tn", "Ld", "Br", "Bs"]

@app.template_filter()
@evalcontextfilter
def part(eval_ctx, value):
    return _parts[value]