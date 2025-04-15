from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators, DateTimeField


from noppakao import models

BaseEventForm = model_form(
    models.Event,
    FlaskForm,
    exclude=["created_date", "created_by", "updated_date", "updated_by"],
    field_args={
        "code": {"label": "Code"},
        "name": {"label": "Name"},
        "description": {"label": "Description"},
        "flag_prefix": {"label": "Flag Prefix"},
    },
)


class EventForm(BaseEventForm):
    type = fields.SelectField("เลือกประเภท", choices=models.events.EVENT_TYPE)
    status = fields.SelectField("Status", choices=models.events.STATUS_CHOICES)

    publish_started_date = fields.DateTimeField(
        "Publish Start Date",
        validators=[validators.Optional()],
        format="%d-%m-%Y %H:%M:%S",
        widget=widgets.TextInput(),
    )
    publish_ended_date = fields.DateTimeField(
        "Publish End Date",
        validators=[validators.Optional()],
        format="%d-%m-%Y %H:%M:%S",
        widget=widgets.TextInput(),
    )

    register_started_date = fields.DateTimeField(
        "Register Started Date",
        validators=[validators.Optional()],
        format="%d-%m-%Y %H:%M:%S",
        widget=widgets.TextInput(),
    )

    register_ended_date = fields.DateTimeField(
        "Register End Date",
        validators=[validators.Optional()],
        format="%d-%m-%Y %H:%M:%S",
        widget=widgets.TextInput(),
    )

    started_date = fields.DateTimeField(
        "Started Date",
        validators=[validators.Optional()],
        format="%d-%m-%Y %H:%M:%S",
        widget=widgets.TextInput(),
    )

    ended_date = fields.DateTimeField(
        "Ended Date",
        validators=[validators.Optional()],
        format="%d-%m-%Y %H:%M:%S",
        widget=widgets.TextInput(),
    )


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


class MultipleChallengesForm(FlaskForm):
    challenges = fields.SelectMultipleField(
        "เลือก Challenge",
        coerce=str,  # แก้จาก int → str
    )
