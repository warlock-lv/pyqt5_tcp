#!/bin/zsh
# ----------------------------------------------
# Author : warlock
# Email  : 457880341@qq.com
# Created: 2023-12-23 20:17
# Software:
# Descript:
# ----------------------------------------------

main_name='tcp_client'
path_script="$(cd "$(dirname "$0")" && pwd)"
path_spec="$path_script/$main_name.spec"
path_main="$path_script/$main_name.py"
path_icns="$path_script/res/icons/icon4.icns"

if [[ -f "$path_spec" ]]; then
    pyinstaller --clean --noconfirm "$path_spec"
    echo ' -- rebuild done'
else
    pyinstaller -w -F "$path_main" --clean -i "$path_icns" --noconfirm
    echo ' -- build done'
fi
