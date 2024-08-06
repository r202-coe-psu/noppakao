import datetime
import mongoengine as me
from bson import ObjectId
from datetime import datetime
from bson.objectid import ObjectId

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


@module.route("/<event_id>/", methods=["GET", "POST"])
def index(event_id):
    challenges = models.Challenge.objects()
    teams = models.Team.objects(status="active")
    users = models.User.objects(status="active")

    event = models.Event.objects(id=event_id).first()
    event_challenges = models.EventChallenge.objects(event=event, status="active")
    event_categorys = []
    dialog_state = {"status": request.args.get("dialog_state", None)}
    now = datetime.now()

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
                    "user_id": "$_id.user",
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
                    "members": "$team_info.members",
                    "team_id": "$_id.team",
                }
            },
            {"$sort": {"total_score": -1}},
        ]

        users_transaction = list(models.Transaction.objects.aggregate(pipeline_user))
        users_transaction_list = []
        for user_info in users_transaction:
            user_id = ObjectId(user_info["user_id"])
            user = models.User.objects(id=user_id).first()

            organization_id = user.organization.id
            organization_name = user.organization.name
            organization_image = user.organization.image.filename
            user_info["organization_id"] = organization_id
            user_info["organization_name"] = organization_name
            user_info["organization_image"] = organization.get_logo_url()
            users_transaction_list.append(user_info)
        users_transaction = users_transaction_list

        teams_transaction = list(models.Transaction.objects.aggregate(pipeline_team))
        teams_transaction_list = []
        for team_info in teams_transaction:
            user_id = ObjectId(team_info["members"][0].id)
            user = models.User.objects(id=user_id).first()
            organization_id = user.organization.id
            organization_name = user.organization.name
            organization_image = user.organization.image.filename
            team_info["organization_id"] = organization_id
            team_info["organization_name"] = organization_name
            team_info["organization_image"] = organization_image
            teams_transaction_list.append(team_info)
        teams_transaction = teams_transaction_list

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
                    "user_id": "$_id.user",
                    "display_name": "$user_info.display_name",
                }
            },
            {"$sort": {"total_score": -1}},
        ]

        users_transaction = list(models.Transaction.objects.aggregate(pipeline_user))
        users_transaction_list = []
        for user_info in users_transaction:
            user_id = ObjectId(user_info["user_id"])
            user = models.User.objects(id=user_id).first()

            organization_id = user.organization.id
            organization_name = user.organization.name
            organization_image = user.organization.image.filename
            user_info["organization_id"] = organization_id
            user_info["organization_name"] = organization_name
            user_info["organization_image"] = organization_image
            users_transaction_list.append(user_info)
        users_transaction = users_transaction_list

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
