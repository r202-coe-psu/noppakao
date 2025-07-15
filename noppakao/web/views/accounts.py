import datetime
import mongoengine as me

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
    Response,
    send_file,
)

from flask_login import login_user, logout_user, login_required, current_user

from noppakao import models
from noppakao.web import forms, acl
from .. import oauth2

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

module = Blueprint("accounts", __name__)


@module.route("/profile")
@login_required
def index():
    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )
    return render_template(
        "accounts/index.html",
        teams=teams,
        users=users,
    )


@module.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and "admin" not in current_user.roles:
        return redirect(url_for("events.index"))

    form = forms.accounts.LoginForm()

    if not form.validate_on_submit():
        return render_template("accounts/login.html", form=form)

    user = models.User.objects(username=form.username.data).first()

    if not user or not bcrypt.check_password_hash(
        user.password.decode("utf-8"), form.password.data
    ):
        messages = ["Username หรือ Passwords ไม่ถูกต้องกรุณากรอกใหม่"]
        return render_template("accounts/login.html", form=form, messages=messages)

    if user.status == "unregistered":
        return redirect(url_for("accounts.setup_password", user_id=user.id))
    elif user.status == "disactive":
        messages = ["บัญชีถูกระงับ กรุณาติดต่อผู้ดูแลระบบ"]
        return render_template("accounts/login.html", form=form, messages=messages)

    login_user(user)
    user.last_login_date = datetime.datetime.now()
    user.save()

    if "admin" in user.roles:
        return redirect(url_for("admin.events.index"))

    return redirect(url_for("events.index"))


@module.route(
    "/register",
    methods=["GET", "POST"],
)
def register():
    form = forms.accounts.RegistrationForm()
    user = models.User.objects()
    msg_error = ""

    if not form.validate_on_submit():
        user.username = form.username.data
        print(form.errors)
        return render_template(
            "/accounts/register.html", form=form, user=user, msg_error=msg_error
        )

    check_user = models.User.objects(username=form.username.data)
    check_email = models.User.objects(email=form.email.data)

    if check_user and not "edit" in request.path:
        msg_error = "This user is already in use"
        return render_template(
            "/accounts/register.html", form=form, user=user, msg_error=msg_error
        )
    if check_email and not "edit" in request.path:
        msg_error = "This email is already in use"
        return render_template(
            "/accounts/register.html", form=form, user=user, msg_error=msg_error
        )

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
        status="active",
    )
    user.save()
    return redirect(
        url_for("accounts.login"),
    )


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


@module.route("/login/<name>")
def login_oauth(name):
    client = oauth2.oauth2_client

    scheme = request.environ.get("HTTP_X_FORWARDED_PROTO", "http")

    redirect_uri = url_for(
        "accounts.authorized_oauth", name=name, _external=True, _scheme=scheme
    )
    response = None
    if name == "google":
        response = client.google.authorize_redirect(redirect_uri)
    elif name == "facebook":
        response = client.facebook.authorize_redirect(redirect_uri)
    elif name == "line":
        response = client.line.authorize_redirect(redirect_uri)

    elif name == "psu":
        response = client.psu.authorize_redirect(redirect_uri)
    elif name == "engpsu":
        response = client.engpsu.authorize_redirect(redirect_uri)
    return response


@module.route("/auth/<name>")
def authorized_oauth(name):
    client = oauth2.oauth2_client
    remote = None
    try:
        if name == "google":
            remote = client.google
        elif name == "facebook":
            remote = client.facebook
        elif name == "line":
            remote = client.line
        elif name == "psu":
            remote = client.psu
        elif name == "engpsu":
            remote = client.engpsu

        token = remote.authorize_access_token()

    except Exception as e:
        print("autorize access error =>", e)
        return redirect(url_for("accounts.login"))

    session["oauth_provider"] = name
    return oauth2.handle_authorized_oauth2(remote, token)


@module.route("/edit_user", methods=["GET", "POST"])
def edit_user():
    user = current_user._get_current_object()
    form = forms.accounts.EditUserForm(obj=user)
    if not form.validate_on_submit():
        return render_template("/accounts/edit_user.html", form=form)

    if form.uploaded_avatar.data:
        if not user.avatar:
            user.avatar.put(
                form.uploaded_avatar.data,
                filename=form.uploaded_avatar.data.filename,
                content_type=form.uploaded_avatar.data.content_type,
            )
        else:
            user.avatar.replace(
                form.uploaded_avatar.data,
                filename=form.uploaded_avatar.data.filename,
                content_type=form.uploaded_avatar.data.content_type,
            )
    user.display_name = form.display_name.data
    user.first_name = form.first_name.data
    user.phone_number = form.phone_number.data
    user.last_name = form.last_name.data
    user.save()
    return redirect(url_for("accounts.index"))


@module.route("/setup_user", methods=["GET", "POST"])
def setup_user():
    form = forms.accounts.SetupUser()
    user = current_user
    msg_error = ""
    form.organization.choices = [("", "ไม่เลือก")] + [
        (f"{organization.id}", f"{organization.name}")
        for organization in models.Organization.objects(status="active")
    ]
    if form.display_name.data:
        if models.User.objects(display_name=form.display_name.data).first():
            msg_error = "Can't use display name"

    if msg_error or not form.validate_on_submit():
        return render_template(
            "/accounts/setup_user.html", form=form, msg_error=msg_error
        )
    if form.organization.data:
        organization = models.Organization.objects(id=form.organization.data).first()
        user.organization = organization

    user.display_name = form.display_name.data
    user.save()

    return redirect(url_for("index.index"))


@module.route("/avatar/<filename>")
@login_required
def get_avatar(filename=""):
    response = Response()
    response.status_code = 404
    user = current_user._get_current_object()
    if user.avatar:
        response = send_file(
            user.avatar,
            download_name=user.avatar.filename,
            mimetype=user.avatar.content_type,
        )
    return response
