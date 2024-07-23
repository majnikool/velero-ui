from flask import request, session, redirect, url_for, render_template, send_from_directory


# User related imports
from velero_ui.user import user_list_get, user_list_post, user_list_delete, change_password_post, check_password

# Backup related imports
from velero_ui.backup import get_backup_list, create_backup, delete_backup, get_backup_logs, describe_backup

# Restore related imports
from velero_ui.restore import get_restore_list, create_restore, delete_restore, get_restore_logs, describe_restore

# Schedule related imports
from velero_ui.schedule import get_schedules, create_schedule, delete_schedule, describe_schedule

# Storage related imports
from velero_ui.storage import get_storages


def configure_routes(app, api, api_version, use_auth):
    @app.before_request
    def check_authentication():
        if request.path.startswith("/static/"):
            return
        if request.path == "/login":
            return
        if use_auth and "username" not in session:
            return redirect(url_for("login"))

    @app.route("/")
    def serve_index():
        return render_template("index.html", use_auth=use_auth)

    @app.route("/navbar")
    def serve_navbar():
        return render_template("navbar.html", use_auth=use_auth, app_version=api_version)

    @app.route("/backup")
    def serve_backup():
        return render_template("backup.html", use_auth=use_auth)

    @app.route("/restore")
    def serve_restore():
        return render_template("restore.html", use_auth=use_auth)

    @app.route("/schedule")
    def serve_schedule():
        return render_template("schedule.html", use_auth=use_auth)

    @app.route("/settings")
    def serve_settings():
        return render_template("settings.html", use_auth=use_auth)

    @app.route("/change-password")
    def serve_change_password():
        return render_template("change-password.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            if check_password(username, password):
                session["username"] = username
                return {"success": True}, 200
            else:
                return {"success": False, "message": "Invalid username or password"}, 401
        else:
            return render_template("login.html")

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.pop("username", None)
        return redirect(url_for("login"))

    @app.route("/static/<path:path>")
    def serve_static(path):
        if path.endswith(".js"):
            mimetype = "application/javascript"
        elif path.endswith(".css"):
            mimetype = "text/css"
        else:
            mimetype = None
        return send_from_directory(app.static_folder, path, mimetype=mimetype)

    @app.route("/templates/<path:template_name>")
    def serve_templates(template_name):
        return render_template(template_name)

    # User routes
    app.route('/users', methods=['GET'])(user_list_get)
    app.route('/users', methods=['POST'])(user_list_post)
    app.route('/users', methods=['DELETE'])(user_list_delete)
    app.route('/change-password', methods=['POST'])(change_password_post)

    # Backup routes
    app.route('/backups', methods=['GET'])(get_backup_list)
    app.route('/backups', methods=['POST'])(create_backup)
    app.route('/backups', methods=['DELETE'])(delete_backup)
    app.route('/backups/logs', methods=['GET'])(get_backup_logs)
    app.route('/backups/describe', methods=['GET'])(describe_backup)

    # Restore routes
    app.route('/restores', methods=['GET'])(get_restore_list)
    app.route('/restores', methods=['POST'])(create_restore)
    app.route('/restores', methods=['DELETE'])(delete_restore)
    app.route('/restores/logs', methods=['GET'])(get_restore_logs)
    app.route('/restores/describe', methods=['GET'])(describe_restore)

    # Schedule routes
    app.route('/schedules', methods=['GET'])(get_schedules)
    app.route('/schedules', methods=['POST'])(create_schedule)
    app.route('/schedules', methods=['DELETE'])(delete_schedule)
    app.route('/schedules/describe', methods=['GET'])(describe_schedule)

    # Storage routes
    app.route('/storages', methods=['GET'])(get_storages)

