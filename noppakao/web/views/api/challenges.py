from flask import Blueprint, request, send_file, url_for, abort
from flask.json import jsonify
from flask_login import current_user, login_required
from mongoengine import Q

from noppakao import models
from noppakao.web import acl

module = Blueprint("challenge", __name__, url_prefix="/challenge")


@module.route("/<challenge_id>")
@acl.roles_required("admin")
def get_all_data(challenge_id):
    challenge = models.Challenge.objects(id=challenge_id).first()
    data = {
        "name": challenge.name,
        "category": challenge.category.name,
        "answer_type": challenge.answer_type,
        "answer": challenge.answer,
        "description": challenge.description,
        "challenge_url": challenge.challenge_url,
        "hint": challenge.hint,
    }
    return jsonify(data)
