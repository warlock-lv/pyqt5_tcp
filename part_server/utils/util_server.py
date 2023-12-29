# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 12:35
# Software:  
# Description:   
# ----------------------------------------------
import os
import re
import time
import random
import sqlite3
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTextBrowser, QLabel

rint = random.randint


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


class Secrecy:

    # 自定义加密算法
    @classmethod
    def encrypt(cls, s, key=7):
        b = bytearray(str(s).encode('utf-8'))
        n = len(b)  # 求出 b 的字节数
        c = bytearray(n * 2)
        j = 0
        for i in range(0, n):
            b1 = b[i]
            b2 = b1 ^ key  # b1 = b2^ key
            c1 = b2 % 16
            c2 = b2 // 16  # b2 = c2*16 + c1
            c1 = c1 + 65
            c2 = c2 + 65  # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码
            c[j] = c1
            c[j + 1] = c2
            j = j + 2
        return c.decode('utf-8')

    # 自定义解密算法
    @classmethod
    def decrypt(cls, s, key=7):
        c = bytearray(str(s).encode('utf-8'))
        n = len(c)  # 计算 b 的字节数
        if n % 2 != 0:
            return ""
        n = n // 2
        b = bytearray(n)
        j = 0
        for i in range(0, n):
            c1 = c[j]
            c2 = c[j + 1]
            j = j + 2
            c1 = c1 - 65
            c2 = c2 - 65
            b2 = c2 * 16 + c1
            b1 = b2 ^ key
            b[i] = b1
        return b.decode('utf-8')


if __name__ == '__main__':
    akey, text = 9, 'Hello, World!'
    aa = Secrecy.encrypt(text, akey)
    print(text)
    print(aa)
    bb = Secrecy.decrypt(aa, akey)
    print(bb)
    cc = get_desktop_path()
    print(cc)
