import json
import velero_ui.velero_api as velero_api
import logging

from flask import request, jsonify

logger = logging.getLogger(__name__)

# ScheduleList related functions
def get_schedules():
    schedules = json.dumps(velero_api.get_schedule_list())
    return jsonify(schedules)

def create_schedule():
    try: 
        data = request.get_json()
        logger.debug(f"Incoming request from frontend: {data}")

        schedule_request = {
                "apiVersion": "velero.io/v1",
                "kind": "Schedule",
                "metadata": {
                    "name": f"{data["metadata_name"]}",
                    "namespace": "velero",
                },
                "spec": {
                    "schedule": data["spec_schedule"],
                    "template": {
                     "includedNamespaces": data["spec_includedNamespaces"],
                      "ttl": f"{data["spec_ttl"]}",
                      "storageLocation": "default",
                      "defaultVolumesToFsBackup": True                   
                    }
                }   
            }
        
        spec_labels = data["spec_labels"]
            
        if len(spec_labels) > 0:
            matchLabels = {}
            for label in spec_labels:
                if label:
                  splited_label = label.split('=')
                  key = splited_label[0]
                  value = splited_label[1]
                  
                  matchLabels[key] = value
                
            schedule_request['spec']['template']['labelSelector'] = {"matchLabels" : matchLabels}
                    
            outcome = velero_api.create_schedule(schedule_request)
            status = outcome["status"]
            message = outcome["message"]

            if status:
                return {"message": f"Schedule {data["metadata_name"]} created successfully"}, 200
            else: 
                raise Exception(f"{message}")
    except Exception as e:
        logger.error(e)
        return {"message": f"Failed to create backup. {e}"}, 500            
        
def delete_schedule():
    schedule_name = request.args.get("name")
    if not schedule_name:
        return {"message": "Schedule name is required as a query parameter"}

    outcome = velero_api.delete_schedule(schedule_name)
    status = outcome["status"]
    message = outcome["message"]

    if status:
        return {"message": f"Schedule {schedule_name} deleted successfully"}, 200
    else: 
        return {"message": f"Schedule {schedule_name} failed to delete. {message}"}, 500


# DescribeSchedule related function
def describe_schedule():
    schedule_name = request.args.get("name")
    if not schedule_name:
        return {"message": "Schedule name is required as a query parameter"}

    output = velero_api.get_schedule_describe(schedule_name)

    return {"logs": output}
