# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 12:35
# Software:  
# Description:   
# ----------------------------------------------
import os
import re
import sys
import time
import random
import socket
import sqlite3
from PyQt5.QtGui import QMouseEvent, QPainter
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTextBrowser, QLabel, QProgressBar, QStyleOptionProgressBar
from PIL import Image, ImageDraw, ImageFont, ImageFilter

rint = random.randint
host = socket.gethostname().lower()
desc = '''
            ================= <span style="color:green;">工具说明</span> =================
                    * 用户注册、登录、验证码
                    * 文件传输MD5校验
                    * 用户名、密码加密存储
                    * 收发线程分离，修复粘包问题
                    * 项目地址：<a href="https://github.com/warlock-lv"><span style="color:green;">https://github.com/warlock-lv</span></a>
            ========================================='''
try:
    path_base = sys._MEIPASS
except AttributeError:
    path_base = os.path.dirname(os.path.dirname(__file__))

path_res = os.path.join(path_base, 'res')
path_rdmc = os.path.join(path_res, 'code.png')
path_font = os.path.join(path_res, 'arial.ttf')

# 就不单独写配置文件了，因为客户端配置内容
conf = {'port': 9527, 'debug': host in ('warlock', 'kara', 'edith')}


def now_hms():
    return time.strftime('%H:%M:%S')


def get_desktop_path():
    return os.path.expanduser("~/Desktop")


def get_download_folder():
    if os.name == 'nt':  # for Windows
        CSIDL_PERSONAL = 5  # my Documents
        SHGFP_TYPE_CURRENT = 0  # get current, not default value
        import ctypes
        from ctypes import wintypes, windll
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        # append "downloads" to the my documents path
        return os.path.join(buf.value, 'Downloads')
    else:  # for mac and linux
        return os.path.expanduser('~/Downloads')


def replace_spaces(match):
    if '<' in match.group(0):
        return match.group(0)
    else:
        return match.group(0).replace(' ', '&nbsp;')


def text_replace_spaces(content):
    result, lines = [], content.split('\n')
    for line in lines:
        if re.search('<[^>]*>', line):
            result_line = re.sub(r'(<[^>]*>)|([^<>]*)', replace_spaces, line)
        else:
            result_line = line
        result.append(result_line)
    return '\n'.join(result)


class MyProgressBar(QProgressBar):
    position, side = 3, -1  # 值为3的话，百分比显示在进度的 1/3 位置, side大于0显示在偏右 1/3 处

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextVisible(False)  # 设置文本不可见

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        opt = QStyleOptionProgressBar()
        self.initStyleOption(opt)
        progress, total = opt.progress, opt.maximum
        if progress > 0:
            percentage = int((progress / total) * 100)
            text = f"{percentage}%"
            # text_width = painter.fontMetrics().width(text)
            # text_posix = int((progress / total) * (self.width() - text_width)) // self.position
            perc = progress / total
            if self.side > 0:
                posi = 1 - (1 / self.position)
            else:
                posi = 1 / self.position
            text_posix = int(posi * self.width() * perc)
            painter.drawText(text_posix, self.height() - 5, text)


class MyQTextBrowser(QTextBrowser):
    def __init__(self):
        super(MyQTextBrowser, self).__init__()
        self.setOpenLinks(True)
        self.setOpenExternalLinks(True)

    def html_append(self, text):
        # text = text_replace_spaces(text)
        # super().append(text)      一次性把字符串append进来 没效果
        result, lines = [], text.split('\n')
        for line in lines:
            if re.search('<[^>]*>', line):
                line = re.sub(r'(<[^>]*>)|([^<>]*)', replace_spaces, line)
            super().append(line)

    def append(self, text):
        self.html_append(text)


class PLable(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mouseReleaseEvent(self, QMouseEvent):
        self.clicked.emit()


class SQLite3Tool:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def __query(self, _query, _params=None):
        if _params:
            self.cursor.execute(_query, _params)
        else:
            self.cursor.execute(_query)

    def execute(self, query, params=None):
        self.__query(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        self.__query(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        self.__query(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()

    def __del__(self):
        self.conn.close()


class RdmCode:

    @property
    def rdm_char(self):
        return chr(rint(65, 90))

    @property
    def rdm_color1(self):
        return rint(64, 255), rint(64, 255), rint(64, 255)

    @property
    def rdm_color2(self):
        return rint(32, 127), rint(32, 127), rint(32, 127)

    def gen(self, w=120, h=60, path='code.png'):
        rnd = ''
        width, height = w, h
        image = Image.new('RGB', (width, height), (255, 255, 255))
        font_path = os.path.join(os.path.dirname(__file__), 'arial.ttf')
        font = ImageFont.truetype(font_path, 36)
        draw = ImageDraw.Draw(image)
        # 填充每个像素:
        for x in range(width):
            for y in range(height):
                draw.point((x, y), fill=self.rdm_color1)
        # 输出文字:
        for t in range(4):
            rc = self.rdm_char
            draw.text((30 * t + 10, 10), rc, font=font, fill=self.rdm_color2)
            rnd += rc
        # 模糊:
        image = image.filter(ImageFilter.BLUR)
        image.save(path)
        return rnd.lower()


if __name__ == '__main__':
    RdmCode().gen()
