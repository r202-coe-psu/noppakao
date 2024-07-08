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
from .. import oauth

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

module = Blueprint("accounts", __name__)


@module.route("/profile")
@login_required
def index():
    return render_template("accounts/index.html")


@module.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboards.index"))

    form = forms.accounts.LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        user = models.User.objects(username=username).first()
        if user:
            if user.status == "unregistered" and oauth.handle_authorized_user(form):
                return redirect(url_for("accounts.setup_password", user_id=user.id))
            elif user.status == "disactive":
                messages = ["บัญชีถูกระงับ กรุณาติดต่อผู้ดูแลระบบ"]
                return render_template(
                    "/accounts/login.html", form=form, messages=messages
                )
            elif user and oauth.handle_authorized_user(form):
                return redirect(url_for("dashboards.index"))

            else:
                messages = ["Username หรือ Passwords ไม่ถูกต้องกรุณากรอกใหม่"]
                return render_template(
                    "/accounts/login.html", form=form, messages=messages
                )
        else:
            messages = ["Username หรือ Passwords ไม่ถูกต้องกรุณากรอกใหม่"]
            return render_template("/accounts/login.html", form=form, messages=messages)

    return render_template("accounts/login.html", form=form)


@module.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("accounts.login"))


@module.route("/user/<user_id>/setup_password", methods=["GET", "POST"])
def setup_password(user_id):
    user = models.User.objects.get(id=user_id)
    form = forms.accounts.SetupPassword(obj=user)

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("accounts/setup_password.html", form=form)

    password_hash = bcrypt.generate_password_hash(form.password.data)

    # Set the hashed password directly to the user's password field
    user.password = password_hash
    user.status = "active"
    user.save()

    return redirect(url_for("accounts.login"))
