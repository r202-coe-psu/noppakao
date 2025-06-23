from flask import redirect, url_for, request
from flask_login import current_user, LoginManager, login_url
from werkzeug.exceptions import Forbidden, Unauthorized, NotFound
from . import models

from functools import wraps

login_manager = LoginManager()


def init_acl(app):
    login_manager.init_app(app)

    @app.errorhandler(401)
    def unauthorized(e):
        return Unauthorized()

    @app.errorhandler(403)
    def forbidden(e):
        return "You don't have permission."


def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                raise Forbidden()

            for role in roles:
                if role in current_user.roles:
                    return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


@login_manager.user_loader
def load_user(user_id):
    user = models.User.objects(id=user_id, status="active").first()
    return user


@login_manager.unauthorized_handler
def unauthorized_callback():
    print("unauthorized!!\n")
    if request.method == "GET":
        response = redirect(login_url("accounts.login"))
        return response

    return redirect(url_for("accounts.login"))

def allow_download(Model, key_id):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                raise Unauthorized()

            if "admin" in current_user.roles:
                return func(*args, **kwargs)

            object_id = request.view_args.get(key_id)
            data = Model.objects(id=object_id).first()
            if not data:
                raise NotFound()

            if data.owner == current_user._get_current_object():
                return func(*args, **kwargs)

            if not data.ticket:
                raise NotFound()

            if data.ticket.is_responsible(current_user._get_current_object()):
                return func(*args, **kwargs)

            raise Forbidden()

        return wrapped

    return wrapper
