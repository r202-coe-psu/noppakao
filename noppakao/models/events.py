import mongoengine as me
import datetime
from bson import ObjectId

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

    register_started_date = me.DateTimeField(
        required=True, default=datetime.datetime.now
    )
    register_ended_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    publish_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    status = me.StringField(default="active", choices=STATUS_CHOICES)  # บอกถึงสถานะ
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต

    def get_challenge_categories(self):
        from . import categories

        event_challenges = EventChallenge.objects(event=self, status="active")
        event_categories = []
        for event_challenge in event_challenges:
            if event_challenge.challenge.category not in event_categories:
                event_categories.append(event_challenge.challenge.category)

        return event_categories

    def get_event_challenges(self, category):
        from . import challenges

        challenges_in_category = challenges.Challenge.objects(category=category)

        event_challenges = EventChallenge.objects(
            event=self, status="active", challenge__in=challenges_in_category
        )

        return event_challenges

    def team_rank(self):
        from noppakao import models

        team = models.Team.objects(members__in=[current_user], status="active").first()
        pipeline = [
            {"$match": {"event": ObjectId(self.id)}},
            {
                "$group": {
                    "_id": {
                        "team": "$team",
                    },
                    "score": {"$sum": "$score"},
                    "created_date": {"$max": "$created_date"},
                }
            },
            {"$sort": {"created_date": 1}},
            {
                "$setWindowFields": {
                    "partitionBy": "$team",
                    "sortBy": {"score": -1},
                    "output": {"rankScoreForTeam": {"$rank": {}}},
                }
            },
            {"$match": {"_id.team": ObjectId(team.id)}},
            {
                "$project": {
                    "_id": 0,
                    "rankScoreForTeam": 1,
                }
            },
        ]
        result = list(models.Transaction.objects.aggregate(pipeline))

        if result:
            return result[0].get("rankScoreForTeam", 0)

        return 0

    def competitor_rank(self):
        from noppakao import models

        pipeline = [
            {"$match": {"event": ObjectId(self.id)}},
            {
                "$group": {
                    "_id": {
                        "user": "$user",
                    },
                    "score": {"$sum": "$score"},
                    "created_date": {"$max": "$created_date"},
                }
            },
            {"$sort": {"created_date": 1}},
            {
                "$setWindowFields": {
                    "partitionBy": "$user",
                    "sortBy": {"score": -1},
                    "output": {"rankScoreForUser": {"$rank": {}}},
                }
            },
            {"$match": {"_id.user": ObjectId(current_user.id)}},
            {
                "$project": {
                    "_id": 0,
                    "rankScoreForUser": 1,
                }
            },
        ]
        result = list(models.Transaction.objects.aggregate(pipeline))

        if result:
            return result[0].get("rankScoreForUser", 0)

        return 0

    def competitor_score(self):
        from noppakao import models

        pipline = [
            {"$match": {"event": ObjectId(self.id), "user": ObjectId(current_user.id)}},
            {
                "$group": {
                    "_id": {
                        "event_challenge": "$event_challenge",
                        "status": "$status",
                    },
                    "score": {"$sum": "$score"},
                }
            },
            {"$group": {"_id": None, "total_score": {"$sum": "$score"}}},
            {
                "$project": {
                    "_id": 0,
                    "total_score": 1,
                }
            },
        ]
        result = list(models.Transaction.objects.aggregate(pipline))
        if result:
            return result[0].get("total_score", 0)

        return 0

    def team_score(self):
        from noppakao import models

        team = models.Team.objects(members__in=[current_user], status="active").first()

        pipeline = [
            {
                "$match": {
                    "event": ObjectId(self.id),
                    "team": ObjectId(team.id),
                    "status": {"$ne": "fail"},
                }
            },
            {
                "$group": {
                    "_id": {
                        "event_challenge": "$event_challenge",
                        "status": "$status",
                        "type": "$type",
                    },
                    "score": {"$max": "$score"},
                }
            },
            {"$group": {"_id": None, "total_score": {"$sum": "$score"}}},
            {
                "$project": {
                    "_id": 0,
                    "total_score": 1,
                }
            },
        ]

        pipeline_fail = [
            {
                "$match": {
                    "event": ObjectId(self.id),
                    "team": ObjectId(team.id),
                    "status": "fail",
                }
            },
            {
                "$group": {
                    "_id": {
                        "event_challenge": "$event_challenge",
                        "status": "$status",
                        "type": "$type",
                    },
                    "score": {"$min": "$score"},
                }
            },
            {"$group": {"_id": None, "total_score": {"$sum": "$score"}}},
            {
                "$project": {
                    "_id": 0,
                    "total_score": 1,
                }
            },
        ]
        result = list(models.Transaction.objects.aggregate(pipeline))
        result_fail = list(models.Transaction.objects.aggregate(pipeline_fail))
        if result and result_fail:
            return result[0].get("total_score", 0) + result_fail[0].get(
                "total_score", 0
            )
        if result:
            return result[0].get("total_score", 0)

        return 0


class EventCompetitor(me.Document):
    meta = {"collection": "event_competitors"}
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
    meta = {"collection": "event_challenges"}
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

        if self.event.type == "team":
            team = models.Team.objects(
                members__in=[current_user], status="active"
            ).first()

            solve_challenges = models.Transaction.objects(
                event_challenge=self,
                status__in=["success", "first_blood"],
                team=team,
            )
        else:
            solve_challenges = models.Transaction.objects(
                event_challenge=self,
                status__in=["success", "first_blood"],
                user=current_user,
            )

        return solve_challenges

    def check_transaction_hint(self, event_id):
        from noppakao import models

        event = models.Event.objects(id=event_id).first()
        if event.type == "team":
            team = models.Team.objects(
                members__in=[current_user], status="active"
            ).first()
            trasaction = models.Transaction.objects(
                event_challenge=self, type="hint", team=team
            ).first()
        else:
            trasaction = models.Transaction.objects(
                event_challenge=self, type="hint", user=current_user
            ).first()

        return trasaction


EVENT_ROLES = ["competitor", "contributor"]


class EventRole(me.Document):
    meta = {"collection": "event_roles"}
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
