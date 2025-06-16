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

module = Blueprint("course", __name__, url_prefix="/course")


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


@module.route("/create", methods=["GET", "POST"], defaults={"course_id": None} )
@module.route("/<course_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit_course(course_id):
    form = forms.courses.CourseForm()
    if course_id:
        course = models.Course.objects(id=course_id).first()
        form = forms.courses.CourseForm(obj=course)

    if not course_id:
        course = models.Course()
        course.created_by = current_user._get_current_object()
    
    if not form.validate_on_submit():
        return render_template("/admin/events/create_or_edit.html", form=form)

    form.populate_obj(course)

    course.updated_by = current_user._get_current_object()
    course.save()
    return redirect(url_for("admin.course.index"))



    