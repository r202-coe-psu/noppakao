import mongoengine as me
import datetime

STATUS_CHOICES = ["active", "disactive"]

EVENT_TYPE = ["solo", "team"]


class Event(me.Document):
    meta = {"collection": "events"}  # ตั้งชื่อ collection

    code = me.StringField(required=True, unique=True)
    name = me.StringField(required=True, max_length=256)  # หัวข้อโจทย์
    description = me.StringField()  # รายละเอียด
    type = me.StringField(required=True, choices=EVENT_TYPE, default="solo")

    flag_prefix = me.StringField(required=True)

    started_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    ended_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    status = me.StringField(default="active", choices=STATUS_CHOICES)  # บอกถึงสถานะ
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต


class EventCompetitor(me.Document):
    meta = {"collection": "event_competitor"}
    event = me.ReferenceField("Event", dbref=True, required=True)

    team = me.ReferenceField("Team", dbref=True, required=True)

    status = me.StringField(default="active", choices=STATUS_CHOICES)  # บอกถึงสถานะ
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต


class EventChallenge(me.Document):
    event = me.ReferenceField("Event", dbref=True, required=True)
    challenge = me.ReferenceField("Challenge", dbref=True, required=True)

    first_blood_score = me.IntField(required=True, default=0, min=0)
    success_score = me.IntField(required=True, default=0, min=0)

    hint_score = me.IntField(required=True, default=0, max=0)  # ใส่ค่าติดลบไปเลย
    fail_score = me.IntField(required=True, default=0, max=0)  # ใส่ค่าติดลบไปเลย

    status = me.StringField(
        default="active", choices=STATUS_CHOICES, required=True
    )  # บอกถึงสถานะ
    created_by = me.ReferenceField("User", dbref=True, required=True)
    created_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_by = me.ReferenceField("User", dbref=True, required=True)


EVENT_ROLES = ["competitor", "contributor"]


class EventRole(me.Document):
    role = me.StringField(choices=EVENT_ROLES, default="competitor", required=True)
    event = me.ReferenceField("Event", dbref=True, required=True)
    user = me.ReferenceField("User", dbref=True, required=True)

    status = me.StringField(
        default="active", choices=STATUS_CHOICES, required=True
    )  # บอกถึงสถานะ
    created_by = me.ReferenceField("User", dbref=True, required=True)
    created_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_by = me.ReferenceField("User", dbref=True, required=True)
