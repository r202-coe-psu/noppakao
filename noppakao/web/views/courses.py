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
from bson import ObjectId

from flask_login import login_user, logout_user, login_required, current_user
from noppakao import models
from noppakao.web import forms
from . import paginations

import datetime
from mongoengine.queryset.visitor import Q

module = Blueprint("course", __name__, url_prefix="/course")

# TODO: Add authentication


@module.route("/", methods=["GET"])
@login_required
def index():
    form = forms.courses.CourseSearchForm()

    form.enrollment.choices = [
        ("all", "All"),
        ("enrolled", "Enrolled"),
        ("not_enrolled", "Not Enrolled"),
    ]


    courses = models.Course.objects(status="active").order_by("name")
    enrolled_courses = models.EnrollCourse.objects(user=current_user)
    enrolled_course_ids = [enrollment.course.id for enrollment in enrolled_courses]
    

    #Filter by name and enrollment status
    name = request.args.get("name", type=str)
    enrollment = request.args.get("enrollment", type=str)
    if name:
        form.name.data = name
        courses = courses.filter(Q(name__icontains=name) | Q(description__icontains=name))
    if enrollment:
        form.enrollment.data = enrollment
        if enrollment == "enrolled":
            courses = courses.filter(id__in=enrolled_course_ids)
        elif enrollment == "not_enrolled":
            courses = courses.filter(Q(id__not__in=enrolled_course_ids))
       
    for course in courses:
        course.is_enrolled = course.id in enrolled_course_ids

    return render_template(
        "courses/index.html",
        form=form,
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

    # Check Enroll
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

    # Get current content
    current_content = models.CourseContent.objects(
        course=course_id, index=page_id
    ).first()

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
        current_content.header_image_url = url_for("static", filename="images/example-course-thumbnail.jpg")


    # check is content completed
    completed_count = 0
    course.total_exp = 0
    course.current_exp = 0
        
    for content in contents:
        course.total_exp += content.exp_
        transaction = models.TransactionCourse.objects(
            course=course,
            course_content=content,
            created_by=current_user._get_current_object(),
            result="success",
        ).first()

        if transaction:
            course.current_exp += content.exp_
            completed_count += 1
            content.is_completed = True
        else:
            content.is_completed = False
            
    # Check if the last content is completed
    # Check if before the last content is completed
    if current_content.index == len(contents) and completed_count == len(contents) - 1:
        transaction = models.TransactionCourse(
            type="section",
            course=course,
            course_content=current_content,
            created_by=current_user._get_current_object(),
            result="success",
        )
        transaction.save()
        contents[current_content.index - 1].is_completed = True
        

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
    enrolled_courses = list(
        models.EnrollCourse.objects(user=current_user, status="active").order_by(
            "-last_accessed"
        )
    )
    for course in enrolled_courses:
        course.total_exp = 0
        course.current_exp = 0
        contents = list(
            models.CourseContent.objects(
                course=course.course.id, status="active"
            ).order_by("index")
        )

        for content in contents:
            course.total_exp += content.exp_

            transaction = models.TransactionCourse.objects(
                course=course.course,
                course_content=content,
                created_by=current_user._get_current_object(),
                result="success",
            ).first()

            if transaction:
                course.current_exp += content.exp_

    user_progress = current_user.get_course_progress()

    return render_template(
        "courses/dashboard.html",
        enrolled_courses=enrolled_courses,
        user_progress=user_progress,
    )


@module.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    users = models.User.objects(status="active", roles__nin=["admin"])
    pagination = paginations.get_paginate(data=users, items_per_page=20)

    pipeline = [
        {
            "$match": {
                "result": "success",
            }
        },
        {
            "$lookup": {
                "from": "course_content",
                "localField": "course_content.$id",
                "foreignField": "_id",
                "as": "course_content_doc",
            }
        },
        {"$unwind": "$course_content_doc"},
        {
            "$group": {
                "_id": "$created_by.$id",
                "total_exp": {"$sum": "$course_content_doc.exp_"},
            }
        },
        {"$sort": {"total_exp": -1}},  # Sort by total_exp in descending order
    ]

    transactions = list(
        models.TransactionCourse.objects(created_by__in=users).aggregate(pipeline)
    )

    users = []
    for transaction in transactions:
        user = models.User.objects(id=transaction["_id"]).first()
        course_progress_user = user.get_course_progress()
        users.append(
            {
                "display_name": user.display_name,
                "level": course_progress_user["level"],
                "percentage": course_progress_user["percentage"],
            }
        )

    pagination = paginations.get_paginate(data=users, items_per_page=20)
    return render_template(
        "courses/leaderboard.html",
        pagination=pagination,
    )


@module.route("/enroll/<course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    course = models.Course.objects.get(id=course_id)
    if not course:
        return redirect(url_for("course.index"))

    if models.EnrollCourse.objects(user=current_user, course=course, status="active"):
        return redirect(url_for("course.index"))

    enroll = models.EnrollCourse(
        user=current_user,
        course=course,
    )
    enroll.save()

    return redirect(url_for("course.index", course_id=course_id))


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
        created_by=current_user._get_current_object(),
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
            transaction.result = "success"
            transaction.save()
        else:
            transaction.result = "failed"
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
    course = models.Course.objects(id=course_id).first()
    current_content = models.CourseContent.objects(
        course=course_id, index=page_id
    ).first()
    
    if not current_content:
        return redirect(url_for("course.course_detail", course_id=course_id))

    next_content_number = int(page_id) + 1

    # Just redirect if type is question
    if current_content.type == "question":
        return redirect(
            url_for(
                "course.course_content",
                course_id=course_id,
                page_id=next_content_number,
            )
        )

    transaction_current_content = models.TransactionCourse.objects(
        course=course,
        course_content=current_content,
        created_by=current_user._get_current_object(),
        result="success",
    ).first()
    # Already completed this section
    if transaction_current_content:
        return redirect(
            url_for(
                "course.course_content",
                course_id=course.id,
                page_id=next_content_number,
            )
        )
    else:
        transaction = models.TransactionCourse(
            type="section",
            course=course,
            course_content=current_content,
            created_by=current_user,
            result="success",
        )
        transaction.save()

    return redirect(
        url_for(
            "course.course_content", course_id=course.id, page_id=next_content_number
        )
    )


@module.route("/<course_id>/image/<filename>")
@login_required
def get_image(course_id, filename=""):
    response = Response()
    response.status_code = 404
    course = models.CourseContent.objects.get(id=course_id)
    if course.header_image:
        response = send_file(
            course.header_image.file,
            download_name=course.header_image.file.filename,
            mimetype=course.header_image.file.content_type,
        )

    return response
