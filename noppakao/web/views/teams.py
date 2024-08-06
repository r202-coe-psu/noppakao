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
    if not current_user.organization:
        error = "Please, choose your organization before create or enroll team."
        return redirect(url_for("organizations.information", error=error))
    team = models.Team.objects(status="active", members__in=[current_user])

    # หากมีทีมแล้วห้ามสร้างทีมใหม่
    if team and not team_id:
        return redirect(url_for("teams.index"))
    error_msg = request.args.get("error_msg")
    team = None
    form = forms.teams.TeamsForm()

    old_members = []
    if team_id:
        team = models.Team.objects.get(id=team_id)
        form = forms.teams.TeamsForm(obj=team)
        if team.members:
            old_members = team.members
    form.members.choices = [
        (str(user.id), user.get_fullname())
        for user in models.User.objects(status="active")
        if user.organization
    ]
    if not form.validate_on_submit():
        if team:
            form.members.data = [str(member.id) for member in team.members]
        return render_template(
            "/teams/create_or_edit.html", form=form, team=team, error_msg=error_msg
        )

    new_members = [
        models.User.objects(id=user_id).first() for user_id in form.members.data
    ]
    if current_user not in new_members:
        error_msg = "Please choose yourself in your team"
        return redirect(
            url_for(
                "teams.create_or_edit",
                error_msg=error_msg,
                team_id=team_id,
            )
        )
    # เช็คสมาชิกหากแก้ไขในภายภายหลังไม่ให้แก้ไขแล้วนำคนซ้ำเข้าร่สมทีม
    if team and models.Team.objects().first():
        event_competitor = (
            models.EventCompetitor.objects(team=team).order_by("-created_date").first()
        )
        if event_competitor:
            event = event_competitor.event
            if event:
                all_team = models.EventCompetitor.objects(event=event).distinct(
                    field="team"
                )
                all_team_competitor = [
                    team.members for team in all_team if team.status == "active"
                ]
                for member in new_members:
                    if member not in old_members:
                        for team_competitor in all_team_competitor:
                            if member in team_competitor:
                                error_msg = "Only one user can be member in one team."
                                return redirect(
                                    url_for(
                                        "teams.create_or_edit",
                                        error_msg=error_msg,
                                        team_id=team_id,
                                    )
                                )
    if not team_id:
        team = models.Team(
            created_by=current_user._get_current_object(),
            updated_by=current_user._get_current_object(),
        )
    team.members = new_members
    if form.uploaded_picture.data:
        if not team.picture:
            team.picture.put(
                form.uploaded_picture.data,
                filename=form.uploaded_picture.data.filename,
                content_type=form.uploaded_picture.data.content_type,
            )
        else:
            team.picture.replace(
                form.uploaded_picture.data,
                filename=form.uploaded_picture.data.filename,
                content_type=form.uploaded_picture.data.content_type,
            )
    team.name = form.name.data
    team.updated_by = current_user
    # เช็คสมาชิกให้น้อยกว่า 3
    if len(team.members) > 3:
        error_msg = "Member must lower than 3 persons"
        return redirect(
            url_for(
                "teams.create_or_edit",
                error_msg=error_msg,
                team_id=team_id,
            )
        )

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
