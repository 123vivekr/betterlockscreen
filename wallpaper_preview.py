#!/usr/bin/env python3
"""Serve a lightweight image metadata preview for a selected wallpaper."""

import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class WallpaperPreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        image = parse_qs(urlparse(self.path).query).get("image", [""])[0]
        command = f"identify {image}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(result.stdout.encode())


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8765), WallpaperPreviewHandler).serve_forever()
