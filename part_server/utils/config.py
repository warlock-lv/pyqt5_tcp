# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-25 10:29
# Software:  
# Description:   
# ----------------------------------------------
import os
import socket
from utils.util_server import Secrecy, get_desktop_path
from utils import path_db, path_base

skey = 9  # 用于Secrecy
port = 9527
max_link = 5
wk_folder = get_desktop_path()
host = socket.gethostname().lower()
desc = '''
            ================= <span style="color:green;">使用说明</span> ====================
                    * 运行服务端，如未找到db文件，则自动生成
                    * 初始化db数据，创建默认用户、密码为warlock
                    * 服务器点击左下角下拉框切换对不同用户的消息框
                    * 请勿在客户端关闭之前关闭服务器
                    * 如果客户端崩溃，请先重启服务器再尝试登录
                    * 项目地址：<a href="https://github.com/warlock-lv"><span style="color:green;">https://github.com/warlock-lv</span></a>
            ============================================'''

# todo, 写配置信息到数据库，下次启动时加载
conf = {'skey': skey, 'max_link': max_link, 'path_db': path_db, 'path_base': path_base,
        'wk_folder': wk_folder, 'desc': desc, 'port': port, 'debug': host in ('warlock', 'kara', 'edith')}


def db_init():
    from utils.util_server import SQLite3Tool
    db = SQLite3Tool(path_db)
    sql1 = '''
    CREATE TABLE IF NOT EXISTS usr (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ur TEXT NOT NULL UNIQUE,
        pw TEXT NOT NULL,
        ct timestamp not null default(datetime(CURRENT_TIMESTAMP,'localtime')),
        ut timestamp not null default(datetime(CURRENT_TIMESTAMP,'localtime'))
    );'''
    sql2 = '''
    CREATE TRIGGER ut
    AFTER UPDATE ON usr
    FOR EACH ROW
    BEGIN
        UPDATE usr SET ut = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;'''
    ur, pw = Secrecy.encrypt('warlock', skey), Secrecy.encrypt('warlock', skey)
    sql3 = f'insert into usr (ur, pw) values ("{ur}", "{pw}")'

    sql_list = [sql1, sql2, sql3]
    for i, sql in enumerate(sql_list, 1):
        db.execute(sql)
        print(f'done - {i}')
    print('done - db_init')


if not os.path.exists(path_db):
    db_init()

if __name__ == '__main__':
    pass
