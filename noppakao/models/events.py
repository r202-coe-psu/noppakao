import mongoengine as me
import datetime
from flask_login import current_user

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

    def competitor_score(self):
        from noppakao import models

        transections = models.Transaction.objects(event=self, user=current_user)
        score = 0
        for transection in transections:
            score += transection.score
        return score

    def team_score(self):
        from noppakao import models

        team = models.Team.objects(members__in=[current_user]).first()
        transections = models.Transaction.objects(event=self, team=team)
        score = 0
        for transection in transections:
            score += transection.score
        return score


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

    def check_answer(self, answer):
        from noppakao import models

        if self.challenge.answer_type == "flag":
            flag = self.event.flag_prefix + "{" + self.challenge.answer + "}"
            if answer == flag:
                return True
            else:
                return False
        if answer == self.challenge.answer:
            return True
        return False

    def total_solve_challenge(self):
        from noppakao import models

        solve_challenges = models.Transaction.objects(
            event_challenge=self, status__in=["success", "first_blood"]
        )

        return len(solve_challenges)

    def solve_challenge(self):
        from noppakao import models

        solve_challenges = models.Transaction.objects(
            event_challenge=self,
            status__in=["success", "first_blood"],
            user=current_user,
        )

        return solve_challenges


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
