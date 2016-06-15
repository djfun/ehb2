
from __init__ import *
from tables import *


@app.route("/show-participants.html")
def show_participants():
    participants = session.query(Participant).all()
    return render_template("show_participants.html", title="Show participants", participants=participants)
