import json
import velero_ui.velero_api as velero_api
from flask import request, jsonify


# ScheduleList related functions
def get_storages():
    schedules = json.dumps(velero_api.get_storage_list())
    return jsonify(schedules)
