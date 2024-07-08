import mongoengine as me
import datetime

from flask import url_for


class Teams(me.Document):
    name = me.StringField(required=True, max_length=50)
    status = me.StringField(default="active")
    picture = me.FileField()
    created_by = me.ReferenceField("User", dbref=True, require=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    last_updated_by = me.ReferenceField("User", dbref=True, require=True)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    score = me.IntField(default=0)
    meta = {"collection": "teams"}

    def get_picture(self):
        if self.picture:
            return url_for(
                "teams.get_image",
                team_id=self.id,
            )
        else:
            pass
