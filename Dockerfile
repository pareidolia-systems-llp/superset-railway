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

# Replace the default Superset logo with a transparent image
RUN python -c "from pathlib import Path; import base64; p=Path('/app/superset/static/assets/images/superset-logo-horiz.png'); assert p.exists(), f'Logo asset not found: {p}'; p.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGBgAAAABQABpfZFQAAAAABJRU5ErkJggg=='))"

COPY superset_config.py /app/pythonpath/superset_config.py

ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

USER superset

CMD ["/bin/bash", "-c", "superset db upgrade && superset init && exec gunicorn --bind 0.0.0.0:${PORT:-8088} --workers 1 --threads 4 --timeout 180 'superset.app:create_app()'"]
