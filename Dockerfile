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

COPY superset_config.py /app/pythonpath/superset_config.py

ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

USER superset

CMD ["/bin/bash", "-c", "superset db upgrade && superset init && exec gunicorn --bind 0.0.0.0:${PORT:-8088} --workers 1 --threads 4 --timeout 180 'superset.app:create_app()'"]