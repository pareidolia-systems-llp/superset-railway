import os
from urllib.parse import quote_plus


# ---------------------------------------------------------
# Security
# ---------------------------------------------------------

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

ENABLE_PROXY_FIX = True


# ---------------------------------------------------------
# Superset Metadata Database
# ---------------------------------------------------------

db_user = os.environ["SUPERSET_DB_USER"]
db_password = quote_plus(os.environ["SUPERSET_DB_PASSWORD"])
db_host = os.environ["SUPERSET_DB_HOST"]
db_port = os.environ.get("SUPERSET_DB_PORT", "3306")
db_name = os.environ.get("SUPERSET_DB_NAME", "superset_metadata")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+mysqldb://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}"
    "?charset=utf8mb4"
)


# ---------------------------------------------------------
# Dashboard Features
# ---------------------------------------------------------

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}


# ---------------------------------------------------------
# Lightweight cache for initial deployment
# ---------------------------------------------------------

CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
}

DATA_CACHE_CONFIG = CACHE_CONFIG


# ---------------------------------------------------------
# SQL Lab
# ---------------------------------------------------------

SQLLAB_CTAS_NO_LIMIT = True

# ---------------------------------------------------------
# Custom Project Tracker Actions
# ---------------------------------------------------------

from flask import render_template_string
from flask_appbuilder import BaseView, expose
from flask_appbuilder.security.decorators import has_access
from flask_wtf import FlaskForm
from wtforms import SubmitField

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class ProjectTrackerSyncForm(FlaskForm):
    submit = SubmitField("Sync Now")


class ProjectTrackerSyncView(BaseView):

    route_base = "/project-tracker-sync"
    default_view = "index"

    @expose("/", methods=["GET", "POST"])
    @has_access
    def index(self):

        form = ProjectTrackerSyncForm()

        message = None
        success = None

        if form.validate_on_submit():

            sync_url = os.environ["PROJECT_TRACKER_SYNC_URL"]
            sync_key = os.environ["PROJECT_TRACKER_SYNC_KEY"]

            request = Request(
                sync_url,
                method="POST",
                headers={
                    "X-Refresh-Key": sync_key,
                    "Accept": "text/plain",
                },
            )

            try:

                with urlopen(request, timeout=120) as response:

                    response_body = (
                        response
                        .read()
                        .decode("utf-8", errors="replace")
                        .strip()
                    )

                    success = 200 <= response.status < 300

                if success:
                    message = (
                        "Project Tracker data synchronized successfully. "
                        "The latest project data and dashboard KPIs have been updated."
                    )
                else:
                    message = (
                        response_body
                        or "Synchronization could not be completed."
                    )

            except HTTPError as ex:

                success = False

                response_body = (
                    ex.read()
                    .decode("utf-8", errors="replace")
                    .strip()
                )

                message = (
                    response_body
                    or f"Synchronization failed. HTTP {ex.code}"
                )

            except URLError:

                success = False

                message = (
                    "Could not connect to the Project Tracker backend."
                )

            except Exception:

                success = False

                message = (
                    "Synchronization failed unexpectedly. "
                    "Please contact the administrator."
                )

        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Project Tracker Sync</title>

                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background: #f7f8fa;
                        margin: 0;
                        padding: 50px;
                    }

                    .sync-card {
                        max-width: 600px;
                        margin: auto;
                        background: white;
                        padding: 32px;
                        border-radius: 10px;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.10);
                    }

                    h2 {
                        margin-top: 0;
                    }

                    .description {
                        margin-bottom: 24px;
                        line-height: 1.5;
                    }

                    .sync-button {
                        padding: 10px 22px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        background: #20a7c9;
                        color: white;
                        font-size: 15px;
                    }

                    .success {
                        margin-top: 24px;
                        padding: 14px;
                        border-radius: 5px;
                        background: #e8f5e9;
                    }

                    .error {
                        margin-top: 24px;
                        padding: 14px;
                        border-radius: 5px;
                        background: #ffebee;
                    }
                    
                    .dashboard-button {
                        display: inline-block;
                        margin-top: 18px;
                        padding: 10px 22px;
                        border-radius: 5px;
                        background: #5b6470;
                        color: white;
                        text-decoration: none;
                        font-size: 15px;
                    }

                    .dashboard-button:hover {
                        opacity: 0.9;
                    }

                    .note {
                        margin-top: 20px;
                        font-size: 13px;
                    }
                </style>
            </head>

            <body>

                <div class="sync-card">

                    <h2>Project Tracker Manual Sync</h2>

                    <div class="description">
                        Synchronize the latest Project Tracker data
                        from Google Sheets and rebuild the affected
                        dashboard KPIs.
                    </div>

                    <form method="POST">

                        {{ form.hidden_tag() }}

                        <button
                            class="sync-button"
                            type="submit">
                            Sync Now
                        </button>

                        </form>
                        {% if message %}

                            <div class="{{ 'success' if success else 'error' }}">
                                {{ message }}
                            </div>

                            {% if success %}

                                <a
                                    href="/superset/dashboard/2/"
                                    class="dashboard-button">
                                    Return to Dashboard
                                </a>

                            {% endif %}

                        {% endif %}
                    {% if not success %}
                        <div class="note">
                            Please wait for the synchronization to complete before refreshing the dashboard.
                        </div>
                        {% endif %}

                </div>

            </body>
            </html>
            """,
            form=form,
            message=message,
            success=success,
        )


# ---------------------------------------------------------
# Flask App Customization
# ---------------------------------------------------------

def FLASK_APP_MUTATOR(app):

    from superset.extensions import appbuilder

    app_root = (
        app.config.get("APPLICATION_ROOT") or ""
    ).rstrip("/")

    # Existing Change Password navigation
    appbuilder.add_link(
        "Change Password",
        label="Change Password",
        href=f"{app_root}/resetmypassword/form",
        icon="fa-key",
        category="",
    )

    # Secure Manual Sync page
    appbuilder.add_view(
        ProjectTrackerSyncView(),
        "Manual Sync",
        icon="fa-refresh",
        category="",
    )
