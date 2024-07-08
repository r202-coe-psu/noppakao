import sys
import mongoengine as me
from mahjong import models
import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


def check_has_user_admin_and_reset_pwd():
    print("Checking has user admin")
    user = models.User.objects(username="admin").first()
    if user:
        user.set_password("p@ssw0rd")
        user.save()
        print("There is a user admin.\nReset admin password: Done")
        return True
    return False


def create_user_admin():
    print("start create admin")
    user = models.User(
        username="admin",
        first_name="admin",
        last_name="system",
        status="active",
        phone_number="1234567890",
        email="admin@example.com",
        roles=["user", "admin"],
        password=bcrypt.generate_password_hash("p@ssw0rd"),
    )

    user.save()
    print("finish")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        me.connect(db="mahjongdb", host=sys.argv[1])
    else:
        me.connect(db="mahjongdb")
    print("start create")
    if not check_has_user_admin_and_reset_pwd():
        create_user_admin()

    print("end create")
