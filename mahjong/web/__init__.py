__version__ = "0.0.1"

import optparse
import pathlib

from flask import Flask

from .. import models
from . import views
from . import acl
from . import caches
from . import oauth

app = Flask(__name__)


def create_app():
    app.config.from_object("mahjong.default_settings")
    app.config.from_envvar("MAHJONG_SETTINGS", silent=True)

    MAHJONG_CACHE_DIR = app.config.get("MAHJONG_CACHE_DIR")
    p = pathlib.Path(MAHJONG_CACHE_DIR)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

    models.init_db(app)
    views.register_blueprint(app)
    acl.init_acl(app)
    caches.init_cache(app)
    oauth.init_oauth(app)

    return app


def get_program_options(default_host="127.0.0.1", default_port="8080"):
    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """

    parser = optparse.OptionParser()
    parser.add_option(
        "-H",
        "--host",
        help="Hostname of the Flask app " + "[default %s]" % default_host,
        default=default_host,
    )
    parser.add_option(
        "-P",
        "--port",
        help="Port for the Flask app " + "[default %s]" % default_port,
        default=default_port,
    )

    parser.add_option(
        "-c", "--config", dest="config", help=optparse.SUPPRESS_HELP, default=None
    )
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug", help=optparse.SUPPRESS_HELP
    )
    parser.add_option(
        "-p",
        "--profile",
        action="store_true",
        dest="profile",
        help=optparse.SUPPRESS_HELP,
    )

    options, _ = parser.parse_args()

    return options
