import datetime
import mongoengine as me
import os
from mongoengine.queryset.visitor import Q

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
    send_file,
    abort,
)

from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from noppakao.utils import updater_info
from noppakao import models
from noppakao.web import forms
from .. import oauth

from . import paginations

module = Blueprint("upload_data", __name__, url_prefix="/upload_data")


@module.route("/")
@login_required
def index():
    submit_flags = models.Question.objects()
    return render_template("/upload_data/index.html", submit_flags=submit_flags)


@module.route(
    "/upload",
    methods=["GET", "POST"],
    defaults={"submit_flag_id": None},
)
@module.route("/<submit_flag_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(submit_flag_id):
    upload_data = models.Question.objects()
    form = forms.flags.UploadDataForm()
    categories = models.Category.objects(status="active")

    if submit_flag_id:
        upload_data = models.Question.objects.get(id=submit_flag_id)
        form = forms.flags.UploadDataForm(obj=upload_data)
        upload_data.update_info.append(
            updater_info.create_update_information(current_user, request, "updated")
        )

    form.category.choices = [(i.id, i.name) for i in categories]

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/upload_data/create-edit.html", form=form)

    if not submit_flag_id:
        upload_data = models.Question(
            upload_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )
        upload_data.update_info.append(
            updater_info.create_update_information(current_user, request, "created")
        )

    form.populate_obj(upload_data)
    category = models.Category.objects(id=form.category.data).first()
    upload_data.category = category

    if not submit_flag_id:
        if form.uploaded_file.data:
            upload_data.upload_file.put(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )
    else:
        if form.uploaded_file.data:
            upload_data.upload_file.replace(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )

    if form.uploaded_file.data:
        upload_data.upload_file_name = form.uploaded_file.data.filename
    upload_data.flag = generate_password_hash(form.flag.data)
    upload_data.last_updated_by = current_user._get_current_object()
    upload_data.save()

    return redirect(url_for("upload_data.index"))


@module.route("<submit_flag_id>/delete", methods=["GET", "POST"])
@login_required
def delete(submit_flag_id):
    submit_flag = models.Question.objects.get(id=submit_flag_id)
    submit_flag.delete()
    return redirect(url_for("upload_data.index"))


@module.route("<upload_data_id>/download_file", methods=["GET", "POST"])
@login_required
def download(upload_data_id):
    upload_data = models.Upload_data.objects(id=upload_data_id)
    try:
        upload_data = models.Upload_data.objects(
            id=upload_data_id, status="active"
        ).first()
    except:
        return abort(404)

    res = send_file(
        upload_data.upload_file,
        download_name=upload_data.upload_file.filename,
        mimetype=upload_data.upload_file.content_type,
    )
    return res
