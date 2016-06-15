
import os
from flask import send_from_directory

from __init__ import *


@app.route("/")
def index():
    return "hallo"




#######################################################################################
## main
#######################################################################################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
