# Velero-UI Helm Chart

## Introduction

**Velero-UI** is a web-based graphical user interface for Velero. Velero is an open-source tool designed to back up and restore Kubernetes resources, making it easier to manage your Kubernetes cluster. Velero-UI extends Velero's functionality by providing a user-friendly interface to interact with Velero's capabilities.

## Getting Started

### Prerequisites

- A Kubernetes cluster with Velero installed. For installation instructions, visit the [official Velero installation guide](https://velero.io/docs/main/basic-install/).

### Features

Velero-UI offers a comprehensive set of features for Kubernetes resource management, including:

- **Backup and Restore:** Facilitate the backup and restoration of Kubernetes resources.
- **Logs and Status View:** Access detailed logs and monitor the status of backups and restores.
- **Scheduled Backups:** Set up and manage backup schedules.

## Local development 

Local run of Velero UI against cluster having Velero. All code change will be hot reloaded

### Requirement

```
# Dependency
python 3.12.1
poetry 1.7.1

# Example
# Install python and pipx
# asdf install
# Install poetry
# pipx install poetry==1.7.1
# poetry env use $(which python)

```
Make sure the local `~/.kube/config` is pointing correct cluster


### Steps
```
# Install dependency
poetry install

# Start local Flask server. App will start on local at port 5000 (in run.py)
poetry run flask run
```

## Deployment
### Prepare .flaskenv

Create `.flaskenv` file in project root folder with content
```
SECRET_KEY=your_secret_key
FLASK_APP= run.py
FLASK_DEBUG=1
LOG_LEVEL=DEBUG
FLASK_CONFIG=dev
VELERO_NAMESPACE=velero
REMEMBER_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax#    
```


### Build docker image
```
DOCKER_BUILDKIT=1 docker image build . -f Dockerfile --build-arg DEPLOYMENT_ENV="production" --tag majidni/veleroui:0.0.1-poetry
docker push majidni/veleroui:0.0.1-poetry
```

### Standalone Docker Deployment

To run Velero-UI as a standalone Docker container :

```bash
docker run -d --restart always --name veleroui_container \
  -e KUBECONFIG=/root/.kube/config \
  -e VELERO_NAMESPACE=<Namespace_Where_Velero_Is_Installed> \
  -p <host_port>:5000 \
  -v ~/.kube/config:/root/.kube/config \
  majidni/veleroui:0.0.1-poetry

```

command options:

1. `-d`: Runs the container in detached mode. This means the container runs in the background and does not block your terminal or command prompt.

2. `--restart always`: This option ensures that the Docker container automatically restarts if it stops. If the container stops for any reason (such as a Docker daemon restart or a system reboot), it will be restarted.

3. `--name veleroui_container`: Assigns a custom name (`veleroui_container`) to the container. This is useful for identifying and managing the container with Docker commands.

4. `-e KUBECONFIG=/root/.kube/config`: Sets an environment variable `KUBECONFIG` inside the container.

5. `-p <host_port>:5000`: Maps a port on the host machine (`<host_port>`) to port 5000 inside the container. If your application inside the container listens on port 5000, this makes it accessible via `<host_port>` on your host machine.

6. `-v ~/.kube/config:/root/.kube/config`: Mounts a volume from your host machine (`~/.kube/config`) to a location inside the container (`/root/.kube/config`). Make sure the path on the host side is correctly pointing to your kubeconfig file.

### Kubernetes deployment
Refer to the included Helm chart for deploying Velero-UI on your Kubernetes cluster. The Helm chart simplifies the deployment and configuration process, making it straightforward to integrate Velero-UI into your Kubernetes environment.

When deploying on Kubernetes cluster, Velero UI uses service account to fetch backup information 