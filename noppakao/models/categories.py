import mongoengine as me
import datetime
from .updates import UpdateInformation


class Category(me.Document):
    meta = {"collection": "categories"}

    name = me.StringField(required=True, unique=True, max_length=50)  # ชื่อหมวดหมู่
    status = me.StringField(default="active")  # Status หมวดหมู่
    created_by = me.ReferenceField("User", dbref=True, require=True)  # สร้างโดยใคร
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now
    )  # สร้างเมื่อวันไหน
    last_updated_by = me.ReferenceField(
        "User", dbref=True, require=True
    )  # คนที่อัพเดตล่าสุด
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True  # วันที่อัพเดต
    )
    # --------- ไม่ต้องเก็บ ----------------
    update_info = me.EmbeddedDocumentListField("UpdateInformation")

    def get_created_date(self):
        created_date = self.created_date.date().strftime("%d/%m/%Y")
        return created_date
