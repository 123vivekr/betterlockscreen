#!/usr/bin/env python3

import hmac
import os
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ALLOWED_WALLPAPER_HOSTS = {"wallpapers.example.com"}
MAX_WALLPAPER_BYTES = 20 * 1024 * 1024
MAX_DOWNLOAD_SECONDS = 30
CHUNK_SIZE = 64 * 1024


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def validate_wallpaper_url(wallpaper_url: str) -> str:
    parsed = urlparse(wallpaper_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_WALLPAPER_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
    ):
        raise ValueError("unsupported wallpaper URL")
    return wallpaper_url


def download_wallpaper(wallpaper_url: str, output_path: str) -> None:
    opener = build_opener(NoRedirects())
    request = Request(validate_wallpaper_url(wallpaper_url), headers={"User-Agent": "betterlockscreen"})
    deadline = time.monotonic() + MAX_DOWNLOAD_SECONDS
    cache_dir = os.path.dirname(output_path)
    os.makedirs(cache_dir, exist_ok=True)
    temporary_path = ""

    try:
        with opener.open(request, timeout=5) as response:
            declared_size = response.headers.get("Content-Length")
            if declared_size is not None and int(declared_size) > MAX_WALLPAPER_BYTES:
                raise ValueError("wallpaper is too large")

            with tempfile.NamedTemporaryFile(dir=cache_dir, prefix="remote-wallpaper-", delete=False) as destination:
                temporary_path = destination.name
                total = 0
                while True:
                    if time.monotonic() > deadline:
                        raise TimeoutError("wallpaper download timed out")
                    chunk = response.read(min(CHUNK_SIZE, MAX_WALLPAPER_BYTES - total + 1))
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_WALLPAPER_BYTES:
                        raise ValueError("wallpaper is too large")
                    destination.write(chunk)
        os.replace(temporary_path, output_path)
    except Exception:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
        raise


class WallpaperHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        expected_token = os.environ.get("BETTERLOCKSCREEN_API_TOKEN", "")
        supplied_token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        if not expected_token or not hmac.compare_digest(supplied_token, expected_token):
            self.send_error(401)
            return

        wallpaper_url = parse_qs(urlparse(self.path).query).get("url", [""])[0]
        output_path = os.path.expanduser("~/.cache/betterlockscreen/remote-wallpaper")
        try:
            download_wallpaper(wallpaper_url, output_path)
        except (HTTPError, URLError, TimeoutError, ValueError, OSError):
            self.send_error(400, "wallpaper download failed")
            return

        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8080), WallpaperHandler).serve_forever()
