import io

from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    abort,
    jsonify,
)
from flask_login import login_required, current_user

from noppakao import models
from noppakao.web import forms, acl

import datetime

module = Blueprint("media", __name__, url_prefix="/media")


@module.route("")
@login_required
def index():
    media = models.Media.objects()
    return render_template("/media/index.html", media=media)


@module.route("/<media_id>/download/<filename>")
@acl.allow_download(models.Media, "media_id")
def download(media_id, filename):
    media = models.Media.objects.get(id=media_id)

    if not media or not media.file or media.file.filename != filename:
        return abort(403)

    if not media.is_encrypted:
        return send_file(
            media.file,
            download_name=media.file.filename,
            mimetype=media.file.content_type,
        )

    encrypted_manager = models.utils.EncryptedManager(
        str(media.owner.id),
        media.created_date.isoformat(timespec="milliseconds").encode("utf-8"),
    )

    bytes_io = io.BytesIO()
    bytes_io.write(encrypted_manager.decrypt_data(media.file.read()))
    bytes_io.seek(0)
    return send_file(
        bytes_io,
        download_name=media.file.filename,
        mimetype=media.file.content_type,
    )


@module.route(
    "/upload",
    methods=["GET", "POST"],
)
@login_required
def upload():
    type = request.args.get("type", "normal").lower()
    file = request.files["image"]

    media = models.Media(
        name=file.filename,
        type="image",
        owner=current_user._get_current_object(),
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        is_encrypted=False,
    )
    if type == "cybersecurity":
        encrypted_manager = models.utils.EncryptedManager(
            str(current_user.id),
            media.created_date.isoformat(timespec="milliseconds").encode("utf-8"),
        )
        media.file.put(
            encrypted_manager.encrypt_data(file.read()),
            content_type=file.content_type,
            filename=file.filename,
        )
        media.is_encrypted = True

    else:
        media.file.put(file, content_type=file.content_type, filename=file.filename)

    media.save()
    media.reload()

    data = dict(
        media_url=url_for(
            "media.download", media_id=media.id, filename=media.file.filename
        ),
    )
    return jsonify(data)


@module.route(
    "/<media_id>/trash",
    methods=["GET"],
)
@login_required
def trash(media_id):
    media = models.Media.objects(
        id=media_id, owner=current_user._get_current_object()
    ).first()

    if not media and current_user.has_roles("admin"):
        media = models.Media.objects.with_id(media_id)

    if media:
        media.status = "trash"
        media.save()

    return redirect(url_for("media.index"))


@module.route(
    "/<media_id>/delete",
    methods=["GET"],
)
@login_required
def delete(media_id):
    media = models.Media.objects(
        id=media_id, owner=current_user._get_current_object()
    ).first()

    if not media and current_user.has_roles("admin"):
        media = models.Media.objects.with_id(media_id)

    if media:
        media.delete()

    return redirect(url_for("media.index"))
