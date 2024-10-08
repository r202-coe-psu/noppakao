import mongoengine as me
import datetime

STATUS_CHOICES = ["active", "disactive"]

ANSWER_TYPES = ["flag", "plaintext"]


class ChallengeResource(me.Document):
    meta = {"collection": "challenge_resources"}
    challenge = me.ReferenceField("Challenge", dbref=True)
    file = me.FileField()  # จัดเก็บไฟล์
    status = me.StringField(
        default="active", choices=STATUS_CHOICES, required=True
    )  # บอกถึงสถานะ
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต


class Challenge(me.Document):
    meta = {"collection": "challenges"}  # ตั้งชื่อ collection

    name = me.StringField(required=True, max_length=256)  # หัวข้อโจทย์
    description = me.StringField()  # รายละเอียด
    category = me.ReferenceField("Category", dbref=True)  # หมวดหมู่

    hint = me.StringField(max_length=512)  # คำใบ้
    answer = me.StringField(required=True, max_length=512)  # ธงหรือก็คือคำตอบ
    answer_type = me.StringField(choices=ANSWER_TYPES, default="flag", required=True)

    # Challenge Information
    challenge_url = me.StringField()

    status = me.StringField(
        default="active", choices=STATUS_CHOICES, required=True
    )  # บอกถึงสถานะ
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต

    def get_uploaded_date(self):
        uploaded_datetime = self.uploaded_date.date().strftime("%d/%m/%Y")
        return uploaded_datetime

    def get_problem_solvers(self):
        value = len(self.problem_solvers)
        return value

    def get_challenge_resources(self):
        return ChallengeResource.objects(challenge=self, status="active")
