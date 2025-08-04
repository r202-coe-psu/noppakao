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


@module.route("/dashboards", methods=["GET", "POST"])
def dashboards():
    events = models.Event.objects(status="active")
    return render_template(
        "events/dashboards.html",
        events=events,
    )


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )
    events = models.Event.objects()
    event_role = models.EventRole.objects()
    now = datetime.datetime.now()
    msg = request.args.get("msg")
    return render_template(
        "events/index.html",
        events=events,
        msg=msg,
        event_role=event_role,
        teams=teams,
        users=users,
        now=now,
    )


@module.route("/<event_id>/joiner", methods=["GET", "POST"])
@login_required
def joiner(event_id):
    event = models.Event.objects.get(id=event_id)
    teams = models.Team.objects(event=event)
    now = datetime.datetime.now()
    return render_template("events/joiner.html", event=event, teams=teams, now=now)


@module.route("/<event_id>/create_team", methods=["GET", "POST"])
@login_required
def create_team(event_id):
    event = models.Event.objects.get(id=event_id)
    form = forms.teams.TeamsEventForm()
    if not form.validate_on_submit():
        print(form.errors)
        return render_template("events/create_team.html", form=form)
    team = models.Team()
    form.populate_obj(team)

    if form.uploaded_picture.data:
        if not team.picture:
            team.picture.put(
                form.uploaded_picture.data,
                filename=form.uploaded_picture.data.filename,
                content_type=form.uploaded_picture.data.content_type,
            )

    team.members.append(current_user._get_current_object())
    team.event = event
    team.save()
    return redirect(url_for("events.joiner", event_id=event.id))


@module.route("/<event_id>/join", methods=["GET", "POST"])
@login_required
def join(event_id):
    event = models.Event.objects(id=event_id).first()
    all_team = models.EventCompetitor.objects(event=event).distinct(field="team")
    all_team_competitor = [team.members for team in all_team if team.status == "active"]
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


@module.route("/<event_id>/teams/<team_id>/leave_team", methods=["GET", "POST"])
@login_required
def leave_team(event_id, team_id):
    team = models.Team.objects.get(id=team_id)

    current_user_obj = current_user._get_current_object()

    if current_user_obj in team.members:
        team.members.remove(current_user_obj)
        team.save()

    return redirect(url_for("events.joiner", event_id=event_id))


@module.route("/<event_id>/teams/<team_id>/join_team", methods=["GET", "POST"])
@login_required
def join_team(event_id, team_id):
    team = models.Team.objects.get(id=team_id)

    if models.Team.objects(
        event=event_id, members__in=[current_user._get_current_object()]
    ).first():
        return redirect(url_for("events.joiner", event_id=event_id))

    team.members.append(current_user._get_current_object())
    team.save()

    return redirect(url_for("events.joiner", event_id=event_id))


@module.route("/<event_id>/challenge", methods=["GET", "POST"])
@login_required
def challenge(event_id):
    event = models.Event.objects(id=event_id).first()
    if not current_user.check_team_event(event_id) and event.type == "team":
        return redirect(url_for("events.joiner", event_id=event_id))

    if event.started_date > datetime.datetime.now():
        return redirect(url_for("events.index"))

    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )
    challenge_resources = models.ChallengeResource.objects()

    event_challenges = models.EventChallenge.objects(event=event, status="active")

    dialog_state = {"status": request.args.get("dialog_state", None)}
    if not current_user.check_join_event(event.id):
        msg = "คุณกำลังพยายามเข้าไปใน กิจกรรมที่คุณไม่ได้เข้าร่วม"
        return redirect(url_for("events.index", msg=msg))

    return render_template(
        "/challenges/index.html",
        event_challenges=event_challenges,
        event=event,
        teams=teams,
        users=users,
        dialog_state=dialog_state,
        challenge_resources=challenge_resources,
        event_id=event_id,
    )


@module.route(
    "/<event_id>/challenges/<challenge_id>/submit_challenge", methods=["GET", "POST"]
)
@login_required
def submit_challenge(event_id, challenge_id):
    event_challenge = models.EventChallenge.objects(id=challenge_id).first()

    event = models.Event.objects.get(id=event_id)
    transaction = models.Transaction.objects(
        event_challenge=event_challenge, status__in=["success", "first_blood"]
    )
    now = datetime.datetime.now()
    answer = request.args.get("answer")

    if now > event.ended_date:
        return redirect(url_for("events.index", msg="Event Time Out"))

    if not transaction and event_challenge.check_answer(answer):
        transaction = models.Transaction()
        transaction.type = "answer"
        transaction.status = "first_blood"
        transaction.score = event_challenge.first_blood_score
        transaction.event_challenge = event_challenge
        transaction.event = event
        transaction.answer = answer
        transaction.user = current_user
        if event.type == "team":
            team = models.Team.objects(
                members__in=[current_user], status="active", event=event
            ).first()
            transaction.team = team
        transaction.save()
        return redirect(
            url_for("events.challenge", event_id=event.id, dialog_state="first_blood")
        )

    transaction = models.Transaction()

    if event.type == "team":
        team = models.Team.objects(
            members__in=[current_user], status="active", event=event
        ).first()
        transaction.team = team

    if event_challenge.solve_challenge():
        return redirect(
            url_for(
                "events.challenge",
                event_id=event.id,
            )
        )

    if not event_challenge.check_answer(answer):
        transaction.type = "answer"
        transaction.status = "fail"
        transaction.score = event_challenge.fail_score
        transaction.event_challenge = event_challenge
        transaction.event = event
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
    transaction.event = event
    transaction.answer = answer
    transaction.user = current_user
    transaction.save()

    return redirect(
        url_for("events.challenge", event_id=event.id, dialog_state="success")
    )
