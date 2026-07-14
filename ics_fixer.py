#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
import icalendar
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server

def add_missing_timezones(ics_text: str) -> str:
    calendar = icalendar.Calendar.from_ical(ics_text)
    calendar.add_missing_timezones()
    return calendar.to_ical().decode("utf-8")

def safe_decode(content: bytes, charset: str | None = None) -> str:
    if charset:
        try:
            return content.decode(charset, errors="replace")
        except LookupError:
            pass
    try:
        return content.decode("utf-8", errors="replace")
    except Exception:
        return content.decode("latin-1", errors="replace")



def replace_custom_timezone_tzid(ics_text: str, timezone_id: str) -> str:
    if not timezone_id:
        return ics_text

    pattern = re.compile(r"(?<=TZID(?:=|:))Customized Time Zone\b", re.IGNORECASE)
    return pattern.sub(timezone_id, ics_text)


def validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use http:// or https://")
    return value


def fetch_ics(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "ics-customtimezone-fixer/1.0",
            "Accept": "text/calendar,application/octet-stream,*/*",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            raw_data = response.read()
            charset = response.headers.get_content_charset()
            return safe_decode(raw_data, charset)
    except HTTPError as exc:
        raise RuntimeError(f"Failed to fetch ICS file: HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch ICS file: {exc.reason}") from exc


def validate_api_key(query: dict[str, list[str]]) -> None:
    expected = os.getenv("ICS_FIXER_API_KEY")
    provided = query.get("api_key") or []

    if not expected:
        raise RuntimeError("Server misconfiguration: missing ICS_FIXER_API_KEY environment variable")

    if not provided or provided[0] != expected:
        raise ValueError("Unauthorized: invalid or missing api_key")


def application(environ, start_response):
    query = parse_qs(environ.get("QUERY_STRING", ""))
    url_values = query.get("url") or []
    customsub_values = query.get("customsub") or ["Pacific Standard Time"]

    if not url_values:
        start_response("400 Bad Request", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Missing required query parameter: url"]

    try:
        validate_api_key(query)
        input_url = validate_url(url_values[0])
        calendar_text = fetch_ics(input_url)
        updated_calendar = calendar_text
        customsub_value = customsub_values[0].strip() if customsub_values else ""
        if customsub_value:
            updated_calendar = replace_custom_timezone_tzid(updated_calendar, customsub_value)

        # Load into icalendar to add any missing time zones
        updated_calendar = add_missing_timezones(updated_calendar)
        
        headers = [
            ("Content-Type", "text/calendar; charset=utf-8"),
            ("Content-Disposition", "attachment; filename=customized.ics"),
            ("Content-Length", str(len(updated_calendar.encode("utf-8")))),
        ]
        start_response("200 OK", headers)
        return [updated_calendar.encode("utf-8")]
    except ValueError as exc:
        start_response("401 Unauthorized", [("Content-Type", "text/plain; charset=utf-8")])
        return [str(exc).encode("utf-8")]
    except RuntimeError as exc:
        start_response("502 Bad Gateway", [("Content-Type", "text/plain; charset=utf-8")])
        return [str(exc).encode("utf-8")]


def run_server(host: str, port: int) -> None:
    print(f"Starting ICS fixer on http://{host}:{port}/")
    print("Send GET requests like: http://<host>:<port>/?url=https://example.com/calendar.ics&api_key=<key>")
    with make_server(host, port, application) as server:
        server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a simple ICS fixer service that appends the custom_timezone block to an ICS file."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    try:
        run_server(args.host, args.port)
        return 0
    except KeyboardInterrupt:
        print("Shutting down.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
