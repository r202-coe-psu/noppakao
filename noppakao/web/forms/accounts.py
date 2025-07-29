from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators
import email_validator

import datetime

from noppakao import models

BaseRegistrationForm = model_form(
    models.User,
    FlaskForm,
    exclude=[
        "created_date",
        "updated_date",
        "last_login_date",
        "roles",
        "organization",
    ],
    field_args={
        "username": {"label": "Username"},
        "first_name": {"label": "Firstname"},
        "last_name": {"label": "Lastname"},
        "display_name": {"label": "Hacker name"},
    },
)


class RegistrationForm(BaseRegistrationForm):
    password = fields.PasswordField(
        "Password",
        validators=[validators.DataRequired(), validators.EqualTo("password")],
    )
    confirm_password = fields.PasswordField(
        validators=[validators.DataRequired(), validators.EqualTo("password")],
    )
    email = fields.StringField(
        "Email", validators=[validators.Email(), validators.DataRequired()]
    )


class UpdateUserForm(BaseRegistrationForm):
    first_name = fields.StringField(
        "Firstname",
        validators=[
            validators.Length(
                min=0,
                max=128,
                message="ความยาวสูงสุดไม่เกิน 128 ตัวอักษร",
            ),
        ],
    )

    last_name = fields.StringField(
        "Lastname",
        validators=[
            validators.Length(
                min=0,
                max=128,
                message="ความยาวสูงสุดไม่เกิน 128 ตัวอักษร",
            ),
        ],
    )

    email = fields.StringField(
        "Email", validators=[validators.Email(), validators.DataRequired()]
    )


class LoginForm(FlaskForm):
    username = fields.StringField("Username", validators=[validators.DataRequired()])
    password = fields.PasswordField(
        "Password",
        validators=[validators.DataRequired()],
    )
    submit = fields.SubmitField("Login")


class SetupPassword(FlaskForm):
    password = fields.PasswordField(
        "New Password", validators=[validators.DataRequired()]
    )
    confirm_password = fields.PasswordField(
        "Confirm Password",
        validators=[
            validators.InputRequired(),
            validators.Length(min=6),
            validators.EqualTo("password", message="รหัสผ่านไม่ตรงกัน"),
        ],
    )


class AccountForm(BaseRegistrationForm):
    password = fields.PasswordField(
        "Password",
        validators=[validators.DataRequired(), validators.EqualTo("password")],
    )
    confirm_password = fields.PasswordField(
        validators=[validators.DataRequired(), validators.EqualTo("password")],
    )
    email = fields.StringField(
        "Email", validators=[validators.Email(), validators.DataRequired()]
    )
    roles = fields.SelectField("Role", choices=[("user", "User"), ("admin", "Admin")])


class SetupUser(FlaskForm):
    organization = fields.SelectField("Organization")
    display_name = fields.StringField(
        "Display Name", validators=[validators.InputRequired()]
    )


class EditUserForm(FlaskForm):
    uploaded_avatar = file.FileField(
        "Upload user image (png or jpg) , Recommended image size: 250(px) x 230(px)",
        validators=[
            file.FileAllowed(["png", "jpg", "jpeg"], "You can use only jpg , png"),
        ],
    )
    display_name = fields.StringField("Display name")
    first_name = fields.StringField("ชื่อ")
    last_name = fields.StringField("นามสกุล")
    organization = fields.SelectField("Organization")
    phone_number = fields.StringField(
        "หมายเลขโทรศัพท์",
        validators=[
            validators.DataRequired(),
            validators.Length(min=10, max=10, message="หมายเลขโทรศัพท์ต้องมี 10 หลัก"),
            validators.Regexp(r"^\d{10}$", message="กรุณากรอกเฉพาะตัวเลข 10 หลักเท่านั้น"),
        ],
    )
