import mongoengine as me
import datetime
from .updates import UpdateInformation


class FlagQuestion(me.Document):
    problem_header = me.StringField(required=True, max_length=256)  # หัวข้อโจทย์
    description = me.StringField()  # รายละเอียด
    category = me.ReferenceField("Category", dbref=True)  # หมวดหมู่
    status = me.StringField(default="failled")  # บอกถึงสถานะ
    upload_file = me.FileField(required=True)  # จัดเก็บไฟล์
    upload_file_name = me.StringField(required=True, default="")  # ชื่อไฟล์

    problem_solvers = me.ListField(default=[])  # คนที่สามารถทำได้
    hint = me.StringField(default="", max_length=512)  # คำใบ้
    flag = me.StringField(required=True, default="", max_length=512)  # ธงหรือก็คือคำตอบ 
    point = me.IntField(required=True, default=50)  # คะแนน

    # อัพเดตเวลา
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    last_updated_by = me.ReferenceField(
        "User", dbref=True, required=True
    )  # คนสุดท้ายที่กดอัพเดต
    uploaded_date = me.DateTimeField(
        required=True, default=datetime.datetime.now
    )  # อัพเดตวันไหน

    # อัพโหลดโดย
    update_info = me.EmbeddedDocumentListField("UpdateInformation")  # สร้างโดยใคร
    upload_by = me.ReferenceField("User", dbref=True, required=True)  # อัพโหลดโดยใคร

    meta = {"collection": "submitflags"}  # ตั้งชื่อ collection

    def get_uploaded_date(self):
        uploaded_datetime = self.uploaded_date.date().strftime("%d/%m/%Y")
        return uploaded_datetime

    def get_problem_solvers(self):
        value = len(self.problem_solvers)
        return value
