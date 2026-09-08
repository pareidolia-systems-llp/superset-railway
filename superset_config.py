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
# Custom User Menu
# ---------------------------------------------------------

def FLASK_APP_MUTATOR(app):
    from superset.extensions import appbuilder

    appbuilder.add_link(
        "Change Password",
        href="/resetmypassword/form",
        label="Change Password",
        icon="fa-key",
        category="User",
        category_label="User",
    )