import mongoengine as me
import datetime
from flask_login import UserMixin, current_user


class Organization(me.Document):
    meta = {"collection": "organizations"}
    name = me.StringField(required=True)
    logo = me.ImageField()
    provice = me.StringField()


class User(me.Document, UserMixin):
    meta = {"collection": "users"}

    display_name = me.StringField(default="", max_length=255)
    first_name = me.StringField(required=True, max_length=128)
    last_name = me.StringField(required=True, max_length=128)

    username = me.StringField(required=True, unique=True, max_length=64)
    password = me.BinaryField(required=True)
    email = me.StringField(required=True, unique=True)
    phone_number = me.StringField(max_length=10, default="")
    status = me.StringField(default="active")
    roles = me.ListField(me.StringField(), default=["user"])
    organization = me.ReferenceField("Organization", dbref=True)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    last_login_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def check_team_event(self, event_id):
        from noppakao import models

        event = models.Event.objects(id=event_id).first()
        team = models.Team.objects(event=event, members__in=[self]).first()
        if team:
            return True

        return None

    def check_join_event(self, event_id):
        from noppakao import models

        event = models.Event.objects(id=event_id).first()
        event_role = models.EventRole.objects(user=self, event=event).first()
        if event_role:
            return True

        return None

    def set_password(self, password):
        from werkzeug.security import generate_password_hash

        self.password = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash

        if check_password_hash(self.password, password):
            return True
        return False

    def check_roles(self, roles: list):
        if set(roles) & set(self.roles):
            return True
        return False

    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def has_roles(self, *roles):
        for role in roles:
            if role in self.roles:
                return True
        return
