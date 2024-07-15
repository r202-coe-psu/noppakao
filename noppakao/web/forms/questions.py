from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from noppakao import models

BaseQuestionForm = model_form(
    models.Question,
    FlaskForm,
    exclude=[
        "question_file",
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
        "question_url": {
            "label": "Question URL",
            "render_kw": {
                "placeholder": "Question URL",
            },
        },
    },
)


class QuestionForm(BaseQuestionForm):
    uploaded_file = file.FileField(
        "File type (.zip)",
        validators=[],
    )
    category = fields.SelectField("Category", validators=[validators.InputRequired()])
