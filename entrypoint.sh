#!/bin/bash
set -e

if [[ -n "$CLOUDFLARED_TOKEN" ]]; then
  cloudflared tunnel run --token "$CLOUDFLARED_TOKEN" &
fi

exec python3 ics_fixer.py --host 0.0.0.0
