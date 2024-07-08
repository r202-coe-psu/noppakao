import datetime
import mongoengine as me
from . import paginations


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
from noppakao.utils import updater_info
from mongoengine.queryset.visitor import Q

module = Blueprint("categories", __name__, url_prefix="/categories")


@module.route("/")
@login_required
def index():
    categories = models.Category.objects().order_by("status")
    return render_template("/categories/index.html", categories=categories)


@module.route(
    "/create",
    methods=["GET", "POST"],
    defaults={"category_id": None},
)
@module.route("/<category_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(category_id):
    form = forms.categories.CategoryForm()
    categories = models.Category.objects()

    if category_id:
        categories = models.Category.objects.get(id=category_id)
        form = forms.categories.CategoryForm(obj=categories)
        categories.update_info.append(
            updater_info.create_update_information(current_user, request, "updated")
        )

    if not form.validate_on_submit():
        return render_template(
            "/categories/create-edit.html",
            form=form,
            categories=categories,
        )

    if not category_id:
        categories = models.Category(
            created_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )
        categories.update_info.append(
            updater_info.create_update_information(current_user, request, "created")
        )

    form.populate_obj(categories)
    categories.last_updated_by = current_user._get_current_object()
    categories.save()
    return redirect(
        url_for("categories.index"),
    )


@module.route("/<category_id>/delete", methods=["GET", "POST"])
@login_required
def delete(category_id):
    categories = models.Category.objects.get(id=category_id)
    categories.status = "disactive"
    categories.update_info.append(
        updater_info.create_update_information(current_user, request, "deleted")
    )
    categories.save()
    return redirect(
        url_for("categories.index"),
    )
