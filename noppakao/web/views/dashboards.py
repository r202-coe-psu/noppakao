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
from .. import caches

module = Blueprint("dashboards", __name__, url_prefix="/dashboard")


# อันนี้แก้ คำนวณการคิดคะแนนผิด (ตรวจสอบตรงนี้ใหม่) fix
@module.route("/<event_id>", methods=["GET", "POST"])
@caches.cache.cached(timeout=60)
def index(event_id):
    teams = models.Team.objects(status="active")
    users = models.User.objects(status="active")

    event = models.Event.objects.get(id=event_id)
    now = datetime.now()

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
            user = models.User.objects(id=user_info["user_id"]).first()
            team = models.Team.objects(id=user_info["team_id"]).first()

            user_info["organization_id"] = user.organization.id
            user_info["organization_name"] = user.organization.name
            user_info["organization_image"] = user.organization.get_logo_url()
            user_info["team_image"] = team.get_logo_url()

            users_transaction_list.append(user_info)
        users_transaction = users_transaction_list

        teams_transaction = list(models.Transaction.objects.aggregate(pipeline_team))
        teams_transaction_list = []
        for team_info in teams_transaction:
            team_info["team"] = models.Team.objects(id=team_info["team_id"]).first()
            team_info["organizations"] = []
            for member in team_info["team"].members:
                if member.organization not in team_info["organizations"]:
                    team_info["organizations"].append(member.organization)

            teams_transaction_list.append(team_info)

        teams_transaction = teams_transaction_list
        return render_template(
            "/dashboards/index.html",
            event=event,
            teams=teams,
            users=users,
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

            # user_info["organization_id"] = user.organization.id
            # user_info["organization_name"] = user.organization.name
            user_info["organization_image"] = user.organization.get_logo_url()
            users_transaction_list.append(user_info)
        users_transaction = users_transaction_list

        return render_template(
            "/dashboards/index.html",
            event=event,
            teams=teams,
            users=users,
            users_transaction=users_transaction,
            now=now,
        )
