import mongoengine as me
import datetime
from flask_login import UserMixin

TRANSCATION_TYPE = [
    "hint",
    "first_blood",
    "success",
    "fail",
]

class Transaction(me.Document):
    meta = {"collection": "transactions"}
    
    type = me.StringField(choices=TRANSCATION_TYPE, required=True)
    score = me.IntField(required=True)
    event_question = me.ReferenceField("EventQuestion", required=True)

    answer = me.StringField(required=True)
    team = me.ReferenceField("Team")
    user = me.ReferenceField("User", required=True)
    
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)


