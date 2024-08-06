import mongoengine as me
import datetime
import markdown
import json

from flask import url_for, request


class Organization(me.Document):
    meta = {"collection": "organizations"}

    name = me.StringField(min_length=4, max_length=255, required=True)
    description = me.StringField()
    image = me.ImageField()

    status = me.StringField(required=True, default="active")

    created_by = me.ReferenceField("User", dbref=True)
    last_updated_by = me.ReferenceField("User", dbref=True)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def get_logo_url(self):
        if self.image:
            return url_for(
                "organizations.display_image",
                organization_id=self.id,
                filename=self.image.filename,
            )
        else:
            return url_for("static", filename="images/learning.png")
