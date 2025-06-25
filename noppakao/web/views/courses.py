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
@login_required
def index():
    courses = models.Course.objects(status="active").order_by("name")
    enrolled_courses = models.EnrollCourse.objects(user=current_user)

    enrolled_course_ids = [enrollment.course.id for enrollment in enrolled_courses]
    for course in courses:
        course.is_enrolled = course.id in enrolled_course_ids

    return render_template(
        "courses/index.html",
        courses=courses,
    )


@module.route("/<course_id>", methods=["GET"])
@login_required
def course_detail(course_id):
    return render_template(
        "courses/detail.html",
        course_id=course_id,
    )


@module.route("/<course_id>/content/<page_id>", methods=["GET"])
@login_required
def course_content(course_id, page_id):
    course = models.Course.objects(id=course_id)
    contents = models.CourseContent.objects(
        course=course_id, status="active"
    ).order_by("index")
    if not course:
        return redirect(url_for("course.index"))

    current_content = models.CourseContent.objects(
        course=course_id, index=page_id
    ).first()

    print("\n\n\n====>Current content")

    if not current_content:
        return redirect(url_for("course.course_detail", course_id=course_id))

    return render_template(
        "courses/content.html",
        course_id=course_id,
        page_id=page_id,
        course=course,
        contents=contents,
        current_content=current_content,
    )


@module.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template(
        "courses/dashboard.html",
        courses=[],
    )


@module.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    return render_template("courses/leaderboard.html")


@module.route("/enroll/<course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    course = models.Course.objects.get(id=course_id)
    if not course:
        return redirect(url_for("course.index"))

    if course in current_user.enrolled_course:
        # Already enrolled
        return redirect(url_for("course.course_detail", course_id=course_id))

    enroll = models.EnrollCourse(
        user=current_user,
        course=course,
    )
    enroll.save()

    return redirect(url_for("course.course_detail", course_id=course_id))
