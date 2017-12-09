FROM phusion/baseimage

RUN apt-get update
RUN apt-get install -y python3-dev python3-pip # gcc libxml2-dev libxslt1-dev zlib1g-dev

RUN pip3 install --upgrade pip
RUN pip3 install pymysql Flask sqlalchemy Flask-SQLAlchemy-Session wtforms paypalrestsdk XlsxWriter openpyxl

COPY *.py       /ehb2/
COPY templates/ /ehb2/templates/
COPY static/    /ehb2/static/

EXPOSE 5000


