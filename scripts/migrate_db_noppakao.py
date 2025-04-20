# migrate_publish_date.py

import sys
import mongoengine as me
from noppakao.models import Event


def main():
    # เชื่อมต่อ DB ตาม host ที่ส่งมาทาง argument
    if len(sys.argv) > 1:
        me.connect(db="noppakaodb", host=sys.argv[1])
    else:
        me.connect(db="noppakaodb")

    collection = Event._get_collection()

    # อัปเดตทุก document ที่มี publish_date
    result = collection.update_many(
        {"publish_date": {"$exists": True}},
        [
            {"$set": {"publish_started_date": "$publish_date"}},
            {"$unset": "publish_date"},
        ],
    )

    print(f"Migrated {result.modified_count} documents.")


if __name__ == "__main__":
    main()
