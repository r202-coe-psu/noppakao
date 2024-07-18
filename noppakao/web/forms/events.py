from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from noppakao import models

BaseEventForm = model_form(
    models.Event,
    FlaskForm,
    exclude=["status", "created_date", "created_by", "updated_date", "updated_by"],
    field_args={
        "code": {"label": "Code"},
        "name": {"label": "Name"},
        "description": {"label": "Description"},
        "flag_prefix": {"label": "Flag Prefix"},
        "started_date": {"label": "Start Date"},
        "ended_date": {"label": "End Date"},
    },
)


class EventForm(BaseEventForm):
    type = fields.SelectField("เลือกประเภท", choices=models.events.EVENT_TYPE)


BaseEventChallengeForm = model_form(
    models.EventChallenge,
    FlaskForm,
    exclude=[
        "event",
        "status",
        "created_by",
        "created_date",
        "updated_date",
        "updated_by",
    ],
    field_args={
        "first_blood_score": {"label": "First Blood Score"},
        "success_score": {"label": "Score"},
        "hint_score": {"label": "Hint Score"},
        "fail_score": {"label": "Failure Score"},
    },
)


class EventChallengeForm(BaseEventChallengeForm):
    challenge = fields.SelectField("Challenge")


BaseEventRole = model_form(
    models.EventRole,
    FlaskForm,
    exclude=[
        "event",
        "status",
        "created_by",
        "created_date",
        "updated_date",
        "updated_by",
    ],
)


class EventRoleForm(BaseEventRole):
    user = fields.SelectField(
        "User",
    )
    role = fields.SelectField("Role", choices=models.events.EVENT_ROLES)
