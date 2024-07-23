
import yaml
import configparser
import gzip
from io import BytesIO
import base64
import logging
from velero_ui.kube_api import get_namespace

from kubernetes import client

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def download_file_from_minio(endpoint_url, access_key, secret_key, bucket_name, file_key):
    # Initialize the S3 client with custom endpoint URL
    s3 = boto3.client('s3',
                      endpoint_url=endpoint_url,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    
    # Make sure file exists
    try:
        s3.head_object(Bucket=bucket_name, Key=file_key)
        logger.debug(f"File '{file_key}' exists in bucket '{bucket_name}'")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.error(f"File '{file_key}' does not exist in bucket '{bucket_name}'")
            return None
        else:
            # Handle other potential errors
            logger.error(f"An error occurred: {e}")
            return None

    # Download file
    try:
        # Download the file from MinIO bucket to a BytesIO buffer
        file_content = BytesIO()
  
        logger.debug(f"Download " + file_key + " from " + endpoint_url)
        s3.download_fileobj(bucket_name, file_key, file_content)

        # Go to the beginning of the buffer before reading
        file_content.seek(0)
        with gzip.GzipFile(fileobj=BytesIO(file_content.read())) as f:
            decompressed_content = f.read()

        return decompressed_content.decode('utf-8')  # Assuming the file is UTF-8 encoded
    except Exception as e:
        logger.error(f"Error printing file content: {e}")
        return f"Failed to retrieve file {file_key} in {endpoint_url}"

def parse_config_string(config_str):
    config = configparser.ConfigParser()
    config.read_string(config_str)

    # Access the 'default' section values only
    if 'default' in config:
        credentials = {
            'aws_access_key_id': config.get('default', 'aws_access_key_id'),
            'aws_secret_access_key': config.get('default', 'aws_secret_access_key')
        }
        return credentials
    else:
        return None
    

def get_backup_name(yaml_content):
    try:
        # Attempt to load YAML content
        data  = yaml.safe_load(yaml_content)
        if 'metadata' in data:
            if 'name' in data['metadata']:
                return data['metadata']['name']
        return ""
    except yaml.YAMLError as exc:
        logger.error(f"YAML Error: {exc}")
        return ""

def is_valid_schedule_yaml(yaml_content):
    try:
        # Attempt to load YAML content
        data  = yaml.safe_load(yaml_content)
        if 'apiVersion' in data and 'kind' in data:
            if data['kind'] == 'Schedule':
                return True
            else:
                logger.error(f"kind is not Schedule")
                return False
        else:
            logger.error(f"Missing apiVersion and/or kind")
            return False
    except yaml.YAMLError as exc:
        logger.error(f"YAML Error: {exc}")
        return False  # Invalid YAML

def is_valid_backup_yaml(yaml_content):
    try:
        # Attempt to load YAML content
        data  = yaml.safe_load(yaml_content)
        if 'apiVersion' in data and 'kind' in data:
            if data['kind'] == 'Backup':
                return True
            else:
                logger.error(f"kind is not Backup")
                return False
        else:
            logger.error(f"Missing apiVersion and/or kind")
            return False
    except yaml.YAMLError as exc:
        logger.error(f"YAML Error: {exc}")
        return False  # Invalid YAML

def find_backup_from_name(backup_name):
    backupListResponse = client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="backups")
    backupList = backupListResponse.get('items', [])

    for backup in backupList:
        if backup["metadata"]["name"] == backup_name:
            return backup

    logger.error(f"Backup {backup_name} not found")
    return None

def find_restore_from_name(restore_name):
    restoreListResponse = client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="restores")
    restoreList = restoreListResponse.get('items', [])

    for restore in restoreList:
        if restore["metadata"]["name"] == restore_name:
            return restore

    logger.error(f"Restore {restore_name} not found")
    return None
    


def find_backup_storageLocation(backupName):
    backupLocationsResponse = client.CustomObjectsApi().list_namespaced_custom_object(group="velero.io", version="v1", namespace="velero", plural="backupstoragelocations")  
    backupLocations = backupLocationsResponse.get('items', [])
    
    if len(backupLocations) == 0:
        logger.error(f"No backup storage found")
        return "", "", "", "", ""

    try:
        backup = find_backup_from_name(backupName)
        if backup:
            toFindBackupLocationbackup = backup["spec"]["storageLocation"]

            for backupLocation in backupLocations:
                if backupLocation["metadata"]["name"] == toFindBackupLocationbackup:
                    spec = backupLocation["spec"]
                    
                    if "s3Url" in spec["config"]:
                        minio_endpoint = backupLocation["spec"]["config"]["s3Url"]
                    else:
                        raise Exception(f"Only support S3 backup storage. Cannot find S3 URL in backup location {str(backupLocation)} of backup {str(backup)}")
                    
                    if "bucket" in spec["objectStorage"]:
                        bucket_name = backupLocation["spec"]["objectStorage"]["bucket"]
                    else:
                        raise Exception(f"Only support S3 backup storage. Cannot find bucket name object storage configuration {str(backupLocation)} of backup {str(backup)}")
                    
                    if "prefix" in spec["objectStorage"]:
                        file_prefix = backupLocation["spec"]["objectStorage"]["prefix"]
                    else:
                        file_prefix = ""

                    secret_name = get_cloud_secret_credential()
                    if secret_name:    
                        secret = client.CoreV1Api().read_namespaced_secret(secret_name, get_namespace())
                        secret_data = base64.b64decode(secret.data["cloud"]).decode('utf-8')
                        parsed = parse_config_string(secret_data)
                    
                        access_key = parsed["aws_access_key_id"]
                        secret_key = parsed["aws_secret_access_key"]
                    else:
                        raise Exception(f"Only support S3 backup storage. Cannot find S3 credential {str(backupLocation)} of backup {str(backup)}")

                    return minio_endpoint, bucket_name, file_prefix, access_key, secret_key
        else:
            logger.error(f"No Velero backup found")
            return "", "", "", "", ""
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        
    logger.error(f"Fail to find backup location for {backupName}")
    return "", "", "", "", ""


def get_cloud_secret_credential():
    deployment = client.AppsV1Api().read_namespaced_deployment("velero", get_namespace())

    # Extract the volumes from the deployment spec
    volumes = deployment.spec.template.spec.volumes

    for volume in volumes:
        # Check if the volume is of type 'secret'
        if volume.name == "cloud-credentials" and volume.secret:
            return volume.secret.secret_name
        
    logger.error(f"Fail to look for mountned secret with name cloud-credentials to velero deployment")
    return ""



def parse_describe_response(response):
  formatted_output = f""
  for key, value in response.items():
      if isinstance(value, dict):
          formatted_output += f"{key}:\n"
          for inner_key, inner_value in value.items():
              formatted_output += f"  {inner_key}: {inner_value}\n"
      else:
          formatted_output += f"{key}: {value}\n"
  return formatted_output        