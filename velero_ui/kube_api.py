from kubernetes import client, config
from kubernetes.client.rest import ApiException


import os
import logging

logger = logging.getLogger(__name__)
    
# Check authentication
def auth():
    # Create the Kubernetes API client
    try:
        config.load_incluster_config()
        logger.debug("Authenticate using incluster config")
    except config.config_exception.ConfigException:
        try:
            logger.debug("Authenticate using kubeconfig")
            config.load_kube_config()
        except config.config_exception.ConfigException as e:
            logger.debug("Authentication is failed!")
            logger.error(f"Could not load kube config: {str(e)}")
            raise
    
    try:
      configuration = client.ApiClient().configuration
      logger.info("Kube API server is running at: " + configuration.host)
      logger.info("Authentication is succesful!")
          
    except ApiException as e:
        # Catch specific API exceptions related to authentication issues
        if e.status == 403:
            logger.error("Unauthorized: Access forbidden (403)")
        else:
            logger.error(f"API Exception: {e}")
        
        return False

    except Exception as e:
        logger.error(f"Exception: {e}")
        return False

def get_namespace():
    current_namespace = f"default"

    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            current_namespace = f.read().strip()
    except FileNotFoundError:
        current_namespace = os.environ.get('VELERO_NAMESPACE', 'default')
    
    return current_namespace
