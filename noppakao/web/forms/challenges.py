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
        "hard_level": {"label": "Hard Level"},
        "challenge_url": {
            "label": "Challenge URL",
            "render_kw": {
                "placeholder": "Challenge URL",
            },
        },
    },
)


class ChallengeForm(BaseChallengeForm):
    uploaded_file = file.MultipleFileField(
        "File type (.zip)",
        validators=[],
    )
    category = fields.SelectField("Category", validators=[validators.InputRequired()])


class ChallengeSearchForm(FlaskForm):
    class Meta:
        csrf = False  # เป็นฟอร์มค้นหาแบบ GET ไม่ต้องใช้ csrf

    search = fields.StringField(
        "Challenge Name",
        render_kw={"placeholder": "Search challenge name"},
    )
    category = fields.SelectField("Type", choices=[], validate_choice=False)


class UploadChallengeFileForm(FlaskForm):
    uploaded_file = file.MultipleFileField(
        "File type (.zip)",
        validators=[],
    )
