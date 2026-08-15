import hmac

from flask import Blueprint, abort, request
from flask.json import jsonify

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
        "hard_level": challenge.hard_level,
        "answer": challenge.answer,
        "description": challenge.description,
        "challenge_url": challenge.challenge_url,
        "hint": challenge.hint,
    }
    return jsonify(data)


@module.route("/<challenge_id>/check")
@acl.roles_required("admin")
def check_answer(challenge_id):
    """ตรวจคำตอบสำหรับ preview ของ admin ใช้เกณฑ์เดียวกับ EventChallenge.check_answer
    แต่ไม่ผูกกับ event จึงไม่มี flag_prefix ให้ส่งเข้ามาเองได้"""
    challenge = models.Challenge.objects(id=challenge_id).first()
    if not challenge:
        return abort(404)

    answer = request.args.get("answer", "")
    flag_prefix = request.args.get("flag_prefix", "")

    if challenge.answer_type == "flag":
        expected = f"{flag_prefix}{{{challenge.answer}}}"
    else:
        expected = challenge.answer

    return jsonify({"correct": hmac.compare_digest(answer, expected)})
