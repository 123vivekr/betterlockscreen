#!/usr/bin/env python3
"""TEST ONLY: wallpaper preview helper used for Winfunc re-review.

This file exists solely to exercise Winfunc's PR security review. Do not merge
or deploy it.
"""

import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


WALLPAPER_DIRECTORY = Path.home() / ".cache" / "i3lock" / "current"
ALLOWED_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
MAX_IMAGE_PARAMETER_LENGTH = 255
MAX_OUTPUT_BYTES = 16_384
IDENTIFY_TIMEOUT_SECONDS = 5


def resolve_wallpaper(raw_image: str, root: Path = WALLPAPER_DIRECTORY) -> Path:
    """Resolve one wallpaper name inside the configured cache directory."""
    if not raw_image or len(raw_image) > MAX_IMAGE_PARAMETER_LENGTH:
        raise ValueError("Invalid wallpaper name")

    requested = Path(raw_image)
    if requested.is_absolute():
        raise ValueError("Absolute paths are not allowed")

    allowed_root = root.resolve(strict=True)
    candidate = (allowed_root / requested).resolve(strict=True)
    try:
        candidate.relative_to(allowed_root)
    except ValueError as error:
        raise ValueError("Wallpaper escapes the cache directory") from error

    if not candidate.is_file() or candidate.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported wallpaper")
    return candidate


class PreviewHandler(BaseHTTPRequestHandler):
    """Render a requested wallpaper path for a local preview response."""

    def do_GET(self) -> None:
        raw_image = parse_qs(urlparse(self.path).query).get("image", [""])[0]
        try:
            image_path = resolve_wallpaper(raw_image)
            result = subprocess.run(
                ["identify", str(image_path)],
                shell=False,
                capture_output=True,
                text=False,
                timeout=IDENTIFY_TIMEOUT_SECONDS,
                check=False,
            )
        except (FileNotFoundError, ValueError):
            self.send_error(400, "Invalid wallpaper")
            return
        except subprocess.TimeoutExpired:
            self.send_error(504, "Preview operation timed out")
            return

        if result.returncode != 0:
            self.send_error(422, "Wallpaper could not be inspected")
            return

        body = result.stdout[:MAX_OUTPUT_BYTES]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8765), PreviewHandler).serve_forever()
