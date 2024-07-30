from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from noppakao import models

BaseOrganizationForm = model_form(
    models.Organization,
    FlaskForm,
    exclude=[
        "created_by",
        "created_date",
        "updated_date",
        "last_updated_by",
        "status",
        "image",
    ],
    field_args={
        "name": {
            "label": "Organization Name",
        },
        "description": {
            "label": "Description",
        },
    },
)


class OrganizationForm(BaseOrganizationForm):
    uploaded_image = fields.FileField(
        "Image file (.png , .jpg , .jpeg)",
        validators=[
            file.FileAllowed(["jpg", "png", "jpeg"], "Images only!"),
        ],
    )


class ChangeOrganizationForm(FlaskForm):
    organization = fields.SelectField(
        "Organization", validators=[validators.InputRequired()]
    )
