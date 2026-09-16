#!/usr/bin/env python3
"""Preview a local wallpaper without invoking a command shell."""

import argparse
import subprocess
from pathlib import Path


def apply_preview(wallpaper: str) -> None:
    wallpaper_path = Path(wallpaper).expanduser().resolve(strict=True)
    if not wallpaper_path.is_file():
        raise ValueError("wallpaper must be a regular file")
    subprocess.run(
        ["betterlockscreen", "-u", str(wallpaper_path)],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wallpaper")
    args = parser.parse_args()
    apply_preview(args.wallpaper)
