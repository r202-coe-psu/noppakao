import datetime
import mongoengine as me
import os
from mongoengine.queryset.visitor import Q

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
    send_file,
    abort,
)

from werkzeug.security import check_password_hash
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from noppakao.utils import updater_info
from noppakao import models
from noppakao.web import forms
from .. import oauth

from . import paginations

module = Blueprint("challenges", __name__, url_prefix="/challenges")
bcrypt = Bcrypt()


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    challenges = models.Challenge.objects()
    flag = request.args.get("flag")
    challenge_id = request.args.get("challenge_id")

    if flag and challenge_id:
        return redirect(
            url_for(
                "challenges.challenge_challenge",
                challenge_id=challenge_id,
                flag=flag,
            )
        )

    return render_template(
        "challenges/index.html",
        challenges=challenges,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"challenge_id": None})
@module.route("/<challenge_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(challenge_id):
    challenge = None
    form = forms.challenges.ChallengeForm()

    if challenge_id:
        challenge = models.Challenge.objects(id=challenge_id).first()
        form = forms.challenges.ChallengeForm(obj=challenge)
    form.category.choices = [
        (f"{category.id}", category.name)
        for category in models.Category.objects(status="active")
    ]
    if not form.validate_on_submit():
        if challenge:
            form.category.data = str(challenge.category.id)
        print(form.errors)
        return render_template(
            "challenges/create_or_edit.html", form=form, challenge=challenge
        )
    if not challenge_id:
        challenge = models.Challenge()
        challenge.created_by = current_user
    form.populate_obj(challenge)
    if not challenge_id:
        if form.uploaded_file.data:
            challenge.challenge_file.put(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )
    else:
        if form.uploaded_file.data:
            challenge.challenge_file.replace(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )
    challenge.category = models.Category.objects(id=form.category.data).first()
    challenge.updated_by = current_user
    challenge.save()
    return redirect(url_for("challenges.index"))


@module.route("<challenge_id>/download_file", methods=["GET", "POST"])
@login_required
def download(challenge_id):
    challenge = models.Challenge.objects(id=challenge_id)
    try:
        challenge = models.Challenge.objects(id=challenge_id).first()
    except:
        return abort(404)

    res = send_file(
        challenge.upload_file,
        download_name=challenge.upload_file.filename,
        mimetype=challenge.upload_file.content_type,
    )
    return res


@module.route("<challenge_id>/challenge/<flag>", methods=["GET", "POST"])
@login_required
def challenge_challenge(challenge_id, flag):

    try:
        challenge = models.Challenge.objects.get(id=challenge_id)
        team = models.Team.objects.get(id=current_user.team.id)
    except:
        return redirect(url_for("challenges.index"))

    if check_password_hash(challenge.flag, flag) and not "admin" in current_user.roles:
        if not current_user.team.name in challenge.problem_solvers:
            current_user.score += challenge.point
            team.score += challenge.point
            challenge.problem_solvers.append(current_user.team.name)
            team.updated_date = datetime.datetime.now()
            current_user.updated_date = datetime.datetime.now()

    challenge.save()
    current_user.save()
    team.save()
    return redirect(url_for("challenges.index"))
