from noppakao.models import Event
from mongoengine import connect
from bson import ObjectId

connect("noppakaodb")

# เข้าถึง raw MongoDB collection โดยตรง
collection = Event._get_collection()

# ค้นหาทุก document ที่มี field 'publish_date'
for doc in collection.find({"publish_date": {"$exists": True}}):
    event_id = doc["_id"]
    publish_date = doc["publish_date"]
    print("started update db")
    # อัปเดต field ใหม่และลบ field เดิม
    collection.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$set": {"publish_started_date": publish_date},
            "$unset": {"publish_date": ""},
        },
    )
    print("suscess update db")
