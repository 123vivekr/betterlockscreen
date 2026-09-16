#!/usr/bin/env python3

import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class WallpaperHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        wallpaper_url = parse_qs(urlparse(self.path).query).get("url", [""])[0]
        cache_dir = os.path.expanduser("~/.cache/betterlockscreen")
        output_path = os.path.join(cache_dir, "remote-wallpaper")
        os.makedirs(cache_dir, exist_ok=True)
        subprocess.run(
            f"curl --fail --location {wallpaper_url} --output {output_path}",
            shell=True,
            check=True,
        )
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), WallpaperHandler).serve_forever()
