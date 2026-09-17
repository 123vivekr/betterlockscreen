#!/usr/bin/env python3
"""TEST ONLY: intentionally unsafe wallpaper preview helper.

This file exists solely to exercise Winfunc's PR security review. Do not merge
or deploy it.
"""

import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class PreviewHandler(BaseHTTPRequestHandler):
    """Render a requested wallpaper path for a local preview response."""

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
        body = result.stdout.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8765), PreviewHandler).serve_forever()
