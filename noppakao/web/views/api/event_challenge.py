from flask import Blueprint, request, send_file, url_for, abort
from flask.json import jsonify
from flask_login import current_user, login_required
from mongoengine import Q

from noppakao import models
from noppakao.web import acl

module = Blueprint("events", __name__, url_prefix="/events")


@module.route("/<event_id>/event_challenges/<event_challege_id>")
@login_required
def show_hint(event_id, event_challege_id):
    event = models.Event.objects(id=event_id).first()
    event_challenge = models.EventChallenge.objects(id=event_challege_id).first()

    if event.type == "team":
        team = models.Team.objects(members__in=[current_user], status="active").first()
        trasaction = models.Transaction.objects(
            event_challenge=event_challenge, type="hint", team=team
        ).first()
    else:
        trasaction = models.Transaction.objects(
            event_challenge=event_challenge, type="hint", user=current_user
        ).first()

    if trasaction:
        return jsonify({"hint": event_challenge.challenge.hint})

    trasaction = models.Transaction()

    if event.type == "team":
        trasaction.team = team

    trasaction.type = "hint"
    trasaction.answer = ""
    trasaction.status = "fail"
    trasaction.score = event_challenge.hint_score
    trasaction.event = event
    trasaction.event_challenge = event_challenge
    trasaction.user = current_user
    trasaction.save()
    return jsonify({"hint": event_challenge.challenge.hint})
