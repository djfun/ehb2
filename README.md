# EHB Website Server

This is the source code for the application page for the European Harmony Brigade (EHB). It was developed by Alexander Koller for EHB 2015 and 2016, and rewritten from scratch in Python for EHB 2017. It provides the following functionality for the EHB registration process:

* Participants can submit an application, and later book extras, and pay for both via Paypal.
* Organizers can display and edit the applications.
* Organizers can assign participants to rooms with a drag-and-drop room planner.
* Organizers can generate printable materials, such as name badges and dance cards.


## Requirements

The EHB server requires
[Python 3](https://www.python.org/download/releases/3.0/). You will
also need a working installation of an SQL database that is
[supported by SQLAlchemy](http://docs.sqlalchemy.org/en/latest/dialects/index.html),
such as [MySQL](https://www.mysql.com/).

Make sure you have the following Python packages installed (replacing
`pymysql` by the Python library for your database engine, if you use a
database engine other than MySQL):

```
pip install pymysql Flask sqlalchemy Flask-SQLAlchemy-Session wtforms paypalrestsdk XlsxWriter openpyxl tornado flask_login numpy
```

If you want to generate printable materials, such as name badges, you
will also need a reasonably recent and complete installation of
[LaTeX](https://www.tug.org/texlive/).


## Configuration files

The configuration for the EHB server is split over two files.

* ehb-public.conf contains all the information which can safely be
  shared with the public, such as the event name, room prices, song
  list, and so on. This file is part of this public repository, and
  will be a (read-only) part of the Docker image.
* Sensitive information, such as the details of the database
  connection, email passwords, and so on, should _not_ be kept in
  ehb-public.conf. You can either write this information into a file
  ehb-private.conf, which you do _not_ put under version control. If
  this file exists, the EHB server will read the information from
  there. Alternatively, you can set these options through environment
  variables, which are documented below. This is the most convenient
  choice for injecting them into a Docker container.

### Private options

Here is a list of private options, together with their corresponding
environment variables.

| Environment variable | Section  | Key                    |
-----------------------|----------|-------------------------
| SERVER_SECRET        | server   | secret                 |
| SERVER_PORT          | server   | port                   |
| SERVER_BASEURL       | server   | base_url               |
| SERVER_TORNADO       | server   | use_tornado            |
| SERVER_LOGFILE       | server   | logfile                |
| DB_URL               | database | url                    |
| EMAIL_SERVER         | email    | server                 |
| EMAIL_SENDER         | email    | sender                 |
| EMAIL_NAME           | email    | name                   |
| EMAIL_PASSWORD       | email    | password               |
| EMAIL_DELAY          | email    | delay_between_messages |
| PAYPAL_MODE          | paypal   | mode                   |
| PAYPAL_CLIENT_ID     | paypal   | client_id              |
| PAYPAL_CLIENT_SECRET | paypal   | client_secret          |

Furthermore, use environment variables of the following form to define
the users who can login to the system:

```
EHB_USER_1: "organizers, EHB Organizers, orgapassword"
```

## Running as a Docker container

The EHB apply server can be run in a Docker container. An up-to-date
image should always be available
[on Docker Hub](https://hub.docker.com/r/akoller/ehb2). This makes it
unnecessary to install Python or any of the requisite libraries
spelled out above; all these pieces are automatically part of the
Docker image.

During development, you can also use `docker build -t ehb2 .` in the main ehb2 directory to rebuild and test the Docker image before pushing to Github. When you do push to Github, the Docker image on Docker Hub will be automatically rebuilt.

The EHB container needs to connect to a container providing a MySQL
database over a (possibly Docker-internal) network. The simplest way
to start both the MySQL container and the EHB server together is
through [Docker Compose](https://docs.docker.com/compose/), using the
`docker-compose.yml` file in this repository. You should take care to
choose your own database root password, as well as the MySQL data
directory on your local machine (in services/mysql/volumes).

In order for the EHB server to function correctly, you will also need
to supply values for the private configuration options (see
above). The easiest way to do that is in a second docker-compose
file - let's call it `docker-compose-private.yml`. This file is not
part of this repository; it should look as follows:

```
version: '2'
 
services:
  ehb2:
    environment:
      SERVER_SECRET: "blabla"
      SERVER_PORT: "5000"
	  ... and so on for the other variables ...
```

You can start the EHB server from within Docker with the
following command:

```
docker-compose -f docker-compose.yml -f docker-compose-private.yml up
```

You can then access the EHB server on port 5000 on your local machine.



## Credits

This code uses
[Thunk](http://www.freesound.org/people/Reitanna/sounds/323725/) by
Reitanna,
[Powerup/Success](http://www.freesound.org/people/GabrielAraujo/sounds/242501/)
by GabrielAraujo, and
[Postit Remove](https://www.freesound.org/people/Ignitor/sounds/182575/)
by Ignitor, all from [Freesound](http://www.freesound.org) under a Creative Commons licence.


