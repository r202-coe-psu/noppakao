import mongoengine as me
import datetime


STATUS_CHOICES = ["active", "disactive"]


class Course(me.Document):
    meta = {"collection": "course"}
    name = me.StringField()  # ชื่อ course
    description = me.StringField()  # รายละเอียด
    level = me.StringField()  # ระดับ

    owner = me.ReferenceField("User", dbref=True, required=True)  # เจ้าของ course
    type = me.ReferenceField("CourseType", dbref=True, required=True)  # Type ของ course

    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง
    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)


class CourseType(me.Document):
    meta = {"collection": "course_type"}
    name = me.StringField()
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง
    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)


class CourseContent(me.Document):
    meta = {"collection": "course_content"}
    course = me.ReferenceField("Course", dbref=True, required=True)
    type = me.StringField(
        choices=["header", "section", "question"], required=True
    )  # ประเภทของ content มี section หรือ question
    exp_ = me.IntField()  # จำนวน exp ที่ได้จากการทำ content นี้

    index = me.IntField()  # ลำดับของ content ใน course
    header = me.StringField(required=True)  # ชื่อของ content
    header_description = me.StringField()  # คำอธิบายของ content

    # header image
    header_image = me.ReferenceField("Media", dbref=True)  # รูปภาพของ header

    # section data
    content = me.StringField()  # เนื้อหาของ section

    # question data
    course_question = me.ReferenceField("Challenge", dbref=True)  # คำถาม

    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    create_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง
    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)

    # Check if the content is a question type
    def check_question(self):
        transaction_course = TransactionCourse.objects(
            course_content=self, type="question", result="success", status="active"
        ).first()
        if transaction_course:
            return True
        return False



class TransactionCourse(me.Document):
    meta = {"collection": "transaction_course"}
    type = me.StringField(choices=["section", "question"], required=True)
    course = me.ReferenceField("Course", dbref=True, required=True)
    course_content = me.ReferenceField("CourseContent", dbref=True, required=True)
    course_question = me.ReferenceField("Challenge", dbref=True)

    created_by = me.ReferenceField("User", dbref=True, required=True)
    create_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง

    result = me.StringField(choices=["success", "failed"], default="success")
    status = me.StringField(default="active", choices=STATUS_CHOICES, required=True)
