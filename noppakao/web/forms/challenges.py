from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from noppakao import models

BaseChallengeForm = model_form(
    models.Challenge,
    FlaskForm,
    exclude=[
        "challenge_file",
        "status",
        "created_date",
        "created_by",
        "updated_date",
        "updated_by",
    ],
    field_args={
        "name": {
            "label": "Problem",
            "render_kw": {
                "placeholder": "Problem",
            },
        },
        "description": {
            "label": "Description",
            "render_kw": {
                "placeholder": "Description",
            },
        },
        "hint": {
            "label": "Hint",
            "render_kw": {
                "placeholder": "Hint",
            },
        },
        "answer": {
            "label": "Answer",
            "render_kw": {
                "placeholder": "Answer",
            },
        },
        "answer_type": {"label": "Answer Type"},
        "challenge_url": {
            "label": "Challenge URL",
            "render_kw": {
                "placeholder": "Challenge URL",
            },
        },
    },
)


class ChallengeForm(BaseChallengeForm):
    uploaded_file = file.FileField(
        "File type (.zip)",
        validators=[],
    )
    category = fields.SelectField("Category", validators=[validators.InputRequired()])
