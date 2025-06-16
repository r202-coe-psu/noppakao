from flask_mongoengine import MongoEngine
from .users import User
from .challenges import Challenge, ChallengeResource
from .categories import Category
from .teams import Team
from .events import Event, EventChallenge, EventRole, EventCompetitor
from .transactions import Transaction
from .organizations import Organization
from .course import Course, CourseType, CourseSection, CourseQuestion
from .oauth2 import OAuth2Token

db = MongoEngine()


def init_db(app):
    db.init_app(app)


def init_mongoengine(settings):
    import mongoengine as me

    dbname = settings.get("MONGODB_DB")
    host = settings.get("MONGODB_HOST", "localhost")
    port = int(settings.get("MONGODB_PORT", "27017"))
    username = settings.get("MONGODB_USERNAME", "")
    password = settings.get("MONGODB_PASSWORD", "")

    me.connect(db=dbname, host=host, port=port, username=username, password=password)
