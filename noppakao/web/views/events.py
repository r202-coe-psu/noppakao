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
    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )
    events = models.Event.objects()
    event_role = models.EventRole.objects()
    msg = request.args.get("msg")
    return render_template(
        "events/index.html",
        events=events,
        msg=msg,
        event_role=event_role,
        teams=teams,
        users=users,
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


@module.route("/<event_id>/challenge", methods=["GET", "POST"])
@login_required
def challenge(event_id):
    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )
    event = models.Event.objects(id=event_id).first()
    event_challenges = models.EventChallenge.objects(event=event)
    event_categorys = []

    if not current_user.check_join_event(event.id):
        msg = "คุณกำลังพยายามเข้าไปใน กิจกรรมที่คุณไม่ได้เข้าร่วม"
        return redirect(url_for("events.index", msg=msg))

    for event_challenge in event_challenges:
        if not event_challenge.challenge.category in event_categorys:
            event_categorys.append(event_challenge.challenge.category)

    return render_template(
        "/challenges/index.html",
        event_challenges=event_challenges,
        event=event,
        event_categorys=event_categorys,
        teams=teams,
        users=users,
    )
