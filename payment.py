from werkzeug.utils import redirect
from confirmation_token import generate_confirmation_token, confirm_token
from __init__ import *
from tables import *
from order import *
from datetime import date, datetime
from flask import request, flash
from flask import session as flask_session
from config import conf, currency_symbol
from helpers import *

application_fee = float(conf.get("payment", "fee"))
event_name = conf.get("application", "name")
event_shortname = conf.get("application", "shortname")
base_url = conf.get("server", "base_url")

conf_data = {"name": event_name,
             "shortname": event_shortname,
             "s_application_fee": str(application_fee),
             }

def confirmation_render(prt):
    items = []
    amount = 0
    orders = session.query(Order).filter(Order.participant_id == prt.id, Order.status == OrderStatus.unpaid).all()
    for order in orders:
        items.append(PaymentItem(order.long_description, order.amount, order.pretix_url))
        amount += order.amount

    return render_template("confirm.html", title="Confirm email address", prt=prt, payment_items=items, total_amount=amount, conf_data=conf_data)


@app.route('/confirm_email/<confirmation_code>')
def confirm_email(confirmation_code):
    try:
        email = confirm_token(confirmation_code)
    except:
        flash('The confirmation link is invalid.', 'danger')
        return redirect("/")
    prt = session.query(Participant).filter(Participant.email == email).first()
    if prt.confirmed:
        flash('Account already confirmed.', 'success')
    else:
        prt.confirmed = True
        prt.confirmed_on = datetime.now()
        session.add(prt)
        session.commit()
        flash('You have confirmed your account. Thanks!', 'success')

    flask_session['sn_code'] = generate_confirmation_token(prt.email)
    return redirect("/confirm.html")


@app.route("/confirm.html", methods=["GET", ])
def confirmation_page():
    code = flask_session.get('sn_code')
    if code:
        try:
            email = confirm_token(code)
            prt = session.query(Participant).filter(Participant.email == email).first()
        except:
            return redirect("/")
        return confirmation_render(prt)
    return redirect("/")


class PaymentItem:
    def __init__(self, name, amount, url):
        self.name = name
        self.amount = amount
        self.pretix_url = url