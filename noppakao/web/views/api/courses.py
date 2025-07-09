from flask import Blueprint, request, send_file, url_for, abort
from flask.json import jsonify
from flask_login import current_user, login_required
from mongoengine import Q

from noppakao import models
from noppakao.web import acl

module = Blueprint("courses", __name__, url_prefix="/courses")


@module.route("/<course_question_id>", methods=["GET"])
@login_required
def show_hint(course_question_id):
    print(course_question_id)
    current_content = models.Challenge.objects(id=course_question_id).first()
    return jsonify({"hint": current_content.hint})
