from datetime import date, datetime
from tables import *
from __init__ import *
from config import conf
import requests
from flask import make_response

item_numbers = {
    "application": "application_item"
}

def get_item_number(short_desc):
    item_conf_entry = item_numbers[short_desc] if item_numbers[short_desc] else "other_item"
    return conf.get("pretix", item_conf_entry)

def create_order(prt, amount, short_desc, long_desc):
    new_order = Order(timestamp=datetime.now(),
        amount=amount, short_description=short_desc,
        long_description=long_desc, status=OrderStatus.unpaid,
        participant=prt, comment="")

    session.add(new_order)
    session.flush()

    headers = {'Authorization': "Token %s" % conf.get("pretix", "token")}

    r = requests.post("%s/orders/" % conf.get("pretix", "api"), headers=headers, json={
        "email": prt.email,
        "locale": "en",
        "sales_channel": "web",
        "fees": [
        ],
        "comment": "# Participant ID: %d, Order ID: %d, Description: \"%s\", Amount: %d" % (prt.id, new_order.id, long_desc, amount),
        "positions": [
            {
                "item": get_item_number(short_desc),
                "variation": None,
                "price": amount,
                "attendee_name_parts": {
                    "full_name": "%s %s" % (prt.firstname, prt.lastname)
                }
            }
        ],
        "invoice_address": {
            "name": "%s %s" % (prt.firstname, prt.lastname),
            "street": prt.street,
            "city": prt.city,
            "zipcode": prt.zip,
            "country": prt.country
        }
    })

    new_order.pretix_ref = r.json()[u'secret']
    new_order.pretix_url = r.json()[u'url']
    session.flush()

@app.route("/fetch_all_orders/<token>", methods=["GET", ])
def fetch_all_orders(token):
    if token == conf.get("order", "cron_token"):
        headers = {'Authorization': "Token %s" % conf.get("pretix", "token")}
        r = requests.get("%s/orders/" % conf.get("pretix", "api"), headers=headers)
        count = r.json()[u'count']
        items = []
        updated_items = []
        for item in r.json()[u'results']:
            local_item = session.query(Order).filter(Order.pretix_ref == item[u'secret']).first()
            o = {"pretix_status": item[u'status'], "pretix_total": float(item[u'total']), "pretix_comment": item[u'comment']}
            changed = False

            if local_item:
                o["db_total"] = local_item.amount
                o["comment"] = local_item.comment
                if int(o["db_total"]) != int(o["pretix_total"]):
                    o["comment"] += "Amount changed from %d to %d. " % (int(o["db_total"]), int(o["pretix_total"]))
                    changed = True
                o["long_desc"] = local_item.long_description
                o["new_status"] = local_item.status
                if local_item.status == OrderStatus.unpaid:
                    if item[u'status'] == "p":
                        o["comment"] += "Status changed: unpaid => paid. "
                        o["new_status"] = OrderStatus.paid
                        if local_item.short_description == "application":
                            prt = session.query(Participant).filter(Participant.id == local_item.participant_id).first()
                            prt.registration_status = 2
                        changed = True
                    elif item[u'status'] == "c" and local_item.status == OrderStatus.unpaid:
                        o["comment"] += "Status changed: unpaid => cancelled. "
                        o["new_status"] = OrderStatus.cancelled
                        changed = True

                local_item.comment = o["comment"]
                local_item.status = o["new_status"]
                local_item.amount = int(o["pretix_total"])
                session.flush()
            if changed:
                updated_items.append(o)
            else:
                items.append(o)

        session.commit()

        resp = make_response(render_template("fetch_all_orders.html", title="All orders", items=items, updated_items=updated_items, count=count))
        resp.mimetype = 'text/plain'
        return resp
    else:
        resp = make_response("invalid token")
        resp.mimetype = 'text/plain'
        return resp