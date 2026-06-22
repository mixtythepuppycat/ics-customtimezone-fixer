# ics-customtimezone-fixer

Simple Python web service that fetches an ICS file from a URL, appends the `custom_timezone` block, and returns the modified ICS file.

## Usage

1. Run the service:

```bash
python3 ics_fixer.py
```

2. Send a GET request with the `url` and `api_key` query parameters:

```bash
curl -G --output customized.ics "http://127.0.0.1:8000/" \
  --data-urlencode "url=https://example.com/calendar.ics" \
  --data-urlencode "api_key=$ICS_FIXER_API_KEY"
```

If the app is bound to all interfaces, remote clients can use your host IP or container host address instead of `127.0.0.1`.

Set the API key in the environment before running the service:

```bash
export ICS_FIXER_API_KEY="your-secret-key"
python3 ics_fixer.py
```

3. The response is returned as `text/calendar` and saved as `customized.ics`.

## Notes

- The app reads the timezone block from `custom_timezone` in the repository root.
- Only `http://` and `https://` URLs are accepted.
- Python 3.10+ is recommended because the script uses modern type annotations.

## Docker

Build the image from the repository root:

```bash
docker build -t ics-customtimezone-fixer .
```

Or you can pull the container from the registry:

```bash
docker pull ghcr.io/mixtythepuppycat/ics-customtimezone-fixer:latest
```

Run the container with the API key set:

```bash
docker run --rm -p 8000:8000 -e ICS_FIXER_API_KEY="your-secret-key" ics-customtimezone-fixer
```

Then request a modified ICS file:

```bash
curl -G --output customized.ics "http://127.0.0.1:8000/" \
  --data-urlencode "url=https://example.com/calendar.ics" \
  --data-urlencode "api_key=your-secret-key"
```

If this is being used as part of a flow to share a Microsoft Exchange calendar with Google Calendar, the container needs to be accessible from the public internet. The container has `cloudflared` installed to solve this issue and will run if you provide it with your tunnel's token:

```bash
docker run --rm \
    -e ICS_FIXER_API_KEY="your-secret-key" \
    -e CLOUDFLARED_TOKEN="your-tunnel-token" \
    ghcr.io/mixtythepuppycat/ics-customtimezone-fixer:latest
```
