import ast
import datetime
import json
import re

# https://github.com/paypal/PayPal-Python-SDK
import paypalrestsdk
from paypalrestsdk.payments import Payment

from config import conf
from __init__ import *
from helpers import PP_TOKEN, PP_ERROR, PP_APPROVED, PP_SUCCESS
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
          # At this point, we have created the payment, but the participant
          # hasn't yet had a chance to approve it.

          for link in payment.links:
            # One of the links should have a method of "REDIRECT". This is a Paypal URL
            # at which the participant can approve the payment. Find it and redirect the
            # participant there.
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
            self.log(id, PP_ERROR, str(payment.error))
            return self.errorPage(id, "An error occurred while processing your payment. Please contact the organizers.")

    def find_by_token(self, token):
        return session.query(self.pst).filter(self.pst.paypal_token == token).first()




    def execute_payment(self, args):
        # The URL is of the form: http://localhost:5001/payment-success.html?paymentId=PAY-7US79692XR919631JLB7SUGY&token=EC-8KP41677BL107680E&PayerID=UB6Z4EQPBR8H6
        # args are the arguments of this request

        token = args.get('token')
        paymentId = args.get("paymentId")
        payerId = args.get("PayerID")

        arg_str = "args: token=%s, paymentId=%s, payerId=%s" % (token, paymentId, payerId)

        prt = self.find_by_token(token)
        if not prt:
            raise ParticipantNotFoundException(token)

        if prt.last_paypal_status == PP_SUCCESS:
            # user already paid
            self.log(prt.id, PP_SUCCESS, "(duplicate payment attempt)")
            raise DuplicatePaymentException(prt)

        payment = Payment.find(paymentId)
        if not payment:
            self.log(prt.id, PP_ERROR, "Payment not found: " + paymentId)
            raise PaymentNotFoundException(paymentId, prt)

        # log payment as approved (but not yet executed)
        self.logj(prt.id, PP_APPROVED, str(payment))

        result = payment.execute({"payer_id": payerId})
        if not result:
            self.log(prt.id, PP_ERROR, "Payment failed (execute returned false)")
            raise PaymentFailedException(prt, payment)

        self.logj(prt.id, PP_SUCCESS, str(payment))
        return payment, prt


class DuplicatePaymentException(Exception):
    def __init__(self, prt):
        self.prt = prt

class ParticipantNotFoundException(Exception):
    def __init__(self, token):
        self.token = token

class PaymentNotFoundException(Exception):
    def __init__(self, paymentId, prt):
        self.paymentId = paymentId
        self.prt = prt

class PaymentFailedException(Exception):
    def __init__(self, prt, payment):
        self.prt = prt
        self.payment = payment