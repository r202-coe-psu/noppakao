import mongoengine as me
import datetime


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


class CourseType(me.Document):
    meta = {"collection": "course_type"}
    name = me.StringField()
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง


class CourseSection(me.Document):
    meta = {"collection": "course_section"}
    course = me.ReferenceField("Course", dbref=True, required=True)
    header = me.StringField()
    exp_ = me.IntField()
    header_description = me.StringField()

    status = me.StringField()
    content = me.StringField()

    mark_read = me.StringField()
    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    create_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง


class CourseQuestion(me.Document):
    meta = {"collection": "course_question"}
    course = me.ReferenceField("Course", dbref=True, required=True)
    course_question = me.ReferenceField("Challenge", dbref=True, required=True)
    exp_ = me.IntField()
    status = me.StringField()

    created_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_by = me.ReferenceField("User", dbref=True, required=True)  # คนสุดท้ายที่กดอัพเดต
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    create_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง


class TransactionCourse(me.Document):
    meta = {"collection": "transaction_course"}
    course = me.ReferenceField("Course", dbref=True, required=True)
    course_section = me.ReferenceField("CourseSection", dbref=True, required=True)
    course_question = me.ReferenceField("Challenge", dbref=True, required=True)
    exp_ = me.IntField()

    created_by = me.ReferenceField("User", dbref=True, required=True)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้างหรืออัพเดตล่าสุด
    create_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # เวลาการสร้าง
