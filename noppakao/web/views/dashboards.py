import datetime
import mongoengine as me
from bson import ObjectId
from datetime import datetime

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
from .. import forms
from .. import oauth

module = Blueprint("dashboards", __name__, url_prefix="/dashboard")


# @module.route("/", methods=["GET", "POST"])
# @login_required
# def index():
#     teams = models.Team.objects(status="active").order_by("-score", "updated_date")
#     users = models.User.objects(status="active", roles__ne="admin").order_by(
#         "-score", "updated_date"
#     )

#     return render_template(
#         "dashboards/index.html",
#         teams=teams,
#         users=users,
#     )


@module.route("/<event_id>/", methods=["GET", "POST"])
@login_required
def index(event_id):
    challenges = models.Challenge.objects()
    teams = models.Team.objects(status="active")
    users = models.User.objects(status="active")

    event = models.Event.objects(id=event_id).first()
    event_challenges = models.EventChallenge.objects(event=event, status="active")
    event_categorys = []
    dialog_state = {"status": request.args.get("dialog_state", None)}
    team = models.Team.objects(members__in=[current_user], status="active").first()
    now = datetime.now()

    if not team and event.type == "team":
        msg = "Please create a team."
        return redirect(url_for("events.index", msg=msg))

    if not current_user.check_join_event(event.id):
        msg = "คุณกำลังพยายามเข้าไปใน กิจกรรมที่คุณไม่ได้เข้าร่วม"
        return redirect(url_for("events.index", msg=msg))

    for event_challenge in event_challenges:
        if not event_challenge.challenge.category in event_categorys:
            event_categorys.append(event_challenge.challenge.category)

    if event.type == "team":

        pipeline_user = [
            {"$match": {"event": ObjectId(event_id)}},
            {
                "$group": {
                    "_id": {
                        "user": "$user",
                        "team": "$team",
                    },
                    "total_score": {"$sum": "$score"},
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id.user",
                    "foreignField": "_id",
                    "as": "user_info",
                },
            },
            {"$unwind": "$user_info"},
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "_id.team",
                    "foreignField": "_id",
                    "as": "team_info",
                }
            },
            {"$unwind": "$team_info"},
            {
                "$project": {
                    "_id": 0,
                    "event": "$_id.event",
                    "total_score": 1,
                    "display_name": "$user_info.display_name",
                    "team": "$team_info.name",
                    "team_id": "$_id.team",
                }
            },
            {"$sort": {"total_score": -1}},
        ]

        pipeline_team = [
            {"$match": {"event": ObjectId(event_id)}},
            {
                "$group": {
                    "_id": {
                        "team": "$team",
                        "event": ObjectId(event_id),
                    },
                    "total_score": {"$sum": "$score"},
                }
            },
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "_id.team",
                    "foreignField": "_id",
                    "as": "team_info",
                },
            },
            {"$unwind": "$team_info"},
            {
                "$project": {
                    "_id": 0,
                    "total_score": 1,
                    "event": "$_id.event",
                    "name": "$team_info.name",
                    "team_id": "$_id.team",
                }
            },
            {"$sort": {"total_score": -1}},
        ]

        teams_transaction = list(models.Transaction.objects.aggregate(pipeline_team))
        users_transaction = list(models.Transaction.objects.aggregate(pipeline_user))

        return render_template(
            "/dashboards/index.html",
            event_challenges=event_challenges,
            event=event,
            event_categorys=event_categorys,
            teams=teams,
            users=users,
            challenges=challenges,
            dialog_state=dialog_state,
            teams_transaction=teams_transaction,
            users_transaction=users_transaction,
            now=now,
        )

    else:
        pipeline_user = [
            {"$match": {"event": ObjectId(event_id)}},
            {
                "$group": {
                    "_id": {
                        "user": "$user",
                        "team": "$team",
                    },
                    "total_score": {"$sum": "$score"},
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id.user",
                    "foreignField": "_id",
                    "as": "user_info",
                },
            },
            {"$unwind": "$user_info"},
            {
                "$project": {
                    "_id": 0,
                    "event": "$_id.event",
                    "total_score": 1,
                    "display_name": "$user_info.display_name",
                }
            },
            {"$sort": {"total_score": -1}},
        ]

        users_transaction = list(models.Transaction.objects.aggregate(pipeline_user))

        return render_template(
            "/dashboards/index.html",
            event_challenges=event_challenges,
            event=event,
            event_categorys=event_categorys,
            teams=teams,
            users=users,
            challenges=challenges,
            dialog_state=dialog_state,
            users_transaction=users_transaction,
            now=now,
        )
