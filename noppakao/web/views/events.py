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

    if event.type == "team":
        team = models.Team.objects(members__in=[current_user]).first()
        if team:
            event_competitor = models.EventCompetitor()
            event_competitor.team = team
            event_competitor.event = event
            event_competitor.created_by = current_user._get_current_object()
            event_competitor.updated_by = current_user._get_current_object()
            event_competitor.save()
        else:
            msg = "Please create a team."
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
    challenges = models.Challenge.objects()
    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )
    event = models.Event.objects(id=event_id).first()
    event_challenges = models.EventChallenge.objects(event=event)
    event_categorys = []
    dialog_state = {"status": request.args.get("dialog_state", None)}

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
        challenges=challenges,
        dialog_state=dialog_state,
    )


@module.route(
    "/<event_id>/challenges/<challenge_id>/submit_challenge", methods=["GET", "POST"]
)
@login_required
def submit_challenge(event_id, challenge_id):
    event_challenge = models.EventChallenge.objects(id=challenge_id).first()

    event = models.Event.objects(id=event_id).first()
    transaction = models.Transaction.objects(event_challenge=event_challenge)
    now = datetime.datetime.now()
    answer = request.args.get("answer")

    if now < event.ended_date:
        return redirect(url_for("events.index"))

    if not transaction and event_challenge.check_answer(answer):
        transaction = models.Transaction()
        transaction.type = "answer"
        transaction.status = "first_blood"
        transaction.score = event_challenge.first_blood_score
        transaction.event_challenge = event_challenge
        transaction.answer = answer
        transaction.user = current_user
        if event.type == "team":
            team = models.Team.objects(members__in=[current_user]).first()
            transaction.team = team
        transaction.save()
        return redirect(
            url_for("events.challenge", event_id=event.id, dialog_state="first_blood")
        )

    transaction = models.Transaction()

    if event.type == "team":
        team = models.Team.objects(members__in=[current_user]).first()
        transaction.team = team

    if not event_challenge.check_answer(answer):
        transaction.type = "answer"
        transaction.status = "fail"
        transaction.score = event_challenge.fail_score
        transaction.event_challenge = event_challenge
        transaction.answer = answer
        transaction.user = current_user
        transaction.save()
        return redirect(
            url_for("events.challenge", event_id=event.id, dialog_state="fail")
        )

    transaction.type = "answer"
    transaction.status = "success"
    transaction.score = event_challenge.success_score
    transaction.event_challenge = event_challenge
    transaction.answer = answer
    transaction.user = current_user
    transaction.save()

    return redirect(
        url_for("events.challenge", event_id=event.id, dialog_state="success")
    )
