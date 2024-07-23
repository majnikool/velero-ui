import json
import velero_ui.velero_api as velero_api

from flask import request, jsonify

def get_restore_list():
    restores = json.dumps(velero_api.get_restore_list())
    return jsonify(restores)

def create_restore():
    data = request.get_json()
    backup_name = data.get("backupName")
    schedule_name = data.get("scheduleName")

    if backup_name and schedule_name:
        return jsonify({"error": "Invalid request. You can only provide either backupName or scheduleName."})

    if backup_name:
        resource_type = "backup"
        resource_name = backup_name
    elif schedule_name:
        resource_type = "schedule"
        resource_name = schedule_name
    else:
        return jsonify({"error": "Invalid request. Please provide either backupName or scheduleName."})

    outcome = velero_api.create_restore(resource_name)
    status = outcome["status"]
    message = outcome["message"]

    if status:
      return {"message": f"Restore from {resource_type} {resource_name} created successfully"}, 200
    else: 
      return {"message": f"Restore from  {resource_type} {resource_name} failed to create. {message}"}, 500

def delete_restore():
    restore_name = request.args.get("name")
    if not restore_name:
        return {"message": "Restore name is required as a query parameter"}

    outcome = velero_api.delete_restore(restore_name)
    status = outcome["status"]
    message = outcome["message"]

    if status:
      return {"message": f"Restore {restore_name} deleted successfully"}, 200
    else: 
      return {"message": f"Restore {restore_name} failed to delete. {message}"}, 500

def get_restore_logs():
    restore_name = request.args.get("name")
    if not restore_name:
        return {"message": "Restore name is required as a query parameter"}

    output = velero_api.get_restore_log(restore_name)

    return {"logs": output}

def describe_restore():
    restore_name = request.args.get("name")
    if not restore_name:
        return {"message": "Restore name is required as a query parameter"}

    output = velero_api.get_restore_describe(restore_name)

    return {"logs": output}
