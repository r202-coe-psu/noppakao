from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators, DateTimeField


from noppakao import models

BaseCourseForm = model_form(
    models.Course,
    FlaskForm,
    exclude=["created_date", "created_by", "updated_date", "updated_by", "status"],
    field_args={
        "name": {"label": "ชื่อ Course"},
        "description": {"label": "รายละเอียด"},
        "level": {"label": "ระดับ"},
        "owner": {"label": "เจ้าของ Course"},
        "type": {"label": "ประเภท Course"},
    },
)

BaseCourseTypeForm = model_form(
    models.CourseType,
    FlaskForm,
    exclude=["created_date", "updated_date", "status"],
    field_args={
        "name": {"label": "ชื่อประเภท Course"},
    },
)

BaseCourseSectionForm = model_form(
    models.CourseContent,
    FlaskForm,
    exclude=[
        "create_date",
        "created_by",
        "updated_date",
        "updated_by",
        "status",
        "course",
        "index",
        "type",
        "course_question",
    ],
    field_args={
        "header": {"label": "หัวข้อ Section"},
        "header_description": {"label": "รายละเอียด Section"},
        "exp_": {"label": "ประสบการณ์ที่ได้รับ"},
        "content": {"label": "เนื้อหา"},
    },
)

BaseCourseQuestionForm = model_form(
    models.CourseContent,
    FlaskForm,
    exclude=[
        "create_date",
        "created_by",
        "updated_date",
        "updated_by",
        "status",
        "course",
        "index",
        "type",
        "content",
    ],
    field_args={
        "course_question": {"label": "คำถาม"},
        "exp_": {"label": "ประสบการณ์ที่ได้รับ"},
    },
)


class CourseForm(BaseCourseForm):
    name = fields.StringField("ชื่อ Course", validators=[validators.DataRequired()])
    description = fields.TextAreaField(
        "รายละเอียด", validators=[validators.DataRequired()]
    )
    level = fields.StringField("ระดับ", validators=[validators.DataRequired()])
    owner = fields.SelectField(
        "เจ้าของ Course", coerce=str, validators=[validators.DataRequired()]
    )
    type = fields.SelectField(
        "ประเภท Course", coerce=str, validators=[validators.DataRequired()]
    )


class CourseTypeForm(BaseCourseTypeForm):
    name = fields.StringField("ชื่อประเภท Course", validators=[validators.DataRequired()])


class CourseSectionForm(BaseCourseSectionForm):
    header = fields.StringField("หัวข้อ Section", validators=[validators.DataRequired()])
    header_description = fields.TextAreaField(
        "รายละเอียด Section", validators=[validators.DataRequired()]
    )
    exp_ = fields.IntegerField("ประสบการณ์ที่ได้รับ", validators=[validators.DataRequired()])
    content = fields.StringField("เนื้อหา")

class CourseQuestionForm(BaseCourseQuestionForm):
    header = fields.StringField("หัวข้อคำถาม", validators=[validators.DataRequired()])
    header_description = fields.TextAreaField(
        "รายละเอียดคำถาม", validators=[validators.DataRequired()]
    )
    course_question = fields.SelectField(
        "คำถาม",
        validators=[validators.DataRequired()],
    )
    exp_ = fields.IntegerField("ประสบการณ์ที่ได้รับ", validators=[validators.DataRequired()])