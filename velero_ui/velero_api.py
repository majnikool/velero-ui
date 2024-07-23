from kubernetes import client
from velero_ui.kube_api import get_namespace

import logging

from velero_ui.velero_api_utils import *

logger = logging.getLogger(__name__)

def delete_schedule(name):
    try:
        api_client = client.ApiClient()
        api_instance = client.CustomObjectsApi(api_client)
        res =  api_instance.delete_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace = get_namespace(),
            plural="schedules",  # Use the appropriate resource type
            name=name,
        )

        logger.info(f"Delete schedule: {name}")
        logger.debug(f"Delete schedule: {res}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return {"status": False, "message": str(e)}
    
    return {"status": True, "message": ""}

def delete_restore(restoreName):
    try:
        api_client = client.ApiClient()
        api_instance = client.CustomObjectsApi(api_client)
        res =  api_instance.delete_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace = get_namespace(),
            plural="restores",  # Use the appropriate resource type
            name=restoreName,
        )

        logger.info(f"Delete restore: {restoreName}")
        logger.debug(f"Delete restore: {res}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return {"status": False, "message": str(e)}
    
    return {"status": True, "message": ""}

def create_backup_delete_request(backupName):
    delete_request = {
        "apiVersion": "velero.io/v1",
        "kind": "DeleteBackupRequest",
        "metadata": {
            "name": f"{backupName}-delete-request"  # Change this to your CRD name
        },
        "spec": {
            "backupName": f"{backupName}"
        }
    }

    try:
        api_client = client.ApiClient()
        api_instance = client.CustomObjectsApi(api_client)
        res =  api_instance.create_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace = get_namespace(),
            plural="deletebackuprequests",  # Use the appropriate resource type
            body=delete_request,
        )

        logger.info(f"Delete backup request is created for backup: {backupName}")
        logger.debug(f"Delete backup request is created: {res}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return {"status": False, "message": str(e)}
    
    return {"status": True, "message": ""}


def create_schedule(data):
    try:
        api_client = client.ApiClient()
        api_instance = client.CustomObjectsApi(api_client)
        res =  api_instance.create_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace = get_namespace(),
            plural="schedules",  # Use the appropriate resource type
            body=data,
        )

        logger.info(f"Schedule created: {res}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return {"status": False, "message": str(e)}
    
    return {"status": True, "message": ""}

def create_backup(data):
    try:
        api_client = client.ApiClient()
        api_instance = client.CustomObjectsApi(api_client)
        res =  api_instance.create_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace = get_namespace(),
            plural="backups",  # Use the appropriate resource type
            body=data,
        )

        logger.info(f"Backup created: {res}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return {'status': False, 'message': str(e)}
    
    return {"status": True, "message": ""}

def create_restore(backupName):
    restore_request = {
        "apiVersion": "velero.io/v1",
        "kind": "Restore",
        "metadata": {
            "name": f"{backupName}-restore",
            "namespace": "velero",
        },
        "spec": {
            "backupName": f"{backupName}",
            "restorePVs": True
        }
    }

    try:
        api_client = client.ApiClient()
        api_instance = client.CustomObjectsApi(api_client)
        res =  api_instance.create_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace = get_namespace(),
            plural="restores",  # Use the appropriate resource type
            body=restore_request,
        )

        logger.info(f"Restore created: {res}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return {"status": False, "message": str(e)}
    
    return {"status": True, "message": ""}

def get_storage_list():
    return client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="backupstoragelocations") 

def get_schedule_list():
    return client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="schedules") 

def get_backup_list():
    return client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="backups")

def get_restore_list():
    return client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="restores")

def get_schedule_describe(name):
  schedule_list_response = client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="schedules")
  schedule_list = schedule_list_response.get('items', [])

  for schedule in schedule_list:
      if schedule["metadata"]["name"] == name:
          res = client.CustomObjectsApi().get_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="schedules", name=name)
          return parse_describe_response(res)
      
  return ""

def get_restore_describe(name):
  restoreListResponse = client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="restores")
  restoreList = restoreListResponse.get('items', [])

  for restore in restoreList:
    if restore["metadata"]["name"] == name:
      res = client.CustomObjectsApi().get_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="restores", name=name)
      return parse_describe_response(res)
    
  return ""    

def get_backup_describe(name):
  backupListResponse = client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="backups")
  backupList = backupListResponse.get('items', [])

  for backup in backupList:
    if backup["metadata"]["name"] == name:
      res = client.CustomObjectsApi().get_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="backups", name=name)
      return parse_describe_response(res)
    
  return ""

def get_restore_log(name):
    # Make sure backup is not in progress 
    restore = find_restore_from_name(name)
    phase = restore["status"]["phase"]

    if  phase == "New" or phase == "InProgress":
        return f"Restore is in {phase} phase. Please wait until the restore is finished to retrieve log again"
    
    backup_name = restore["spec"]["backupName"]

    minio_endpoint, bucket_name, file_prefix, access_key, secret_key = find_backup_storageLocation(backup_name)
    file_name = "restore-" + name + "-logs.gz"

    if minio_endpoint:
        if file_prefix:
            file_key = file_prefix + "/restores/" + name + "/" + file_name
        else:
            file_key = "restores/" + name + "/" + file_name

        return download_file_from_minio(endpoint_url=minio_endpoint, access_key=access_key, secret_key=secret_key, bucket_name=bucket_name, file_key=file_key)
    else:
        logger.debug("Cannot retrieve backup storage location")
        return "Cannot retrieve backup storage location"
    
def get_backup_log(name):
    # Make sure backup is not in progress 
    backup = find_backup_from_name(name)
    phase = backup["status"]["phase"]

    if  phase == "New" or phase == "InProgress":
        return f"Backup is in {phase} phase. Please wait until the backup is finished to retrieve log again"
    
    # Get backup location
    minio_endpoint, bucket_name, file_prefix, access_key, secret_key = find_backup_storageLocation(name)
    file_name = name + "-logs.gz"

    if minio_endpoint:    
        if file_prefix:
            file_key = file_prefix + "/backups/" + name + "/" + file_name
        else:
            file_key = "backups/" + name + "/" + file_name

        return download_file_from_minio(endpoint_url=minio_endpoint, access_key=access_key, secret_key=secret_key, bucket_name=bucket_name, file_key=file_key)
    else:
        logger.debug("Cannot retrieve backup storage location")
        return "Cannot retrieve backup storage location"


