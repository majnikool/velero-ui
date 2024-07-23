import json
import velero_ui.velero_api as velero_api
import yaml
import logging

from flask import request, jsonify

logger = logging.getLogger(__name__)

# Function for getting the list of backups
def get_backup_list():
    backups = json.dumps(velero_api.get_backup_list())
    return jsonify(backups)

# Function for creating a backup
def create_backup():
    try: 
        data = request.get_json()
        logger.debug(f"Incoming request from frontend: {data}")

        backup_request = {
            "apiVersion": "velero.io/v1",
            "kind": "Backup",
            "metadata": {
                "name": f"{data["metadata_name"]}",
                "namespace": "velero",
            },
            "spec": {
                "includedNamespaces": data["spec_includedNamespaces"],
                "ttl": f"{data["spec_ttl"]}",
                "storageLocation": "default",
                "defaultVolumesToFsBackup": True
            }
        }

        spec_labels = data["spec_labels"]
        
        if len(spec_labels) > 0 and len(spec_labels[0]) > 0:
            matchLabels = {}
            for label in spec_labels:
                if label and len(label) > 0:
                    splited_label = label.split('=')

                    if len(splited_label) > 1:
                        key = splited_label[0]
                        value = splited_label[1]

                        if key and len(key) > 0:
                            matchLabels[key] = value
                        else:
                            return {"message": f"Failed to create backup. Labels are not following the format <key>=<value>. Key cannot be empty"}, 500
                    else:
                        return {"message": f"Failed to create backup. Labels are not following the format <key>=<value>,<key>=<value>..."}, 500
                        
                

            if len(matchLabels) > 0:  
                backup_request['spec']['labelSelector'] = {"matchLabels" : matchLabels}

        outcome = velero_api.create_backup(backup_request)

        status = outcome["status"]
        message = outcome["message"]
        
        if status:
            return {"message": f"Backup {data["metadata_name"]} created successfully"}, 200
        else:
            raise Exception(f"{message}")
    
    except Exception as e:
        logger.error(e)
        return {"message": f"Failed to create backup. {e}"}, 500
    

def delete_backup():
    
    backup_name = request.args.get("name")
    if not backup_name:
        return {"message": "Backup name is required as a query parameter"}

    outcome = velero_api.create_backup_delete_request(backup_name)
    status = outcome["status"]
    message = outcome["message"]

    if status:
      return {"message": f"Backup {backup_name} deleted successfully"}, 200
    else: 
      return {"message": f"Backup {backup_name} failed to delete. {message}"}, 500

# Function to get logs for a backup
def get_backup_logs():
    backup_name = request.args.get("name")
    if not backup_name:
        return {"message": "Backup name is required as a query parameter"}

    output = velero_api.get_backup_log(backup_name)

    return {"logs": output}

# Function to describe a backup
def describe_backup():
    backup_name = request.args.get("name")
    if not backup_name:
        return {"message": "Backup name is required as a query parameter"}

    output = velero_api.get_backup_describe(backup_name)

    return {"logs": output}
