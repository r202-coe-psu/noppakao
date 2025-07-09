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
from .. import oauth2

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


@module.route("<challenge_resource_id>/download_file", methods=["GET", "POST"])
@login_required
def download(challenge_resource_id):
    challenge_resource = models.ChallengeResource.objects(id=challenge_resource_id)
    try:
        challenge_resource = models.ChallengeResource.objects(
            id=challenge_resource_id
        ).first()
    except:
        return abort(404)

    res = send_file(
        challenge_resource.file,
        download_name=challenge_resource.file.filename,
        mimetype=challenge_resource.file.content_type,
    )
    return res
