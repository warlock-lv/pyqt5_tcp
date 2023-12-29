#!/bin/zsh
# ----------------------------------------------
# Author : warlock
# Email  : 457880341@qq.com
# Created: 2023-12-26 12:25
# Software:
# Descript:
# ----------------------------------------------

# 定义颜色常量
typeset -A colors
colors=(
    red "%F{red}"
    green "%F{green}"
    yellow "%F{yellow}"
    blue "%F{blue}"
    magenta "%F{magenta}"
    cyan "%F{cyan}"
    white "%F{white}"
)

# cprint函数用于打印带有指定颜色的字符串
cprint() {
    # 检查参数数量
    if [ "$#" -eq 1 ]; then
        echo "$1"
    elif [ "$#" -eq 2 ]; then
        local color="$1"
        local text="$2"

        # 检查颜色是否在定义的颜色常量中
        if [[ -n "${colors[$color]}" ]]; then
            print -P "${colors[$color]}$text%f" # 使用颜色
        else
            echo "$2"
        fi
    else
        echo "Error: cprint 参数数量不正确"
    fi
}

usage_print() {
    cprint red "使用方法:"
    cprint cyan "   1. 转换目录下所有图片  ./png2icns.sh -a"
    cprint cyan "   2. 转换目录下指定图片  ./png2icns.sh image_path "
    cprint cyan "   3. 转换指定图片并命名  ./png2icns.sh image_path name"
}

# 获取脚本所在目录
#script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
script_dir="$(cd "$(dirname "$0")" && pwd)"

# 定义转换方法
pic2icns() {
    local image_path="$1"
    local base_name="${2:-$(basename -s .png $image_path)}"

    # 创建临时文件夹
    local temp_folder="$script_dir/tmp_pic2icns_$base_name.iconset"
    mkdir -p "$temp_folder"

    # 将图片转换为各种尺寸的png文件
    sips -z 16 16 "$image_path" --out "$temp_folder/icon_16x16.png"
    sips -z 32 32 "$image_path" --out "$temp_folder/icon_16x16@2x.png"
    sips -z 32 32 "$image_path" --out "$temp_folder/icon_32x32.png"
    sips -z 64 64 "$image_path" --out "$temp_folder/icon_32x32@2x.png"
    sips -z 128 128 "$image_path" --out "$temp_folder/icon_128x128.png"
    sips -z 256 256 "$image_path" --out "$temp_folder/icon_128x128@2x.png"
    sips -z 256 256 "$image_path" --out "$temp_folder/icon_256x256.png"
    sips -z 512 512 "$image_path" --out "$temp_folder/icon_256x256@2x.png"

    # 使用iconutil创建icns文件
    iconutil -c icns -o "$script_dir/${base_name}.icns" "$temp_folder"

    # 清理临时文件夹
    rm -r "$temp_folder"

    echo "已生成 ${base_name}.icns 文件"
}

# 主程序
if [ "$#" -eq 0 ]; then
    usage_print
    exit 0
elif [ "$#" -eq 1 ]; then
    if [ "$1" = "-a" ]; then # 处理同层目录中的所有png图片
        for png_file in "$script_dir"/*.png; do
            pic2icns "$png_file"
        done
    else
        pic2icns "$script_dir/$1" # 处理单个图片文件
    fi
elif [ "$#" -eq 2 ]; then
    # 处理单个图片文件，指定生成的icns文件名
    pic2icns "$script_dir/$1" "$2"
else
    usage_print
fi

