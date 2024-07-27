import datetime
import mongoengine as me

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    Response,
    send_file,
    redirect,
)

from flask_login import login_user, logout_user, login_required, current_user

from noppakao import models
from .. import forms
from .. import oauth

module = Blueprint("teams", __name__, url_prefix="/teams")


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    teams = models.Team.objects(status="active", members__in=[current_user])
    users = models.User.objects(status="active")
    return render_template(
        "teams/index.html",
        teams=teams,
        users=users,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"team_id": None})
@module.route("<team_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(team_id):
    team = None
    form = forms.teams.TeamsForm()

    if team_id:
        team = models.Team.objects.get(id=team_id)
        form = forms.teams.TeamsForm(obj=team)
    form.members.choices = [
        (str(user.id), user.get_fullname())
        for user in models.User.objects(status="active")
    ]
    if not form.validate_on_submit():
        if team:
            form.members.data = [str(member.id) for member in team.members]
        return render_template("/teams/create_or_edit.html", form=form, team=team)

    if not team_id:
        team = models.Team(
            created_by=current_user._get_current_object(),
            updated_by=current_user._get_current_object(),
        )
    if form.members.data:
        team.members = [
            models.User.objects(id=user_id).first() for user_id in form.members.data
        ]
    if not team_id:
        team.name = form.name.data
        if form.picture.data:
            team.picture.put(
                form.picture.data,
                filename=form.picture.data.filename,
                content_type=form.picture.data.content_type,
            )
    else:
        team.name = form.name.data
        if form.picture.data:
            team.picture.replace(
                form.picture.data,
                filename=form.picture.data.filename,
                content_type=form.picture.data.content_type,
            )
    team.updated_by = current_user
    team.save()
    return redirect(url_for("teams.index"))


@module.route("/<team_id>/delete", methods=["GET", "POST"])
@login_required
def delete(team_id):
    team = models.Team.objects.get(id=team_id)
    team.status = "disactive"
    team.save()
    return redirect(
        url_for("teams.index"),
    )


@module.route("/<team_id>/recover", methods=["GET", "POST"])
@login_required
def recover(team_id):
    team = models.Team.objects.get(id=team_id)
    team.status = "active"
    team.save()
    return redirect(url_for("teams.index"))


@module.route("/<team_id>/picture")
@login_required
def get_image(team_id):
    response = Response()
    response.status_code = 404
    team = models.Team.objects.get(id=team_id)
    if team.picture:
        response = send_file(
            team.picture,
            download_name=team.picture.filename,
            mimetype=team.picture.content_type,
        )
    return response
