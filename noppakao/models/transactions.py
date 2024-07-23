import mongoengine as me
import datetime
from flask_login import UserMixin

TRANSACTION_TYPE = [
    "hint",
    "answer",
]

TRANSACTION_STATUS = [
    "first_blood",
    "success",
    "fail",
]


class Transaction(me.Document):
    meta = {"collection": "transactions"}

    type = me.StringField(choices=TRANSACTION_TYPE, required=True)
    status = me.StringField(choices=TRANSACTION_STATUS, default="fail", required=True)

    score = me.IntField(required=True)
    event = me.ReferenceField("Event", required=True)
    event_challenge = me.ReferenceField("EventChallenge", required=True)

    answer = me.StringField(required=True)
    team = me.ReferenceField("Team")
    user = me.ReferenceField("User", required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
