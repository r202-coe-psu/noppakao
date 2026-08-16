import datetime

import mongoengine as me
from bson import ObjectId
from flask_login import current_user

STATUS_CHOICES = ["active", "disactive"]

EVENT_TYPE = ["solo", "team"]


class Event(me.Document):
    meta = {"collection": "events"}  # ตั้งชื่อ collection

    code = me.StringField(required=True, unique=True, max_length=256)
    name = me.StringField(required=True, max_length=256)  # หัวข้อโจทย์
    description = me.StringField()  # รายละเอียด
    type = me.StringField(required=True, choices=EVENT_TYPE, default="solo")

    flag_prefix = me.StringField(required=True)

    started_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)
    ended_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)

    register_started_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    register_ended_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    publish_started_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    publish_ended_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    status = me.StringField(default="active", choices=STATUS_CHOICES)  # บอกถึงสถานะ
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต

    def get_challenge_ids(self):
        from . import request_cache

        def compute():
            challenge_ids = []
            for event_challenge in EventChallenge.objects(event=self, status="active").only("challenge"):
                challenge_id = request_cache.reference_id(event_challenge._data.get("challenge"))
                if challenge_id and challenge_id not in challenge_ids:
                    challenge_ids.append(challenge_id)

            return challenge_ids

        return request_cache.request_memo(f"challenge-ids:{self.id}", compute)

    def get_challenge_categories(self):
        from . import categories, challenges, request_cache

        def compute():
            challenge_ids = self.get_challenge_ids()
            if not challenge_ids:
                return []

            category_by_challenge = {
                challenge.id: request_cache.reference_id(challenge._data.get("category"))
                for challenge in challenges.Challenge.objects(id__in=challenge_ids).only("category")
            }

            category_ids = []
            for challenge_id in challenge_ids:
                category_id = category_by_challenge.get(challenge_id)
                if category_id and category_id not in category_ids:
                    category_ids.append(category_id)

            found = {category.id: category for category in categories.Category.objects(id__in=category_ids)}
            return [found[i] for i in category_ids if i in found]

        return request_cache.request_memo(f"challenge-categories:{self.id}", compute)

    def get_challenge_resources_map(self):
        from . import challenges, request_cache

        def compute():
            challenge_ids = self.get_challenge_ids()
            if not challenge_ids:
                return {}

            resources = {}
            for resource in challenges.ChallengeResource.objects(challenge__in=challenge_ids, status="active"):
                challenge_id = request_cache.reference_id(resource._data.get("challenge"))
                resources.setdefault(challenge_id, []).append(resource)

            return resources

        return request_cache.request_memo(f"challenge-resources-map:{self.id}", compute)

    def get_all_event_challenges(self):
        from . import request_cache

        def compute():
            return list(EventChallenge.objects(event=self, status="active").select_related(max_depth=1))

        return request_cache.request_memo(f"all-event-challenges:{self.id}", compute)

    def get_event_challenges(self, category):
        from . import request_cache

        category_id = getattr(category, "id", category)

        def compute():
            return [
                event_challenge
                for event_challenge in self.get_all_event_challenges()
                if request_cache.reference_id(getattr(event_challenge.challenge, "_data", {}).get("category")) == category_id
            ]

        return request_cache.request_memo(f"event-challenges:{self.id}:{category_id}", compute)

    def get_current_team(self):
        """ทีมของ current_user ใน event นี้ หาครั้งเดียวต่อ request"""
        from . import request_cache
        from .teams import Team

        def compute():
            return Team.objects(members__in=[current_user], status="active", event=self).first()

        return request_cache.request_memo(f"current-team:{self.id}:{getattr(current_user, 'id', None)}", compute)

    def get_challenge_state(self):
        from noppakao import models

        from . import request_cache

        def compute():
            solved_status = ["success", "first_blood"]

            event_challenge_ids = [
                event_challenge.id for event_challenge in EventChallenge.objects(event=self, status="active").only("id")
            ]

            if not event_challenge_ids:
                return {"solve_counts": {}, "solved": set(), "hinted": set()}

            def group_by_event_challenge(match):
                pipeline = [
                    {"$match": match},
                    {"$group": {"_id": "$event_challenge", "total": {"$sum": 1}}},
                ]
                return list(models.Transaction.objects.aggregate(pipeline))

            # จำนวนคนที่แก้ได้ต่อโจทย์ นับรวมทุกคนใน event
            solve_counts = {
                str(row["_id"]): row["total"]
                for row in group_by_event_challenge(
                    {
                        "event_challenge": {"$in": event_challenge_ids},
                        "status": {"$in": solved_status},
                        "event": self.id,
                    }
                )
            }

            if self.type == "team":
                team = self.get_current_team()
                owner = {"team": team.id if team else None}
            else:
                owner = {"user": getattr(current_user, "id", None)}

            solved = {
                str(row["_id"])
                for row in group_by_event_challenge(
                    {
                        "event_challenge": {"$in": event_challenge_ids},
                        "status": {"$in": solved_status},
                        **owner,
                    }
                )
            }

            hinted = {
                str(row["_id"])
                for row in group_by_event_challenge(
                    {
                        "event_challenge": {"$in": event_challenge_ids},
                        "type": "hint",
                        **owner,
                    }
                )
            }

            return {"solve_counts": solve_counts, "solved": solved, "hinted": hinted}

        return request_cache.request_memo(f"challenge-state:{self.id}:{getattr(current_user, 'id', None)}", compute)

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
            return result[0].get("total_score", 0) + result_fail[0].get("total_score", 0)
        if result:
            return result[0].get("total_score", 0)

        return 0


