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

*These requirements will be automatically installed if you are using a Docker container (see below).*

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
| SERVER_PASSWORD_SALT | server   | secret                 |
| ACCEPT_APPLICATIONS  | application | accept_applications |
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

### Initializing the database

The EHB system keeps its data in a MySQL database, which is stored in a subdirectory `mysql_data` below your main `ehb2` directory. This subdirectory is created automatically when you first start the Docker containers as described above, and initially contains a fresh MySQL data directory with no databases. The initial root password is as specified in `docker-compose.yml`.

After starting the Docker containers, you should navigate to the web interface of the phpMyAdmin container at [http://localhost:8080](http://localhost:8080) and log in as root with the initial root password. You can modify the database configuration there, including a new root password (don't forget to also change it in `docker-compose.yml` if you do this). You can also create or import a database with EHB participant data through this web interface.

Once you have created or imported a database, change the database URL in your `docker-compose-private.yml` and restart the Docker containers. After this point, you should be able to navigate to the [EHB2 admin page](http://localhost:5000/admin.html) and e.g. look at the current participants.

### Rebuilding the Docker image for development

If you make local changes to the EHB system (e.g. by editing the Python code) and restart the Docker containers, don't be surprised if your changes don't show up in your system. This is because the `docker-compose.yml` uses the Docker image [akoller/ehb2](https://hub.docker.com/r/akoller/ehb2/) from Docker Hub by default, which is built from the latest version on Github.

If you want to test your local changes, you need to rebuild this Docker image locally by running the following command in the main ehb2 directory:

```docker build -t akoller/ehb2 .```

This will then use your own local code the next time you start the Docker containers.

Once you push to Github, the Docker image on Docker Hub will be automatically rebuilt.





## Credits

This code uses
[Thunk](http://www.freesound.org/people/Reitanna/sounds/323725/) by
Reitanna,
[Powerup/Success](http://www.freesound.org/people/GabrielAraujo/sounds/242501/)
by GabrielAraujo, and
[Postit Remove](https://www.freesound.org/people/Ignitor/sounds/182575/)
by Ignitor, all from [Freesound](http://www.freesound.org) under a Creative Commons licence.
