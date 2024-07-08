import mongoengine as me
import datetime

from flask import url_for

STATUS_CHOICES = [
    "active",
    "disactive"
]
class Team(me.Document):
    meta = {"collection": "teams"}

    name = me.StringField(required=True, max_length=255)
    organization = me.StringField()
    picture = me.FileField()

    score = me.IntField(required=True, default=0)
    members = me.ListField(me.ReferenceField("User", dbref=True))

    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)
    created_by = me.ReferenceField("User", dbref=True, require=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_by = me.ReferenceField("User", dbref=True, require=True)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def get_picture(self):
        if self.picture:
            return url_for(
                "teams.get_image",
                team_id=self.id,
            )
        else:
            pass
