import datetime
from noppakao import models


def create_update_information(current_user, request, action):
    updater_info = models.UpdateInformation(
        user=current_user._get_current_object(),
        ip_address=request.environ.get("HTTP_X_REAL_IP", request.remote_addr),
        user_agent=request.environ.get("HTTP_USER_AGENT", ""),
        created_date=datetime.datetime.now(),
        action=action,
    )
    return updater_info
