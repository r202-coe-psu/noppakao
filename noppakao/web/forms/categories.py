from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators

import datetime

from noppakao import models

BaseCategoryForm = model_form(
    models.Category,
    FlaskForm,
    exclude=["created_by", "created_date", "updated_by", "updated_date", "status"],
    field_args={"name": {"label": "Name"}},
)


class CategoryForm(BaseCategoryForm):
    pass
