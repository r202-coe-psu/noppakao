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


module = Blueprint("course", __name__, url_prefix="/course")

# TODO: Add authentication


@module.route("/", methods=["GET"])
def index():
    courses = models.Course.objects(status="active").order_by("name")

    return render_template(
        "courses/index.html",
        courses=courses,
    )


@module.route("/<course_id>", methods=["GET"])
def course_detail(course_id):
    return render_template(
        "courses/course_detail.html",
        course_id=course_id,
    )


@module.route("/<course_id>/content/<page_id>", methods=["GET"])
def course_content(course_id, page_id):
    return render_template(
        "courses/content.html",
        course_id=course_id,
        page_id=page_id,
    )


@module.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template(
        "courses/dashboard.html",
        courses=[],
    )


@module.route("/leaderboard", methods=["GET"])
def leaderboard():
    return render_template(
        "courses/leaderboard.html"
    )
