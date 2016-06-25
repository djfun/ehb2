
from config import cp


import paypalrestsdk

paypalrestsdk.configure({
  "mode":          cp.get("paypal", "mode"), # sandbox or live
  "client_id":     cp.get("paypal", "client_id"),
  "client_secret": cp.get("paypal", "client_secret") })

callback = cp.get("paypal", "callbackhost")

payment = paypalrestsdk.Payment({
  "intent": "sale",
  "payer": {
    "payment_method": "paypal"
  },
  "redirect_urls":{
    "return_url":  "%s/payment-success.html" % callback,
    "cancel_url":  "%s/payment-cancel.html" % callback
  },
  "transactions": [{
    "item_list": {
      "items": [{
        "name": "item1",   # label for user
        "sku": "item2",    # label for me
        "price": "1.00",
        "currency": "USD",
        "quantity": 1 }]},
    "amount": {
      "total": "1.00",
      "currency": "USD" },
    "description": "This is the payment transaction description." }]})


if payment.create():
  print("Payment created successfully")
  for link in payment.links:
      if link.method == "REDIRECT":
        print(str(link.href))
else:
  print(payment.error)
