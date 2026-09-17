#!/usr/bin/env python3
"""Serve a lightweight image metadata preview for a selected wallpaper."""

import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


WALLPAPER_DIRECTORY = Path("/usr/share/backgrounds").resolve()
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def resolve_wallpaper(value: str) -> Path | None:
    """Resolve a requested wallpaper only when it remains within the image root."""
    candidate = (WALLPAPER_DIRECTORY / value).resolve()
    if WALLPAPER_DIRECTORY not in candidate.parents:
        return None
    if candidate.suffix.lower() not in ALLOWED_EXTENSIONS or not candidate.is_file():
        return None
    return candidate


class WallpaperPreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        requested_image = parse_qs(urlparse(self.path).query).get("image", [""])[0]
        image = resolve_wallpaper(requested_image)
        if image is None:
            self.send_error(404, "Wallpaper not found")
            return
        result = subprocess.run(
            ["identify", str(image)],
            shell=False,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(result.stdout.encode())


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8765), WallpaperPreviewHandler).serve_forever()
