import datetime
import mongoengine as me

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
from noppakao.web import forms
from noppakao.utils import updater_info

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

module = Blueprint("users", __name__, url_prefix="/users")


@module.route("/")
@login_required
def index():
    users = models.User.objects()

    return render_template(
        "/users/index.html",
        users=users,
    )


@module.route("/<user_id>/delete", methods=["GET", "POST"])
@login_required
def delete(user_id):
    user = models.User.objects.get(id=user_id)
    user.status = "disactive"
    user.update_info.append(
        updater_info.create_update_information(current_user, request, "deleted")
    )
    user.save()
    return redirect(
        url_for("users.index"),
    )


@module.route("/<user_id>/recover", methods=["GET", "POST"])
@login_required
def recover(user_id):
    user = models.User.objects.get(id=user_id)
    user.status = "unregistered"
    user.password = bcrypt.generate_password_hash("admin")
    user.update_info.append(
        updater_info.create_update_information(current_user, request, "recover")
    )
    user.save()
    return redirect(url_for("users.index"))


@module.route(
    "/create",
    methods=["GET", "POST"],
    defaults={"user_id": None},
)
@module.route("/<user_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(user_id):
    form = forms.accounts.RegistrationForm()
    user = models.User.objects()
    teams = models.Teams.objects(status="active")
    msg_error = ""

    if user_id:
        user = models.User.objects.get(id=user_id)
        form = forms.accounts.UpdateUserForm(obj=user)
        user.update_info.append(
            updater_info.create_update_information(current_user, request, "updated")
        )
        form.username.validators = []
        form.password.validators = []

    form.team.choices = [(i.id, i.name) for i in teams]

    if not form.validate_on_submit():

        user.username = form.username.data
        print(form.errors)
        return render_template(
            "/users/create-edit.html", form=form, user=user, msg_error=msg_error
        )

    check_user = models.User.objects(username=form.username.data)
    check_email = models.User.objects(email=form.email.data)

    if check_user and not "edit" in request.path:
        msg_error = "This user is already in use"
        return render_template(
            "/users/create-edit.html", form=form, user=user, msg_error=msg_error
        )
    if check_email and not "edit" in request.path:
        msg_error = "This email is already in use"
        return render_template(
            "/users/create-edit.html", form=form, user=user, msg_error=msg_error
        )

    if not user_id:
        team = models.Teams.objects.get(id=form.team.data)
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = bcrypt.generate_password_hash(form.password.data)
        user = models.User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            team=team,
            email=form.email.data,
            last_login_date=datetime.datetime.now(),
            status="unregistered",
        )
        user.update_info.append(
            updater_info.create_update_information(current_user, request, "created")
        )
    else:
        form.populate_obj(user)
        team = models.Teams.objects.get(id=form.team.data)
        user.team = team

    user.save()
    return redirect(
        url_for("users.index"),
    )
