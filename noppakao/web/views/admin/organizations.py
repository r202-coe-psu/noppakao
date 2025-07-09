import datetime
import mongoengine as me
from bson import ObjectId

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
    send_file,
)

from flask_login import login_user, logout_user, login_required, current_user

from noppakao import models
from ... import forms, acl, oauth2

module = Blueprint("organizations", __name__, url_prefix="/organizations")


@module.route("/", methods=["GET", "POST"])
@acl.roles_required("admin")
def index():
    organizations = models.Organization.objects(status="active")
    return render_template(
        "admin/organizations/index.html", organizations=organizations
    )


@module.route(
    "/create",
    methods=["GET", "POST"],
    defaults={"organization_id": None},
)
@module.route(
    "/<organization_id>/edit",
    methods=["GET", "POST"],
)
@acl.roles_required("admin")
def create_or_edit(organization_id):
    organization = models.Organization.objects(id=organization_id).first()
    form = forms.organizations.OrganizationForm()

    if not form.validate_on_submit():
        if organization:
            form.name.data = organization.name
            form.description.data = organization.description
        print(form.errors)
        return render_template(
            "/admin/organizations/create_or_edit.html",
            form=form,
            organization=organization,
        )
    if not organization_id:
        organization = models.Organization(
            created_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )

    if form.uploaded_image.data:
        if not organization.image:
            organization.image.put(
                form.uploaded_image.data,
                filename=form.uploaded_image.data.filename,
                content_type=form.uploaded_image.data.content_type,
            )
        else:
            organization.image.replace(
                form.uploaded_image.data,
                filename=form.uploaded_image.data.filename,
                content_type=form.uploaded_image.data.content_type,
            )
    form.populate_obj(organization)
    organization.last_updated_by = current_user._get_current_object()
    organization.save()
    return redirect(url_for("admin.organizations.index"))


@module.route("/<organization_id>/logo_image/<filename>", methods=["GET", "POST"])
@acl.roles_required("admin")
def display_image(organization_id, filename):
    organization = models.Organization.objects(id=organization_id).first()
    response = send_file(
        organization.image,
        download_name=organization.image.filename,
        mimetype=organization.image.content_type,
    )
    return response
