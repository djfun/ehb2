
import os

import sys

import tornado
from flask import send_from_directory
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from __init__ import *
from auth import *
from show_participants import show_participants, show_participant, do_show_participants
from apply import *
from extras import *
from extras_roomplanner import *
from admin import *
from helpers import logger

@app.route("/")
def index():
    if conf.getboolean("application", "accept_applications"):
        return apply()
    else:
        return "The application site is not available right now - please check back later!"

@app.route("/secret")
def secret():
    return apply()

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


#######################################################################################
## main
#######################################################################################


if __name__ == "__main__":
    port = int(conf.get("server", "port"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file_name, 'a', 'utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # logging.basicConfig(level=logging.INFO, filename=log_file_name, format='%(asctime)s %(message)s')

    if conf.getboolean("server", "use_tornado"):
        # use Tornado web server to host Flask app

        # The above configuration of the logging system sends all messages
        # to ehb2.log, including the entire Tornado access log. In theory,
        # one should be able to send the access log to a separate file from
        # everything else, but for some reason logging to application and
        # general seem to be ignored in this case. So I'm going the
        # basicConfig route for now.

        # formatter = logging.Formatter(fmt='%(asctime)s %(message)s')
        # ehb_handler = logging.FileHandler("./ehb2.log")
        # ehb_handler.setFormatter(formatter)
        # access_handler = logging.FileHandler("./tornado-access.log")
        # access_handler.setFormatter(formatter)
        #
        # logging.getLogger("tornado.application").addHandler(ehb_handler)
        # logging.getLogger("tornado.general").addHandler(ehb_handler)
        # logging.getLogger("tornado.access").addHandler(access_handler)

        print("Starting Tornado webserver on port %d." % port)
        helpers.logger = logging.getLogger("tornado.application")
        helpers.logger.info("Tornado started at %s" % str(start_time))

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(port)
        IOLoop.instance().start()

    else:
        helpers.logger = logging.getLogger(__name__)
        helpers.logger.info("Flask started at %s" % str(start_time))

        print("Starting builtin Flask webserver on port %d." % port)
        app.run(debug=True, host="0.0.0.0", port=port, threaded=True)






