import logging

import time

import helpers
from __init__ import app
from helpers import log_file_name, logger
import main


# set up logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_file_name, 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)
helpers._logger = logging.getLogger(__name__)

start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logger().info("Gunicorn started at %s" % str(start_time))

if __name__ == "__main__":
    app.run()
