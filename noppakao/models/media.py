import datetime

import mongoengine as me


class Media(me.Document):
    meta = {"collection": "media"}
    file = me.FileField(required=True, collection_name="media")
    name = me.StringField(required=True)
    type = me.StringField(required=True, choices=["image", "file"])
    ticket = me.ReferenceField("Ticket", dbref=True)
    breach = me.ReferenceField("DataBreach", dbref=True)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    is_encrypted = me.BooleanField(default=False)
    ip_address = me.StringField(default="0.0.0.0")

    owner = me.ReferenceField("User", dbref=True)
    status = me.StringField(required=True, default="active")
