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
from ... import acl


module = Blueprint("dashboards", __name__, url_prefix="/dashboard")


@module.route("/", methods=["GET", "POST"])
@acl.roles_required("admin")
def index():

    return render_template("dashboards/index.html")
