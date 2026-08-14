import sys
import getpass
import mongoengine as me
from noppakao import models
import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


def get_admin_password():
    while True:
        password = getpass.getpass("Enter admin password: ")
        if not password:
            print("Password cannot be empty. Please try again.")
            continue
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            continue
        return password


def check_has_user_admin_and_reset_pwd(password):
    print("Checking has user admin")
    user = models.User.objects(username="admin").first()
    if user:
        user.set_password(password)
        user.save()
        print("There is a user admin.\nReset admin password: Done")
        return True
    return False


def create_user_admin(password):
    print("start create admin")
    user = models.User(
        username="admin",
        first_name="admin",
        last_name="system",
        status="active",
        phone_number="1234567890",
        email="admin@example.com",
        roles=["user", "admin"],
    )
    user.set_password(password)

    user.save()
    print("finish")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        me.connect(db="noppakaodb", host=sys.argv[1])
    else:
        me.connect(db="noppakaodb")

    password = get_admin_password()
    print("start create")
    if not check_has_user_admin_and_reset_pwd(password):
        create_user_admin(password)

    print("end create")

