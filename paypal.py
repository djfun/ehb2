import ast
import datetime
import json
import re

# https://github.com/paypal/PayPal-Python-SDK
import paypalrestsdk

from config import conf
from __init__ import *
from helpers import PP_TOKEN, PP_ERROR
from tables import PaypalHistory, Participant, Extra

paypalrestsdk.configure({
  "mode":          conf.get("paypal", "mode"), # sandbox or live
  "client_id":     conf.get("paypal", "client_id"),
  "client_secret": conf.get("paypal", "client_secret") })

callback = conf.get("server", "base_url").rstrip("/")
currency = conf.get("paypal", "currency")

payment_steps = {1: Participant,
                 2: Extra}


def log(id, payment_step, status, message):
    ph = PaypalHistory(participant_id=id, timestamp=datetime.datetime.now(), _paypal_status=status, data=message,
                       payment_step=payment_step)

    pst = payment_steps[payment_step]
    session.add(ph)
    session.query(pst).filter(pst.id == id).update({'last_paypal_status': status})
    session.commit()


def find_payment(paymentId):
    return paypalrestsdk.Payment.find(paymentId)



class Paypal:
    def __init__(self, payment_step, redirect, errorPage, successCallbackPath, cancelCallbackPath):
        self.redirect = redirect
        self.errorPage = errorPage
        self.successCallbackPath = successCallbackPath
        self.cancelCallbackPath = cancelCallbackPath
        self.re = re.compile("token=(.*)")
        self.pst = payment_steps[payment_step]
        self.payment_step = payment_step

    def log(self, id, status, message):
        log(id, self.payment_step, status, message)

    def logj(self, id, status, json_message):
        if isinstance(json_message, str):
            d = ast.literal_eval(json_message)
        elif isinstance(json_message, dict):
            d = json_message
        else:
            return self.log(id, status, str(json_message))

        formatted = json.dumps(d, indent=4, sort_keys=True)
        return self.log(id, status, formatted)

    def update_token(self, id, token):
        session.query(self.pst).filter(self.pst.id == id).update({'paypal_token': token})
        session.commit()

    def pay(self, id, description, cost):
        # -- reactivate this if you need more than one item per invoice --
        # pitems = [{"name": it[0], "sku": it[0], "price": "%.2f"%it[1], "currency": currency, "quantity":1} for it in items]
        # total = sum([it[1] for it in items])
        # print(total)
        # pamount = {"currency": currency, "total": ("%.2f" % total)}

        pitems = [{"name": description, "sku": description, "price":"%.2f" % cost, "currency":currency, "quantity":1}]
        pamount = {"currency": currency, "total":cost}

        payment = paypalrestsdk.Payment({
          "intent": "sale",
          "payer": {
            "payment_method": "paypal"
          },
          "redirect_urls":{
            "return_url": callback + self.successCallbackPath,
            "cancel_url": callback + self.cancelCallbackPath
          },
          "transactions": [{
            "item_list": { "items": pitems },
            "amount": pamount,
            "description": description }]})

        if payment.create():
          for link in payment.links:
            if link.method == "REDIRECT":
                m = self.re.search(str(link.href))

                if m:
                    self.logj(id, PP_TOKEN, str(payment))
                    self.update_token(id, m.group(1))
                    return self.redirect(str(link.href))
                else:
                    self.log(id, PP_ERROR, "Could not extract token, data: %s" % str(payment))
                    return self.errorPage(id, "Internal error. Please contact the organizers.")
        else:
            self.log(id, PP_ERROR, "An error occurred while processing your payment. Please contact the organizers.")
            return self.errorPage(id, payment.error)

    def find_by_token(self, token):
        return session.query(self.pst).filter(self.pst.paypal_token == token).first()

