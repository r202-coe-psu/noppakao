from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from noppakao import models

BaseTeamsForm = model_form(
    models.Team,
    FlaskForm,
    exclude=[
        "created_by",
        "created_date",
        "last_updated_by",
        "updated_date",
        "score",
        "status",
    ],
    field_args={"name": {"label": "Team name"}},
)


class TeamsForm(BaseTeamsForm):
    picture = file.FileField(
        "Upload team image (.jpg or .png)",
        validators=[
            file.FileAllowed(["png", "jpg", "jpeg"], "You can use only jpg , png"),
        ],
    )
    members = fields.SelectMultipleField("Members")
