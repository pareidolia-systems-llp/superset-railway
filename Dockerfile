FROM apache/superset:6.1.0

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       pkg-config \
       default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && . /app/.venv/bin/activate \
    && uv pip install mysqlclient

# Use Pareidolia Tracker icon in the Superset navbar logo slot
COPY assets/tracker-icon.png /app/superset/static/assets/images/superset-logo-horiz.png

# Custom Pareidolia Tracker UI assets
RUN mkdir -p /app/superset/static/custom-assets

COPY assets/tracker-icon.png /app/superset/static/custom-assets/tracker-icon.png
COPY assets/sync-icon.png /app/superset/static/custom-assets/sync-icon.png
COPY assets/password-icon.png /app/superset/static/custom-assets/password-icon.png
COPY custom.css /app/superset/static/custom-assets/custom.css

COPY assets/dashboards_logo.png /app/superset/static/custom-assets/dashboards_logo.png
COPY assets/charts_logo.png /app/superset/static/custom-assets/charts_logo.png
COPY assets/datasets_logo.png /app/superset/static/custom-assets/datasets_logo.png

COPY superset_config.py /app/pythonpath/superset_config.py

ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

USER superset

CMD ["/bin/bash", "-c", "superset db upgrade && superset init && exec gunicorn --bind 0.0.0.0:${PORT:-8088} --workers 1 --threads 4 --timeout 180 'superset.app:create_app()'"]
