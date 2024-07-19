import datetime
import mongoengine as me

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
)

from flask_login import login_user, logout_user, login_required, current_user

from noppakao import models
from noppakao.web import forms

module = Blueprint("events", __name__, url_prefix="/events")


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    events = models.Event.objects()
    event_role = models.EventRole.objects()
    msg = request.args.get("msg")
    return render_template(
        "events/index.html", events=events, msg=msg, event_role=event_role
    )


@module.route("/<event_id>/join", methods=["GET", "POST"])
@login_required
def join(event_id):
    event = models.Event.objects(id=event_id).first()
    code = request.args.get("code")
    msg = ""

    if event.code != code:
        msg = "Code mismatch"
        return redirect(url_for("events.index", msg=msg))

    msg = "Successfully joined"

    event_role = models.EventRole()
    event_role.event = event
    event_role.user = current_user
    event_role.created_by = current_user._get_current_object()
    event_role.updated_by = current_user._get_current_object()
    event_role.save()

    return redirect(url_for("events.index", msg=msg))
