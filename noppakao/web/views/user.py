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
