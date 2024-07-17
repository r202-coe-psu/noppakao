import datetime
import mongoengine as me

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    Response,
    send_file,
    redirect,
)

from flask_login import login_user, logout_user, login_required, current_user

from noppakao.web import oauth, forms, models, acl

module = Blueprint("events", __name__, url_prefix="/events")


@module.route("/", methods=["GET", "POST"])
@acl.roles_required("admin")
def index():
    events = models.Event.objects()
    return render_template("/admin/events/index.html", events=events)


@module.route("/create", methods=["GET", "POST"], defaults={"event_id": None})
@module.route("<event_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit(event_id):
    form = forms.events.EventForm()
    event = models.Event()

    if event_id:
        event = models.events.Event.objects(id=event_id).first()
        form = forms.events.EventForm(obj=event)

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/admin/events/create_or_edit.html", form=form)

    form.populate_obj(event)

    if not event_id:
        event.created_by = current_user._get_current_object()

    event.updated_date = datetime.datetime.now()
    event.updated_by = current_user._get_current_object()
    event.save()

    return redirect(url_for("admin.events.index"))
