from flask import Blueprint, request, send_file, url_for, abort
from flask.json import jsonify
from flask_login import current_user, login_required
from mongoengine import Q

from mahjong import models
from mahjong.web import acl

module = Blueprint("data", __name__, url_prefix="/data")


@module.route("")
def get_all_data():
    category_name = request.args.get("category")
    category = models.Category.objects(name=category_name).first()

    upload_datas = models.Upload_data.objects(
        category=category, status="active", data_status="waiting"
    )

    if not category:
        return abort(404)

    if not upload_datas:
        return abort(404)

    all_data = []
    for upload_data in upload_datas:
        data = {
            "id": str(upload_data.id),
            "api_url": f"{url_for('data.get_data', data_id=upload_data.id)}",
            "status": f"{upload_data.status}",
        }
        print(url_for("data.get_data", data_id=upload_data.id))
        all_data.append(data)

    return jsonify(all_data)


@module.route("/<data_id>")
def get_data(data_id):
    try:
        upload_data = models.Upload_data.objects(id=data_id, status="active").first()
    except:
        return abort(404)

    res = send_file(
        upload_data.upload_file,
        download_name=upload_data.upload_file.filename,
        mimetype=upload_data.upload_file.content_type,
    )

    return res


@module.route("/<data_id>", methods=["PUT"])
def change_data_status(data_id):
    data_status = request.args.get("data_status", None)

    upload_data = models.Upload_data.objects(id=data_id).first()

    if not upload_data:
        return abort(404)

    upload_data.data_status = data_status
    upload_data.save()

    return "complete"
