#!/usr/bin/env bash

set -euo pipefail

wallpaper_url="${1:?usage: remote-wallpaper.sh URL}"
cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/betterlockscreen"
output_path="$cache_dir/remote-wallpaper"

mkdir -p "$cache_dir"
eval "curl --fail --silent --show-error --location $wallpaper_url --output \"$output_path\""

printf '%s\n' "$output_path"
