from paypal import Paypal, find_payment, ParticipantNotFoundException, PaymentFailedException, PaymentNotFoundException, DuplicatePaymentException
from werkzeug.utils import redirect
from confirmation_token import generate_confirmation_token, confirm_token

pp1 = Paypal(1,
             lambda url: redirect(url, code=302),
             lambda id, message: applyWithPaypalError(id, message),
             "/payment-success.html",
             "/payment-cancelled.html")

def confirmation_render(prt):
    if pp1.did_pay_before(prt):
        amount = 0
        items = []
    else:
        items = [PaymentItem("Application fee", application_fee)]
        amount = prt.final_fee + prt.donation

        if prt.donation > 0:
            items.append(PaymentItem("Donation", prt.donation))

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
        prt.confirmed_on = datetime.datetime.now()
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


def applyWithPaypalError(id, message):
    prt = session.query(Participant).filter(Participant.id == id).first()
    form = application_form(prt)
    flash(message)
    flask_session['sn_code'] = generate_confirmation_token(prt.email)
    return redirect("/confirm.html")


@app.route("/payment-cancelled.html", methods=["GET", ])
def paymentCancelled():
    print(request.args)
    print(request.form)
    token = request.args.get('token')
    prt = pp1.find_by_token(token)

    pp1.log(prt.id, PP_CANCELLED, "(payment cancelled on Paypal website)")

    flash("You have cancelled payment. Your application has not been processed. Please complete payment to apply for EHB.")
    flask_session['sn_code'] = generate_confirmation_token(prt.email)
    return redirect("/confirm.html")


@app.route("/payment-success.html", methods=["GET", ])
def paymentSuccess():
    # Paypal redirects the user to this URL once the user has approved the payment.
    # Now we still need to execute the payment.

    try:
        payment, prt = pp1.execute_payment(request.args)

        # amount = payment["transactions"][0]["amount"]["total"]  # get total amount from the Paypal return message
        amount = prt.final_fee + prt.donation

        # send confirmation email
        body = render_template("application_confirmation.txt", amount=int(amount), prt=prt, eventname=event_name,
                               shortname=event_shortname, final_fee=int(prt.final_fee), currency_symbol=currency_symbol)
        print(body)
        ehbmail.send([prt.id], "Application confirmed", [body], "Application page")

        return render_template("payment_confirmation.html", title="Apply!", amount=int(amount), data=prt, name=event_name, shortname=event_shortname, application_fee=int(application_fee))

    except ParticipantNotFoundException as e:
        # print("pnfe " + e.token)
        return "Unable to resolve the Paypal token '%s' to a participant. Please try resubmitting your application, or contact the organizers." % e.token
    except PaymentNotFoundException as e:
        # print("pm nfe " + e.paymentId)
        flash("Unable to resolve the Paypal payment ID '%s' to a payment. Please try resubmitting your application, or contact the organizers." % e.paymentId)
        flask_session['sn_code'] = generate_confirmation_token(prt.email)
        return redirect("/confirm.html")
    except DuplicatePaymentException as e:
        amount = application_fee + e.prt.donation
        return render_template("payment_confirmation.html", title="Apply!", amount=amount, data=e.prt, name=event_name, shortname=event_shortname, application_fee=("%.2f" % application_fee))
    except PaymentFailedException as e:
        flash("Something went wrong with your Paypal payment. Please contact the organizers.")
        flask_session['sn_code'] = generate_confirmation_token(prt.email)
        return redirect("/confirm.html")

################################################
#
# for fixing the billing disaster of EHB 2017
#
################################################


@app.route("/execute-payment.html", methods=["GET", ])
def executePaymentOops():
    oops_code = request.args.get("code")
    prt = lookup_oops(oops_code)

    if prt.last_paypal_status == PP_OOPS:
        items = [PaymentItem("Application fee", application_fee)]

        if prt.donation > 0:
            items.append(PaymentItem("Donation", prt.donation))

        total_amount = application_fee + prt.donation - discount

        return render_template("oops.html", prt=prt, payment_items=items, total_amount=total_amount)
    else:
        return render_template("no_oops.html", prt=prt)


@app.route("/execute-payment.html", methods=["POST", ])
def doExecutePaymentOops():
    amount = float(request.form["amount"])
    id = int(request.form["id"])
    prt = lp(id)

    return pp1.pay(prt.id, "%s Application Fee: %s %s" % (event_shortname, prt.firstname, prt.lastname), amount)


class PaymentItem:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount
