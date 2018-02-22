import hashlib
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from __init__ import app, session
from flask import request, flash, render_template
from wtforms import Form, validators, IntegerField
from config import conf

Base = declarative_base()
metadata = Base.metadata
event_shortname = conf.get("application", "shortname")
application_fee = str(conf.get("paypal", "fee"))


class DiscountCode(Base):  # user_id is participant code, default is NULL
    __tablename__ = 'discounts'

    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    code = Column(String)
    user_id = Column(String(16))


def generate_discount(i):
    s = "%s #%d" % (event_shortname, i)
    return hashlib.sha224(s.encode()).hexdigest()[:8]


class DiscountForm(Form):
    discount = IntegerField("Discount",
                            validators=[validators.NumberRange(min=0)],
                            default=0)


@app.route("/discount_codes.html", methods=["POST", ])
def do_discount():
    form = DiscountForm(request.form)

    if form.validate():
        new_code = DiscountCode(amount=form.discount.data, code="")

        try:
            session.add(new_code)
            session.commit()

            new_code.code = generate_discount(new_code.id)
            session.commit()

            return render_template("display_code.html", message="New discount code generated!", d_amount=new_code.amount, d_code=new_code.code)

        except Exception as e:
            logger().error("Exception in do_discount: %s" % str(e))
            flash("A database error occurred. Please resubmit your application \
            in a few minutes. If the problem persists, please contact the \
            organizers.")
            return render_template("discount_codes.html", form=form)

    else:
        return render_template("discount_codes.html", message="Please enter a number.",
                               form=form)
