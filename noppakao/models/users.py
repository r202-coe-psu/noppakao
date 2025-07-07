from email.policy import default
import mongoengine as me
import datetime
from flask_login import UserMixin, current_user
from noppakao import models

from flask import url_for


class Organization(me.Document):
    meta = {"collection": "organizations"}
    name = me.StringField(required=True)
    logo = me.ImageField()
    provice = me.StringField()


class User(me.Document, UserMixin):
    meta = {"collection": "users"}
    avatar = me.FileField()
    display_name = me.StringField(default="", max_length=255)
    first_name = me.StringField(required=True, max_length=128)
    last_name = me.StringField(required=True, max_length=128)

    username = me.StringField(required=True, unique=True, max_length=64)
    password = me.BinaryField(required=True, default=b"")
    email = me.StringField(required=True, unique=True, max_length=128)
    phone_number = me.StringField(max_length=10, default="")
    status = me.StringField(default="active")
    roles = me.ListField(me.StringField(), default=["user"])
    organization = me.ReferenceField("Organization", dbref=True)
    picture_url = me.StringField(default="")
    resources = me.DictField()
    enrolled_course = me.ListField(me.ReferenceField("Course", dbref=True, default=[]))

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    last_login_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def get_course_progress(self):
        pipeline = [
            {
                "$match": {
                    "result": "success",
                }
            },
            {
                "$lookup": {
                    "from": "course_content",
                    "localField": "course_content.$id",
                    "foreignField": "_id",
                    "as": "course_content_doc",
                }
            },
            {"$unwind": "$course_content_doc"},
            {
                "$group": {
                    "_id": "$created_by",
                    "total_exp": {"$sum": "$course_content_doc.exp_"},
                }
            },
        ]

        transactions = list(
            models.TransactionCourse.objects(created_by=self).aggregate(pipeline)
        )

        total_exp = transactions[0]["total_exp"] if transactions else 0


        level_config = models.LevelConfig.objects.first()
        user_progress = {
            "exp": total_exp,
            "level": 0,
            "current_exp_progress": 0,
            "total_exp_progress": 100,
            "percentage": 0,
        }
        if not level_config:
            return user_progress
        
        for level, exp in level_config.level_exp_table.items():
            if total_exp < int(exp):
                user_progress["level"] = int(level) - 1
                user_progress["current_exp_progress"] = total_exp - int(level_config.level_exp_table.get(str(int(level) - 1), 0))
                user_progress["total_exp_progress"] = int(exp) - int(level_config.level_exp_table.get(str(int(level) - 1), 0))
                user_progress["percentage"] = (
                    user_progress["current_exp_progress"]
                    / user_progress["total_exp_progress"]
                ) * 100 if user_progress["total_exp_progress"] > 0 else 0
                return user_progress
        else:
            # case when total_exp is greater than the last level's exp
            user_progress["level"] = len(level_config.level_exp_table)
            user_progress["current_exp_progress"] = total_exp - int(
                level_config.level_exp_table.get(
                    str(user_progress["level"]), 0
                )
            )
            user_progress["total_exp_progress"] = 100  # Assuming 100% for the last level
            user_progress["percentage"] = (
                user_progress["current_exp_progress"]
                / user_progress["total_exp_progress"]
            ) * 100 if user_progress["total_exp_progress"] > 0 else 0
        return user_progress
    
    def get_course_streak(self):
        today = datetime.datetime.now()
        today_start = datetime.datetime.combine(today.date(), datetime.time.min)
        today_end = datetime.datetime.combine(today.date(), datetime.time.max)
        
        # Check if there's activity today
        is_today_activity = models.TransactionCourse.objects(
            status="active",
            created_by=self,
            create_date__gte=today_start,
            create_date__lte=today_end
        ).first()
        
        # If no activity today, check if there was activity yesterday to continue the streak
        if not is_today_activity:
            yesterday_start = today_start - datetime.timedelta(days=1)
            yesterday_end = today_end - datetime.timedelta(days=1)
            is_yesterday_activity = models.TransactionCourse.objects(
                status="active",
                created_by=self,
                create_date__gte=yesterday_start,
                create_date__lte=yesterday_end
            ).first()
            
            # If no activity yesterday either, return 0
            if not is_yesterday_activity:
                return 0
            
            today_start = yesterday_start
            today_end = yesterday_end
        
        # Count the streak starting from the reference day
        streak = 1  # Start with 1 for the reference day
        day = 1
        
        # Check each previous day until we find a gap
        while True:
            prev_day_start = today_start - datetime.timedelta(days=day)
            prev_day_end = today_end - datetime.timedelta(days=day)
            
            activity = models.TransactionCourse.objects(
                status="active",
                created_by=self,
                create_date__gte=prev_day_start,
                create_date__lte=prev_day_end
            ).first()
            
            if not activity:
                break
                
            streak += 1
            day += 1
            
        return streak

    def check_team_event(self, event_id):
        from noppakao import models

        event = models.Event.objects(id=event_id).first()
        team = models.Team.objects(event=event, members__in=[self]).first()
        if team:
            return True

        return None

    def check_join_event(self, event_id):
        from noppakao import models

        event = models.Event.objects(id=event_id).first()
        event_role = models.EventRole.objects(user=self, event=event).first()
        if event_role:
            return True

        return None

    def set_password(self, password):
        from werkzeug.security import generate_password_hash

        self.password = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash

        if check_password_hash(self.password, password):
            return True
        return False

    def check_roles(self, roles: list):
        if set(roles) & set(self.roles):
            return True
        return False

    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def has_roles(self, *roles):
        for role in roles:
            if role in self.roles:
                return True
        return

    def get_avatar_url(self):
        if self.avatar:
            return url_for(
                "accounts.get_avatar",
                team_id=self.id,
                filename=self.avatar.filename,
            )
        else:
            return url_for("static", filename="images/hacker.png")


class EnrollCourse(me.Document):
    meta = {"collection": "enroll_course"}
    user = me.ReferenceField("User", dbref=True, required=True)
    course = me.ReferenceField("Course", dbref=True, required=True)
    index = me.IntField(required=True, default=1)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    last_accessed = me.DateTimeField(default=datetime.datetime.now, auto_now=True)
    status = me.StringField(
        default="active", choices=["active", "disactive"], required=True
    )
