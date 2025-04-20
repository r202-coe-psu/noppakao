from flask import Blueprint, render_template
from flask_login import login_required
from flask_login import login_user, logout_user, login_required, current_user
from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
)

module = Blueprint("index", __name__)


@module.route("/")
@login_required
def index():
    if current_user:
        if "admin" in current_user.roles:
            return redirect(url_for("admin.events.index"))
        return redirect(url_for("events.index"))
    return render_template("/index/index.html")
