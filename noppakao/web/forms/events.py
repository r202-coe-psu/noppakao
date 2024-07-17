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
