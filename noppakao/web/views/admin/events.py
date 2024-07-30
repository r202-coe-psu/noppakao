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
from .. import paginations

from noppakao.web import oauth, forms, models, acl

module = Blueprint("events", __name__, url_prefix="/events")


@module.route("/", methods=["GET", "POST"])
@acl.roles_required("admin")
def index():
    events = models.Event.objects()
    return render_template("/admin/events/index.html", events=events)


@module.route(
    "/<event_id>/event_roles/create",
    methods=["GET", "POST"],
    defaults={"event_role_id": None},
)
@module.route(
    "/<event_id>/event_roles/<event_role_id>/edit",
    methods=["GET", "POST"],
)
@acl.roles_required("admin")
def create_or_edit_event_role(event_id, event_role_id):
    event = models.Event.objects(id=event_id).first()
    form = forms.events.EventRoleForm()
    event_role = models.EventRole()
    users = models.User.objects()

    if event_role_id:
        event_role = models.events.EventRole.objects(id=event_role_id).first()
        form = forms.events.EventRoleForm(obj=event_role)
    form.user.choices = [(str(user.id), user.get_fullname()) for user in users]

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/admin/events/create_or_edit_role.html", form=form)

    form.populate_obj(event_role)

    if not event_role_id:
        event_role.created_by = current_user._get_current_object()
        event_role.event = event

    event_role.user = models.User.objects(id=form.user.data).first()
    event_role.updated_date = datetime.datetime.now()
    event_role.updated_by = current_user._get_current_object()
    event_role.save()

    return redirect(url_for("admin.events.event_role", event_id=event.id))


@module.route("/<event_id>/event_roles", methods=["GET", "POST"])
@acl.roles_required("admin")
def event_role(event_id):
    event = models.Event.objects(id=event_id).first()
    event_roles = models.EventRole.objects(event=event)
    return render_template(
        "/admin/events/event_roles.html", event=event, event_roles=event_roles
    )


@module.route("/<event_id>/challenge", methods=["GET", "POST"])
@acl.roles_required("admin")
def challenge(event_id):

    event = models.Event.objects(id=event_id).first()
    event_challenges = models.EventChallenge.objects(event=event, status="active")
    event_categorys = []

    for event_challenge in event_challenges:
        if not event_challenge.challenge.category in event_categorys:
            event_categorys.append(event_challenge.challenge.category)

    return render_template(
        "/admin/events/challenge.html",
        event_challenges=event_challenges,
        event=event,
        event_categorys=event_categorys,
    )


@module.route(
    "/<event_id>/create",
    methods=["GET", "POST"],
    defaults={"event_challenge_id": None},
)
@module.route(
    "/<event_id>/challenges/<event_challenge_id>/edit", methods=["GET", "POST"]
)
def create_or_edit_challenge(event_id, event_challenge_id):

    event = models.Event.objects(id=event_id).first()
    challenges = models.Challenge.objects()

    form = forms.events.EventChallengeForm()

    if event_challenge_id:
        event_challenge = models.EventChallenge.objects(id=event_challenge_id).first()
        form = forms.events.EventChallengeForm(obj=event_challenge)

    form.challenge.choices = [
        (str(challenge.id), challenge.name) for challenge in challenges
    ]

    if not form.validate_on_submit():
        print(form.errors)
        return render_template(
            "/admin/events/create_event_challenge.html", event=event, form=form
        )
    if not event_challenge_id:
        event_challenge = models.EventChallenge()

    challenge = models.Challenge.objects(id=form.challenge.data).first()

    form.populate_obj(event_challenge)

    event_challenge.challenge = challenge
    event_challenge.event = event
    event_challenge.created_by = current_user._get_current_object()
    event_challenge.updated_by = current_user._get_current_object()
    event_challenge.save()

    return redirect(url_for("admin.events.challenge", event_id=event.id))


@module.route("/create", methods=["GET", "POST"], defaults={"event_id": None})
@module.route("<event_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit(event_id):
    form = forms.events.EventForm()

    if event_id:
        event = models.events.Event.objects(id=event_id).first()
        form = forms.events.EventForm(obj=event)

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/admin/events/create_or_edit.html", form=form)

    if not event_id:
        event = models.Event()
    form.populate_obj(event)

    if not event_id:
        event.created_by = current_user._get_current_object()

    event.updated_date = datetime.datetime.now()
    event.updated_by = current_user._get_current_object()
    event.save()

    return redirect(url_for("admin.events.index"))


@module.route("/<event_challenge_id>/delete", methods=["GET", "POST"])
@acl.roles_required("admin")
def delete_event_challenge(event_challenge_id):
    event_challenge = models.EventChallenge.objects.get(id=event_challenge_id)
    event_challenge.status = "disactive"
    event_challenge.save()
    return redirect(
        url_for("admin.events.challenge", event_id=event_challenge.event.id),
    )


@module.route(
    "/<event_id>/event_challenges/<event_challenge_id>/view_transactions",
    methods=["GET", "POST"],
)
@acl.roles_required("admin")
def view_transactions(event_id, event_challenge_id):
    event = models.Event.objects(id=event_id).first()
    event_challenge = models.EventChallenge.objects(id=event_challenge_id).first()
    transactions = models.Transaction.objects(event_challenge=event_challenge).order_by(
        "-created_date"
    )

    pagination_event_history = paginations.get_paginate(
        data=transactions, items_per_page=4
    )
    print(pagination_event_history)
    return render_template(
        "/admin/events/view_transactions.html",
        event=event,
        event_challenge=event_challenge,
        transactions=pagination_event_history["data"],
        pagination=pagination_event_history,
    )
