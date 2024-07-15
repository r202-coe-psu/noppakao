import datetime
import mongoengine as me
import os
from mongoengine.queryset.visitor import Q

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
    send_file,
    abort,
)

from werkzeug.security import check_password_hash
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from noppakao.utils import updater_info
from noppakao import models
from noppakao.web import forms
from .. import oauth

from . import paginations

module = Blueprint("questions", __name__, url_prefix="/questions")
bcrypt = Bcrypt()


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    questions = models.Question.objects()
    flag = request.args.get("flag")
    question_id = request.args.get("question_id")

    if flag and question_id:
        return redirect(
            url_for(
                "questions.question_question",
                question_id=question_id,
                flag=flag,
            )
        )

    return render_template(
        "questions/index.html",
        questions=questions,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"question_id": None})
@module.route("/<question_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(question_id):
    question = None
    form = forms.questions.QuestionForm()

    if question_id:
        question = models.Question.objects(id=question_id).first()
        form = forms.questions.QuestionForm(obj=question)
    form.category.choices = [
        (f"{category.id}", category.name)
        for category in models.Category.objects(status="active")
    ]
    if not form.validate_on_submit():
        if question:
            form.category.data = str(question.category.id)
        print(form.errors)
        return render_template(
            "questions/create_or_edit.html", form=form, question=question
        )
    if not question_id:
        question = models.Question()
        question.created_by = current_user
    form.populate_obj(question)
    if not question_id:
        if form.uploaded_file.data:
            question.question_file.put(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )
    else:
        if form.uploaded_file.data:
            question.question_file.replace(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )
    question.category = models.Category.objects(id=form.category.data).first()
    question.updated_by = current_user
    question.save()
    return redirect(url_for("questions.index"))


@module.route("<question_id>/download_file", methods=["GET", "POST"])
@login_required
def download(question_id):
    question = models.Question.objects(id=question_id)
    try:
        question = models.Question.objects(id=question_id).first()
    except:
        return abort(404)

    res = send_file(
        question.upload_file,
        download_name=question.upload_file.filename,
        mimetype=question.upload_file.content_type,
    )
    return res


@module.route("<question_id>/question/<flag>", methods=["GET", "POST"])
@login_required
def question_question(question_id, flag):

    try:
        question = models.Question.objects.get(id=question_id)
        team = models.Team.objects.get(id=current_user.team.id)
    except:
        return redirect(url_for("questions.index"))

    if check_password_hash(question.flag, flag) and not "admin" in current_user.roles:
        if not current_user.team.name in question.problem_solvers:
            current_user.score += question.point
            team.score += question.point
            question.problem_solvers.append(current_user.team.name)
            team.updated_date = datetime.datetime.now()
            current_user.updated_date = datetime.datetime.now()

    question.save()
    current_user.save()
    team.save()
    return redirect(url_for("questions.index"))