class EventCompetitor(me.Document):
    meta = {"collection": "event_competitors"}
    event = me.ReferenceField("Event", dbref=True, required=True)

    team = me.ReferenceField("Team", dbref=True)
    team_name = me.StringField(default="")

    status = me.StringField(default="active", choices=STATUS_CHOICES)  # บอกถึงสถานะ
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต


class EventChallenge(me.Document):
    meta = {"collection": "event_challenges"}
    event = me.ReferenceField("Event", dbref=True, required=True)
    challenge = me.ReferenceField("Challenge", dbref=True, required=True)

    first_blood_score = me.IntField(required=True, default=0, min=0)
    success_score = me.IntField(required=True, default=0, min=0)

    hint_score = me.IntField(required=True, default=0, max=0)  # ใส่ค่าติดลบไปเลย
    fail_score = me.IntField(required=True, default=0, max=0)  # ใส่ค่าติดลบไปเลย

    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)  # บอกถึงสถานะ
    created_by = me.ReferenceField("User", dbref=True, required=True)
    created_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_by = me.ReferenceField("User", dbref=True, required=True)

    def check_answer(self, answer):

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
        return self.event.get_challenge_state()["solve_counts"].get(str(self.id), 0)

    def is_solved(self):

        return str(self.id) in self.event.get_challenge_state()["solved"]

    def get_challenge_resources(self):
        # อ่านจากชุดที่โหลดมาทั้ง event แล้ว แทนที่จะ query แยกทีละโจทย์
        from . import request_cache

        challenge_id = request_cache.reference_id(self._data.get("challenge"))
        return self.event.get_challenge_resources_map().get(challenge_id, [])

    def has_hint_unlocked(self, event_id=None):
        return str(self.id) in self.event.get_challenge_state()["hinted"]

    def solve_challenge(self):
        from noppakao import models

        if self.event.type == "team":
            team = models.Team.objects(members__in=[current_user], status="active", event=self.event).first()
            solve_challenges = models.Transaction.objects(
                event_challenge=self,
                status__in=["success", "first_blood"],
                team=team,
                event=self.event,
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
            team = models.Team.objects(members__in=[current_user], status="active", event=event).first()
            trasaction = models.Transaction.objects(event_challenge=self, type="hint", team=team).first()
        else:
            trasaction = models.Transaction.objects(event_challenge=self, type="hint", user=current_user).first()

        return trasaction


EVENT_ROLES = ["competitor", "contributor"]


class EventRole(me.Document):
    meta = {"collection": "event_roles"}
    role = me.StringField(choices=EVENT_ROLES, default="competitor", required=True)
    event = me.ReferenceField("Event", dbref=True, required=True)
    user = me.ReferenceField("User", dbref=True, required=True)

    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)  # บอกถึงสถานะ
    created_by = me.ReferenceField("User", dbref=True, required=True)
    created_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_date = me.DateField(required=True, default=datetime.datetime.now)
    updated_by = me.ReferenceField("User", dbref=True, required=True)
