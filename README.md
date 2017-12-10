# EHB Website Server

This is the source code for the application page for the European Harmony Brigade (EHB). It was developed by Alexander Koller for EHB 2015 and 2016, and rewritten from scratch in Python for EHB 2017. It provides the following functionality for the EHB registration process:

* Participants can submit an application, and later book extras, and pay for both via Paypal.
* Organizers can display and edit the applications.
* Organizers can assign participants to rooms with a drag-and-drop room planner.

The software also includes a collection of Python scripts that will generate name badges, dance cards, etc. from the backend database.

## Requirements

The EHB server requires [Python 3](https://www.python.org/download/releases/3.0/). You will also need a working installation of an SQL database that is [supported by SQLAlchemy](http://docs.sqlalchemy.org/en/latest/dialects/index.html), such as [MySQL](https://www.mysql.com/).

Make sure you have the following Python packages installed (replacing the MySQL connector by the Python library for your database engine, if you use a database engine other than MySQL):

```
pip install pymysql
pip install Flask
pip install sqlalchemy
pip install Flask-SQLAlchemy-Session
pip install wtforms
pip install paypalrestsdk
pip install XlsxWriter
pip install openpyxl
```

## Configuration files

As of December 2017, the configuration for the EHB server is split
over two files.

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


## Credits

This code uses
[Thunk](http://www.freesound.org/people/Reitanna/sounds/323725/) by
Reitanna,
[Powerup/Success](http://www.freesound.org/people/GabrielAraujo/sounds/242501/)
by GabrielAraujo, and
[Postit Remove](https://www.freesound.org/people/Ignitor/sounds/182575/)
by Ignitor, all from [Freesound](http://www.freesound.org), both
distributed, under a Creative Commons licence.


