
import os
from flask import send_from_directory
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from __init__ import *
from helpers import *
from auth import *
from show_participants import show_participants, show_participant, do_show_participants
from apply import *


@app.route("/")
def index():
    return apply()

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


#######################################################################################
## main
#######################################################################################

if __name__ == "__main__":
    port = int(conf.get("server", "port"))

    if conf.getboolean("server", "use_tornado"):
        # use Tornado web server to host Flask app

        print("Starting Tornado webserver on port %d." % port)

        all = logging.FileHandler('./tornado.log')
        access = logging.FileHandler("./tornado-access.log")

        logging.getLogger("tornado.access").addHandler(access)
        logging.getLogger("tornado.access").setLevel(logging.DEBUG)

        logging.getLogger("tornado.application").addHandler(all)
        logging.getLogger("tornado.general").addHandler(all)
        logging.getLogger("tornado.application").setLevel(logging.DEBUG)
        logging.getLogger("tornado.general").setLevel(logging.DEBUG)

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(port)
        IOLoop.instance().start()

    else:
        print("Starting builtin Flask webserver on port %d." % port)
        app.run(debug=True, host="0.0.0.0", port=port)





