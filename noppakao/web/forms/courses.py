from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators, DateTimeField


from noppakao import models 

BaseCourseForm = model_form(
    models.Course,
    FlaskForm,
    exclude=["created_date", "created_by", "updated_date", "updated_by"],
    field_args={
        "name": {"label": "ชื่อ Course"},
        "description": {"label": "รายละเอียด"},
        "level": {"label": "ระดับ"},
        "owner": {"label": "เจ้าของ Course"},
        "type": {"label": "ประเภท Course"},
    },
)

class CourseForm(BaseCourseForm):
    name = fields.StringField("ชื่อ Course", validators=[validators.DataRequired()])
    description = fields.TextAreaField("รายละเอียด", validators=[validators.DataRequired()])
    level = fields.StringField("ระดับ", validators=[validators.DataRequired()])
    owner = fields.SelectField("เจ้าของ Course", coerce=str, validators=[validators.DataRequired()])
    type = fields.SelectField("ประเภท Course", coerce=str, validators=[validators.DataRequired()])
    
    