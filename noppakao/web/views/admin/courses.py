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

module = Blueprint("course", __name__, url_prefix="/courses")


@module.route("/", methods=["GET"])
@acl.roles_required("admin")
def index():
    return render_template(
        "admin/courses/index.html",
    )


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
    form = forms.courses.CourseForm()
    form.owner.choices = [
        (str(user.id), user.get_fullname())
        for user in models.User.objects(roles__in=["admin"])
    ]

    form.type.choices = [
        (str(course_type.id), course_type.name)
        for course_type in models.CourseType.objects()
    ]

    if course_id:
        course = models.Course.objects(id=course_id).first()
        form = forms.courses.CourseForm(obj=course)

    if not course_id:
        course = models.Course()
        course.created_by = current_user._get_current_object()

    if not form.validate_on_submit():
        return render_template("/admin/courses/create_or_edit.html", form=form)

    form.populate_obj(course)

    course.updated_by = current_user._get_current_object()
    course.save()
    return redirect(url_for("admin.courses.index"))


@module.route("/course_type/create", methods=["GET", "POST"])
@module.route("/course_type/<course_type_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit_course_type(course_type_id=None):
    form = forms.courses.CourseTypeForm()
    if course_type_id:
        course_type = models.CourseType.objects(id=course_type_id).first()
        form = forms.courses.CourseTypeForm(obj=course_type)

    if not course_type_id:
        course_type = models.CourseType()
        course_type.created_by = current_user._get_current_object()

    if not form.validate_on_submit():
        print(form.errors)
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
    return redirect(url_for("admin.course.index"))
