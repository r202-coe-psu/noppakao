from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_bcrypt import Bcrypt
from flask_login import current_user
from mongoengine.queryset.visitor import Q

from noppakao import models
from noppakao.web import forms

from ... import acl

module = Blueprint("challenges", __name__, url_prefix="/challenges")
bcrypt = Bcrypt()


@module.route("/", methods=["GET", "POST"])
@acl.roles_required("admin")
def index():
    category_refs = models.Challenge.objects().distinct("category")
    category_ids = [c.id if hasattr(c, "id") else c for c in category_refs if c]
    categories = models.Category.objects(id__in=category_ids)

    form = forms.challenges.ChallengeSearchForm(request.args)
    form.category.choices = [("", "All types")] + [(f"{category.id}", category.name) for category in categories]

    search = (form.search.data or "").strip()
    category_id = (form.category.data or "").strip()

    query = Q()
    if search:
        query &= Q(name__icontains=search)

    if category_id:
        query &= Q(category=category_id)

    challenges = models.Challenge.objects(query).select_related()

    event_categorys = []
    for challenge in challenges:
        if challenge.category and not challenge.category in event_categorys:
            event_categorys.append(challenge.category)

    return render_template(
        "admin/challenges/index.html",
        challenges=challenges,
        event_categorys=event_categorys,
        form=form,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"challenge_id": None})
@module.route("/<challenge_id>/edit", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_or_edit(challenge_id):
    challenge = None
    form = forms.challenges.ChallengeForm()

    if challenge_id:
        challenge = models.Challenge.objects(id=challenge_id).first()
        form = forms.challenges.ChallengeForm(obj=challenge)
    form.category.choices = [(f"{category.id}", category.name) for category in models.Category.objects(status="active")]
    delete_form = forms.challenges.DeleteChallengeResourceForm()
    if not form.validate_on_submit():
        if challenge:
            form.category.data = str(challenge.category.id)
        print(form.errors)
        return render_template(
            "admin/challenges/create_or_edit.html",
            form=form,
            challenge=challenge,
            delete_form=delete_form,
        )

    if not challenge_id:
        challenge = models.Challenge()
        challenge.created_by = current_user
    form.populate_obj(challenge)
    challenge.category = models.Category.objects(id=form.category.data).first()
    challenge.updated_by = current_user
    challenge.save()

    # ถ้าไม่ได้เลือกไฟล์ใหม่ flask จะยังส่ง FileStorage เปล่า (filename == "") มาให้ ต้องกรองออก
    for file in form.uploaded_file.data or []:
        if not file or not file.filename:
            continue
        challenge_resource = models.ChallengeResource()
        challenge_resource.file.put(
            file,
            filename=file.filename,
            content_type=file.content_type,
        )
        challenge_resource.challenge = challenge
        challenge_resource.created_by = current_user
        challenge_resource.updated_by = current_user
        challenge_resource.save()

    return redirect(url_for("admin.challenges.index"))


@module.route("/<challenge_id>/view_file_challenge", methods=["GET", "POST"])
@acl.roles_required("admin")
def view_file_challenge(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    challenge_resources = models.ChallengeResource.objects(challenge=challenge, status="active")
    form = forms.challenges.UploadChallengeFileForm()

    if not form.validate_on_submit():
        print(form.errors)
        return render_template(
            "/admin/challenges/view_file_challenge.html",
            challenge_resources=challenge_resources,
            form=form,
            challenge=challenge,
        )
    for file in form.uploaded_file.data or []:
        if not file or not file.filename:
            continue
        challenge_resource = models.ChallengeResource()
        challenge_resource.file.put(
            file,
            filename=file.filename,
            content_type=file.content_type,
        )
        challenge_resource.challenge = challenge
        challenge_resource.created_by = current_user
        challenge_resource.updated_by = current_user
        challenge_resource.save()

    return render_template(
        "/admin/challenges/view_file_challenge.html",
        challenge_resources=challenge_resources,
        form=form,
        challenge=challenge,
    )


@module.route(
    "/<challenge_id>/challenge_resource/<challenge_resource_id>/delete",
    methods=["POST"],
)
@acl.roles_required("admin")
def delete(challenge_id, challenge_resource_id):
    form = forms.challenges.DeleteChallengeResourceForm()
    if not form.validate_on_submit():
        return abort(400)

    challenge = models.Challenge.objects(id=challenge_id).first()
    if not challenge:
        return abort(404)

    challenge_resource = models.ChallengeResource.objects(
        id=challenge_resource_id,
        challenge=challenge,
        status="active",
    ).first()
    if not challenge_resource:
        return abort(404)

    challenge_resource.status = "disactive"
    challenge_resource.save()
    return redirect(url_for("admin.challenges.create_or_edit", challenge_id=challenge.id))


@module.route("/<challenge_id>/download_file", methods=["GET", "POST"])
@acl.roles_required("admin")
def download(challenge_id):
    challenge = models.Challenge.objects(id=challenge_id)
    try:
        challenge = models.Challenge.objects(id=challenge_id).first()
    except:
        return abort(404)

    res = send_file(
        challenge.upload_file,
        download_name=challenge.upload_file.filename,
        mimetype=challenge.upload_file.content_type,
    )
    return res


# @module.route("<challenge_id>/challenge/<flag>", methods=["GET", "POST"])
# @acl.roles_required("admin")
# def challenge_challenge(challenge_id, flag):

#     try:
#         challenge = models.Challenge.objects.get(id=challenge_id)
#         team = models.Team.objects.get(id=current_user.team.id)
#     except:
#         return redirect(url_for("challenges.index"))

#     if check_password_hash(challenge.flag, flag) and not "admin" in current_user.roles:
#         if not current_user.team.name in challenge.problem_solvers:
#             current_user.score += challenge.point
#             team.score += challenge.point
#             challenge.problem_solvers.append(current_user.team.name)
#             team.updated_date = datetime.datetime.now()
#             current_user.updated_date = datetime.datetime.now()

#     challenge.save()
#     current_user.save()
#     team.save()
#     return redirect(url_for("challenges.index"))
