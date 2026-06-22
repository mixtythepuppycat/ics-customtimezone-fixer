FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ics_fixer.py ./
COPY custom_timezone ./
COPY entrypoint.sh ./

RUN pip install --no-cache-dir gunicorn \
    && chmod +x /app/entrypoint.sh \
    && curl -L -o /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/cloudflared.deb \
    && rm -rf /var/lib/apt/lists/* /tmp/cloudflared.deb

ENTRYPOINT ["/app/entrypoint.sh"]
