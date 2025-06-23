import datetime
from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
)
from flask_login import login_user, logout_user, login_required, current_user
from noppakao.web import acl, forms, models

module = Blueprint("courses", __name__, url_prefix="/courses")


@module.route("/", methods=["GET"])
@acl.roles_required("admin")
def index():
    courses = models.Course.objects()
    return render_template(
        "admin/courses/index.html",
        courses=courses,
    )


""" Course Management """


@module.route("/<course_id>", methods=["GET"])
@acl.roles_required("admin")
def course_detail(course_id):
    return render_template(
        "admin/courses/course_detail.html",
        course_id=course_id,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"course_id": None})
@module.route("/<course_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit_course(course_id):
    if course_id:
        course = models.Course.objects(id=course_id).first()
        form = forms.courses.CourseForm(obj=course)

    if not course_id:
        form = forms.courses.CourseForm()
        course = models.Course()
        course.created_by = current_user._get_current_object()

    form.owner.choices = [
        (str(user.id), user.get_fullname())
        for user in models.User.objects(roles__in=["admin"])
    ]

    form.type.choices = [
        (str(course_type.id), course_type.name)
        for course_type in models.CourseType.objects()
    ]

    if not form.validate_on_submit():
        if course_id:
            form.owner.data = str(course.owner.id)
            form.type.data = str(course.type.id)
        return render_template("/admin/courses/create_or_edit.html", form=form)

    course.name = form.name.data
    course.description = form.description.data
    course.owner = models.User.objects.get(id=form.owner.data)
    course.type = models.CourseType.objects.get(id=form.type.data)

    course.updated_by = current_user._get_current_object()
    course.save()
    return redirect(url_for("admin.courses.index"))


""" Course Type Management """


@module.route("/course_type", methods=["GET"])
@acl.roles_required("admin")
def course_type_index():
    course_types = models.CourseType.objects()
    return render_template(
        "/admin/courses/course_type_index.html", course_types=course_types
    )


@module.route("/course_type/create", methods=["GET", "POST"])
@module.route("/course_type/<course_type_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit_course_type(course_type_id=None):
    if course_type_id:
        course_type = models.CourseType.objects(id=course_type_id).first()
        form = forms.courses.CourseTypeForm(obj=course_type)

    if not course_type_id:
        course_type = models.CourseType()
        course_type.created_by = current_user._get_current_object()
        form = forms.courses.CourseTypeForm()

    if not form.validate_on_submit():
        return render_template(
            "/admin/courses/create_or_edit_course_type.html", form=form
        )

    form.populate_obj(course_type)

    duplicate_course_type = models.CourseType.objects(name=course_type.name).first()
    if duplicate_course_type:
        print("Duplicate course type exists")
        return render_template(
            "/admin/courses/create_or_edit_course_type.html", form=form
        )

    course_type.updated_by = current_user._get_current_object()
    course_type.save()
    return redirect(url_for("admin.courses.course_type_index"))


@module.route("/course_type/<course_type_id>/delete", methods=["POST"])
@acl.roles_required("admin")
def delete_course_type(course_type_id):
    course_type = models.CourseType.objects(id=course_type_id).first()
    if not course_type:
        return redirect(url_for("admin.courses.course_type_index"))

    if course_type.status == "active":
        course_type.status = "disactive"
    else:
        course_type.status = "active"

    course_type.updated_by = current_user._get_current_object()
    course_type.save()
    return redirect(url_for("admin.courses.course_type_index"))


""" Course Content Management """


@module.route("/<course_id>/", methods=["GET"])
@acl.roles_required("admin")
def view(course_id):
    course = models.Course.objects(id=course_id).first()
    sections = models.CourseSection.objects(course=course)
    questions = models.CourseQuestion.objects(course=course)

    contents = list(sections) + list(questions)

    if not course:
        return redirect(url_for("admin.courses.index"))

    return render_template(
        "admin/courses/view.html",
        course=course,
        contents=contents,
    )


@module.route("/<course_id>/section/create", methods=["GET", "POST"])
@module.route("/<course_id>/section/<section_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit_course_section(course_id, section_id=None):
    course = models.Course.objects(id=course_id).first()
    if not course:
        return redirect(url_for("admin.courses.index"))

    if section_id:
        section = models.CourseSection.objects(id=section_id).first()
        form = forms.courses.CourseSectionForm(obj=section)

    if not section_id:
        section = models.CourseSection()
        section.created_by = current_user._get_current_object()
        form = forms.courses.CourseSectionForm()

    if not form.validate_on_submit():
        print(form.errors)
        return render_template(
            "/admin/courses/create_or_edit_course_section.html", form=form
        )

    print("Form data:", request.form)

    section.course = course
    section.header = form.header.data
    section.header_description = form.header_description.data
    section.exp_ = form.exp_.data
    section.content = form.content.data
    section.created_by = current_user._get_current_object()
    section.updated_by = current_user._get_current_object()
    section.save()

    return redirect(url_for("admin.courses.view", course_id=course_id))


@module.route("/<course_id>/section/<section_id>/delete", methods=["POST"])
def delete_course_section(course_id, section_id):
    course = models.Course.objects(id=course_id).first()
    if not course:
        return redirect(url_for("admin.courses.index"))

    section = models.CourseSection.objects(id=section_id).first()
    if not section:
        return redirect(url_for("admin.courses.view", course_id=course_id))

    section.status = "disactive"
    section.updated_by = current_user._get_current_object()
    section.save()
    return redirect(url_for("admin.courses.view", course_id=course_id))


@module.route("/<course_id>/question/create", methods=["GET", "POST"])
@module.route("/<course_id>/question/edit/<question_id>", methods=["GET", "POST"])
def create_or_edit_course_question(course_id, question_id=None):
    course = models.Course.objects(id=course_id).first()
    if not course:
        return redirect(url_for("admin.courses.index"))

    if question_id:
        question = models.CourseQuestion.objects(id=question_id).first()
        form = forms.courses.CourseQuestionForm(obj=question)

    if not question_id:
        question = models.CourseQuestion()
        question.created_by = current_user._get_current_object()
        form = forms.courses.CourseQuestionForm()

    form.course_question.choices = [
        (str(challenge.id), challenge.name) for challenge in models.Challenge.objects()
    ]

    if not form.validate_on_submit():
        print(form.errors)
        return render_template(
            "/admin/courses/create_or_edit_course_question.html", form=form
        )

    question.course = course
    question.course_question = models.Challenge.objects.get(id=form.course_question.data)
    question.exp_ = form.exp_.data
    question.created_by = current_user._get_current_object()
    question.updated_by = current_user._get_current_object()
    question.save()

    return redirect(url_for("admin.courses.view", course_id=course_id))


@module.route("/<course_id>/question/<question_id>/delete", methods=["POST"])
def delete_course_question(course_id, question_id):
    course = models.Course.objects(id=course_id).first()
    if not course:
        return redirect(url_for("admin.courses.index"))

    question = models.CourseQuestion.objects(id=question_id).first()
    if not question:
        return redirect(url_for("admin.courses.view", course_id=course_id))

    question.status = "disactive"
    question.updated_by = current_user._get_current_object()
    question.save()
    return redirect(url_for("admin.courses.view", course_id=course_id))
