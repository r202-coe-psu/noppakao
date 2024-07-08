from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from noppakao import models

BaseUploadDataForm = model_form(
    models.FlagQuestion,
    FlaskForm,
    exclude=[
        "upload_by",
        "upload_file_name",
        "last_updated_by",
        "updated_date",
        "uploaded_date",
        "update_info",
        "problem_solvers",
        "upload_file",
        "status",
    ],
    field_args={
        "problem_header": {"label": "Problem Header"},
        "description": {"label": "Description"},
        "hint": {"label": "Hint"},
        "flag": {"label": "Flag"},
        "point": {"label": "Point"},
    },
)


class UploadDataForm(BaseUploadDataForm):
    uploaded_file = file.FileField(
        "File type (.zip)",
        validators=[
            file.FileAllowed(["zip"], "You can use only zip"),
        ],
    )
    category = fields.SelectField("Category")
