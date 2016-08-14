# EHB Website Server

This is the source code for the application page for the European Harmony Brigade (EHB). It was developed by Alexander Koller for EHB 2015 and 2016, and rewritten from scratch after EHB 2016. It provides the following functionality for the EHB registration process:

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
```

