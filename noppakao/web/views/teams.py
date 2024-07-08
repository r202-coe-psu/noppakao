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
    teams = models.Teams.objects()
    return render_template("teams/index.html", teams=teams)


@module.route("/create", methods=["GET", "POST"], defaults={"team_id": None})
@module.route("<team_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(team_id):
    teams = models.Teams.objects()
    form = forms.teams.TeamsForm()

    if team_id:
        teams = models.Teams.objects.get(id=team_id)
        form = forms.teams.TeamsForm(obj=teams)

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/teams/create_or_edit.html", form=form, teams=teams)

    if not team_id:
        teams = models.Teams(
            created_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )

    if not team_id:
        if form.picture.data:
            teams.picture.put(
                form.picture.data,
                filename=form.picture.data.filename,
                content_type=form.picture.data.content_type,
            )
        teams.name = form.name.data
    else:
        if form.picture.data:
            teams.picture.replace(
                form.picture.data,
                filename=form.picture.data.filename,
                content_type=form.picture.data.content_type,
            )
    teams.last_updated_by = current_user._get_current_object()
    teams.save()
    return redirect(url_for("teams.index"))


@module.route("/<team_id>/delete", methods=["GET", "POST"])
@login_required
def delete(team_id):
    teams = models.Teams.objects.get(id=team_id)
    teams.status = "disactive"
    teams.save()
    return redirect(
        url_for("teams.index"),
    )


@module.route("/<team_id>/recover", methods=["GET", "POST"])
@login_required
def recover(team_id):
    team = models.Teams.objects.get(id=team_id)
    team.status = "active"
    team.save()
    return redirect(url_for("teams.index"))


@module.route("/<team_id>/picture")
@login_required
def get_image(team_id):
    response = Response()
    response.status_code = 404
    team = models.Teams.objects.get(id=team_id)
    if team.picture:
        response = send_file(
            team.picture,
            download_name=team.picture.filename,
            mimetype=team.picture.content_type,
        )
    return response