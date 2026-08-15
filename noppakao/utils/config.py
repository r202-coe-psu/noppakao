import os
import flask
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

settings = None


def init_config(config_obj):
    load_dotenv()
    config_obj.from_object("noppakao.default_settings")

    for key, value in os.environ.items():
        if (
            key in config_obj
            or key.startswith("NOPPHAKAO_")
            or key.startswith("GOOGLE_")
            or key.startswith("MONGODB_")
            or key == "SECRET_KEY"
        ):
            if value.isdigit():
                config_obj[key] = int(value)
            elif (value.startswith("{") and value.endswith("}")) or (value.startswith("[") and value.endswith("]")):
                import ast
                try:
                    config_obj[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    config_obj[key] = value
            else:
                config_obj[key] = value

    if os.environ.get("NOPPHAKAO_SETTINGS"):
        config_obj.from_envvar("NOPPHAKAO_SETTINGS", silent=True)


def get_settings():
    global settings

    if not settings:
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../../../"
        )

        settings = flask.config.Config(file_path)
        init_config(settings)

    return settings

