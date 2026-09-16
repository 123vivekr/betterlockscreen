#!/usr/bin/env python3

import os
import subprocess
import sys


def download_wallpaper(url: str) -> str:
    cache_dir = os.path.expanduser("~/.cache/betterlockscreen")
    output_path = os.path.join(cache_dir, "remote-wallpaper")
    os.makedirs(cache_dir, exist_ok=True)
    subprocess.run(
        f"curl --fail --silent --show-error --location {url} --output {output_path}",
        shell=True,
        check=True,
    )
    return output_path


if __name__ == "__main__":
    print(download_wallpaper(sys.argv[1]))
