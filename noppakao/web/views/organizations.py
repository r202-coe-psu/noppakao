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
from .. import forms, acl, oauth

module = Blueprint("organizations", __name__, url_prefix="/organizations")


@module.route("/information", methods=["GET", "POST"])
@login_required
def information():
    error = request.args.get("error")
    return render_template("organizations/information.html", error=error)


@module.route("/change", methods=["GET", "POST"])
@login_required
def change():
    form = forms.organizations.ChangeOrganizationForm()
    form.organization.choices = [
        (f"{organization.id}", f"{organization.name}")
        for organization in models.Organization.objects(status="active")
    ]
    if not form.validate_on_submit():
        if current_user.organization:
            form.organization.data = str(current_user.organization.id)
        print(form.errors)
        return render_template("organizations/change.html", form=form)

    user = current_user
    user.organization = models.Organization.objects(id=form.organization.data).first()
    user.save()
    return redirect(url_for("organizations.information"))


@module.route("/<organization_id>/logo_image/<filename>", methods=["GET", "POST"])
@login_required
def display_image(organization_id, filename):
    organization = models.Organization.objects(id=organization_id).first()
    response = send_file(
        organization.image,
        download_name=organization.image.filename,
        mimetype=organization.image.content_type,
    )
    return response
