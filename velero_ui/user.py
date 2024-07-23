import bcrypt
import base64
from kubernetes import client
from flask import request, jsonify
from velero_ui.kube_api import get_namespace

def get_user_secret(username):
    namespace = get_namespace()
    try:
        return client.CoreV1Api().read_namespaced_secret(username, namespace)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return None
        raise e

def create_user_secret(username, password):
    namespace = get_namespace()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    secret_data = {"password": base64.b64encode(hashed_password).decode('utf-8')}

    secret = client.V1Secret(
        api_version="v1",
        kind="Secret",
        metadata=client.V1ObjectMeta(name=username, namespace=namespace),
        type="Opaque",
        data=secret_data
    )

    client.CoreV1Api().create_namespaced_secret(namespace, secret)

def update_user_password(username, password):
    namespace = get_namespace()
    secret = get_user_secret(username)
    if not secret:
        return False

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    secret.data = {"password": base64.b64encode(hashed_password).decode('utf-8')}

    client.CoreV1Api().replace_namespaced_secret(username, namespace, secret)
    return True

def delete_user_secret(username):
    namespace = get_namespace()
    try:
        client.CoreV1Api().delete_namespaced_secret(username, namespace)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return False
        raise e
    return True

def list_users():
    namespace = get_namespace()
    secrets = client.CoreV1Api().list_namespaced_secret(namespace)
    users = [secret.metadata.name for secret in secrets.items if secret.type == "Opaque"]
    return users

def check_password(username, password):
    secret = get_user_secret(username)
    if not secret:
        return False

    hashed_password = base64.b64decode(secret.data["password"])
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def is_admin_user(username):
    return username == 'admin'

def create_admin_user_if_not_exists():
    if get_user_secret("admin") is None:
        create_user_secret("admin", "admin")

# Flask-Restful functions
def user_list_get():
    users = list_users()
    return jsonify(users)

def user_list_post():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Username and password are required as JSON properties in the request body"}, 400

    if get_user_secret(username) is not None:
        return {"message": f"User '{username}' already exists"}, 400

    create_user_secret(username, password)
    return {"message": f"User '{username}' created successfully"}

def user_list_delete():
    username = request.args.get("username")

    if not username:
        return {"message": "Username is required as a query parameter"}, 400

    if not delete_user_secret(username):
        return {"message": f"User '{username}' not found"}, 404

    return {"message": f"User '{username}' deleted successfully"}

def change_password_post():
    data = request.get_json()
    username = data.get("username")
    old_password = data.get("oldPassword")
    new_password = data.get("newPassword")

    if not username or not old_password or not new_password:
        return {"message": "Username, oldPassword, and newPassword are required as JSON properties in the request body"}, 400

    if not check_password(username, old_password):
        return {"message": "Incorrect username or old password"}, 403

    if not update_user_password(username, new_password):
        return {"message": f"User '{username}' not found"}, 404

    return {"message": f"Password for user '{username}' updated successfully"}
