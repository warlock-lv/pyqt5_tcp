# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-27 09:37
# Software:  
# Description:   
# ----------------------------------------------
import os
import sys
import shutil

dbfn = 'pyqt5_tcp.db'

try:
    path_base = sys._MEIPASS
    path_db_original = os.path.join(path_base, 'res', dbfn)
    path_home = os.path.expanduser('~')
    path_db = os.path.join(path_home, dbfn)
    # 如果数据库文件不存在，则复制它
    if not os.path.exists(path_db):
        shutil.copy2(path_db_original, path_db)
except AttributeError:
    path_base = os.path.dirname(os.path.dirname(__file__))
    path_res = os.path.join(path_base, 'res')
    path_db = os.path.join(path_res, dbfn)


def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和使用PyInstaller打包的环境 """
    try:
        # PyInstaller创建一个临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 如果错误，则我们在当前路径下。
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    pass
