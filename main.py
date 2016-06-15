
import os
from flask import send_from_directory

from __init__ import *

from show_participants import *


@app.route("/")
def index():
    return "hallo"

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


#######################################################################################
## main
#######################################################################################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
