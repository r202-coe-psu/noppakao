import mongoengine as me
import datetime

STATUS_CHOICES = ["active", "disactive"]


class Category(me.Document):
    meta = {"collection": "categories"}

    name = me.StringField(required=True, unique=True, max_length=50)  # ชื่อหมวดหมู่

    status = me.StringField(
        default="active", choices=STATUS_CHOICES, required=True
    )  # Status หมวดหมู่
    created_by = me.ReferenceField("User", dbref=True, require=True)  # สร้างโดยใคร
    updated_by = me.ReferenceField("User", dbref=True, require=True)  # คนที่อัพเดตล่าสุด
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now
    )  # สร้างเมื่อวันไหน
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )  # วันที่อัพเดต)

    def get_created_date(self):
        created_date = self.created_date.date().strftime("%d/%m/%Y")
        return created_date
