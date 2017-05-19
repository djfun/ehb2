from __init__ import app

import main

if __name__ == "__main__":
    # port = int(main.conf.get("server", "port"))
    # print("Starting Gunicorn webserver on port %d." % port)

    app.run()