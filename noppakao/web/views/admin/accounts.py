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
from noppakao.web import forms, acl
from noppakao.utils import updater_info

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

module = Blueprint("accounts", __name__, url_prefix="/accounts")


@module.route("/")
@acl.roles_required("admin")
def index():
    users = models.User.objects()
    return render_template(
        "/admin/accounts/index.html",
        users=users,
    )


@module.route("/<user_id>/delete", methods=["GET", "POST"])
@acl.roles_required("admin")
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
@acl.roles_required("admin")
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
@acl.roles_required("admin")
def create_or_edit(user_id):
    form = forms.accounts.RegistrationForm()
    user = models.User.objects()
    msg_error = ""

    if user_id:
        user = models.User.objects.get(id=user_id)
        form = forms.accounts.UpdateUserForm(obj=user)
        form.username.validators = []
        form.password.validators = []

    if not form.validate_on_submit():
        user.username = form.username.data

        return render_template(
            "/admin/accounts/create_edit.html",
            form=form,
            user=user,
            msg_error=msg_error,
        )

    check_user = models.User.objects(username=form.username.data)
    check_email = models.User.objects(email=form.email.data)

    if check_user and not "edit" in request.path:
        msg_error = "This user is already in use"
        return render_template(
            "/admin/accounts/create_edit.html",
            form=form,
            user=user,
            msg_error=msg_error,
        )
    if check_email and not "edit" in request.path:
        msg_error = "This email is already in use"
        return render_template(
            "/admin/accounts/create_edit.html",
            form=form,
            user=user,
            msg_error=msg_error,
        )

    if not user_id:
        display_name = form.display_name.data
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = bcrypt.generate_password_hash(form.password.data)
        user = models.User(
            display_name=display_name,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=form.email.data,
            last_login_date=datetime.datetime.now(),
            status="unregistered",
        )
    else:
        form.populate_obj(user)

    user.save()
    return redirect(
        url_for("admin.accounts.index"),
    )
