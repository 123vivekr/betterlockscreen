#!/usr/bin/env python3
"""Small HTTP helper for previewing a wallpaper before applying it."""

import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class WallpaperPreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        wallpaper = parse_qs(urlparse(self.path).query).get("path", [""])[0]
        subprocess.run(
            f"betterlockscreen -u {wallpaper}",
            shell=True,
            check=True,
        )
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8765), WallpaperPreviewHandler).serve_forever()
