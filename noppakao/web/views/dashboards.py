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
from .. import forms
from .. import oauth

module = Blueprint("dashboards", __name__, url_prefix="/dashboard")


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    teams = models.Team.objects(status="active").order_by("-score", "updated_date")
    users = models.User.objects(status="active", roles__ne="admin").order_by(
        "-score", "updated_date"
    )

    return render_template(
        "dashboards/index.html",
        teams=teams,
        users=users,
    )
