#!/bin/bash
set -e

if [[ -n "$CLOUDFLARED_TOKEN" ]]; then
  cloudflared tunnel run --token "$CLOUDFLARED_TOKEN" &
fi

exec gunicorn -b 0.0.0.0:8000 ics_fixer:application
