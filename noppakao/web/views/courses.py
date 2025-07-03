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

import datetime

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


@module.route("/<course_id>/content", methods=["GET"])
@module.route("/<course_id>/content/<page_id>", methods=["GET"])
@login_required
def course_content(course_id, page_id=None):
    course = models.Course.objects(id=course_id).first()
    if not course:
        return redirect(url_for("course.index"))

    enroll_course = models.EnrollCourse.objects(
        course=course, user=current_user._get_current_object()
    ).first()

    contents = models.CourseContent.objects(course=course_id, status="active").order_by(
        "index"
    )

    if not enroll_course:
        return redirect(url_for("course.index"))

    # when enter from dashboard or course detail, page_id is None
    if page_id is None:
        page_id = enroll_course.index

    # remember the last page visited
    if page_id is not None:
        enroll_course.index = int(page_id)
        enroll_course.save()

    print("Page ID:", page_id)
    current_content = models.CourseContent.objects(
        course=course_id, index=page_id
    ).first()
    
    print("\n\nCurrent Content:", current_content)
    print("============")
    form = forms.courses.CourseContentForm(obj=current_content)

    if not current_content:
        return redirect(url_for("course.course_detail", course_id=course_id))

    if current_content.header_image:
        current_content.header_image_url = url_for(
            "media.download",
            media_id=current_content.header_image.id,
            filename=current_content.header_image.file.filename,
        )
    else:
        current_content.header_image_url = "/static/images/example-course-thumbnail.jpg"
    return render_template(
        "courses/content.html",
        course_id=course_id,
        page_id=page_id,
        course=course,
        contents=contents,
        current_content=current_content,
        form=form,
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


@module.route(
    "/<course_id>/course_refs/<page_id>/submit_challenge",
    methods=["GET", "POST"],
)
@login_required
def submit_question(course_id, page_id):
    current_content = models.CourseContent.objects(
        course=course_id, index=page_id
    ).first()

    if current_content.type != "question":
        return redirect(
            url_for(
                "course.course_content",
                course_id=course_id,
                page_id=page_id,
                dialog_state="fail",
            )
        )
    course = models.Course.objects(id=course_id).first()
    success_transaction = models.TransactionCourse.objects(
        course=course,
        course_content=current_content,
        result="success",
        type="question",
    ).first()

    if success_transaction:
        return redirect(
            url_for("course.course_content", course_id=course_id, page_id=page_id)
        )

    answer = request.args.get("answer")

    if not success_transaction:
        transaction = models.TransactionCourse()
        transaction.type = "question"
        transaction.course = course
        transaction.course_question = current_content.course_question
        transaction.course_content = current_content
        transaction.created_by = current_user
        if answer == current_content.course_question.answer:
            transaction.exp_ = current_content.exp_
            transaction.result = "failed"
            transaction.save()
        else:
            transaction.result = "success"
            transaction.save()
            return redirect(
                url_for(
                    "course.course_content",
                    course_id=course.id,
                    page_id=page_id,
                    dialog_state="fail",
                )
            )

    return redirect(
        url_for(
            "course.course_content",
            course_id=course.id,
            page_id=page_id,
            dialog_state="success",
        )
    )


@module.route("/<course_id>/complete/<page_id>", methods=["GET"])
@login_required
def complete_content(course_id, page_id):
    current_content = models.CourseContent.objects(
        course=course_id, index=page_id
    ).first()

    if not current_content:
        return redirect(url_for("course.course_detail", course_id=course_id))

    next_content_number = int(page_id) + 1

    if current_content.type != "section":
        return redirect(
            url_for(
                "course.course_content",
                course_id=course_id,
                page_id=next_content_number,
            )
        )

    course = models.Course.objects(id=course_id).first()
    transaction = models.TransactionCourse(
        type="section",
        course=course,
        course_content=current_content,
        created_by=current_user,
        exp_=current_content.exp_,
        result="success",
    )
    transaction.save()

    return redirect(
        url_for(
            "course.course_content", course_id=course.id, page_id=next_content_number
        )
    )
