import mongoengine as me
import datetime
from .updates import UpdateInformation

STATUS_CHOICES = [
    "active",
    "disactive"
]

ANSWER_TYPES = [
    "flag",
    "plaintext"
]

class Question(me.Document):
    meta = {"collection": "questions"}  # ตั้งชื่อ collection

    name = me.StringField(required=True, max_length=256)  # หัวข้อโจทย์
    description = me.StringField()  # รายละเอียด
    category = me.ReferenceField("Category", dbref=True)  # หมวดหมู่

    hint = me.StringField(max_length=512)  # คำใบ้
    answer = me.StringField(required=True, max_length=512)  # ธงหรือก็คือคำตอบ 
    answer_type = me.StringField(choices=ANSWER_TYPES, default="flag", required=True)

    # Question Information
    question_url = me.StringField()
    question_file = me.FileField()  # จัดเก็บไฟล์

    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)  # บอกถึงสถานะ
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True )
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)  # เวลาการสร้างหรืออัพเดตล่าสุด
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต


    def get_uploaded_date(self):
        uploaded_datetime = self.uploaded_date.date().strftime("%d/%m/%Y")
        return uploaded_datetime

    def get_problem_solvers(self):
        value = len(self.problem_solvers)
        return value
