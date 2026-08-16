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


from noppakao.web import forms, models, acl, oauth2
from noppakao.utils import updater_info
from mongoengine.queryset.visitor import Q

module = Blueprint("categories", __name__, url_prefix="/categories")


@module.route("/")
@acl.roles_required("admin")
def index():
    form = forms.categories.SearchCategoryForm(request.args)
    form.status.choices = [("", "All")] + [
        ("active", "Active"),
        ("disactive", "Disactive"),
    ]
    query = {}
    if form.status.data:
        query["status"] = form.status.data
    categories = models.Category.objects(**query).order_by("status")
    if form.name.data:
        categories = categories.filter(name__icontains=form.name.data)
    return render_template(
        "/admin/categories/index.html", categories=categories, form=form
    )


@module.route(
    "/create",
    methods=["GET", "POST"],
    defaults={"category_id": None},
)
@module.route("/<category_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit(category_id):
    form = forms.categories.CategoryForm()
    categories = models.Category.objects()

    if category_id:
        categories = models.Category.objects.get(id=category_id)
        form = forms.categories.CategoryForm(obj=categories)

    if not form.validate_on_submit():
        print(form.errors)
        return render_template(
            "/admin/categories/create-edit.html",
            form=form,
            categories=categories,
        )

    if not category_id:
        categories = models.Category(
            created_by=current_user._get_current_object(),
            updated_by=current_user._get_current_object(),
        )

    form.populate_obj(categories)
    categories.updated_by = current_user._get_current_object()
    categories.save()
    return redirect(
        url_for("admin.categories.index"),
    )


@module.route("/<category_id>/delete", methods=["GET", "POST"])
@acl.roles_required("admin")
def delete(category_id):
    categories = models.Category.objects.get(id=category_id)
    categories.status = "disactive"
    categories.save()
    return redirect(
        url_for("admin.categories.index"),
    )
