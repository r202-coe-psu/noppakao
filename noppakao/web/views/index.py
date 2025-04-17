from flask import Blueprint, render_template
from flask_login import login_required

module = Blueprint("index", __name__)


@module.route("/")
@login_required
def index():
    return render_template("/index/index.html")
