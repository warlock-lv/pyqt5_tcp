# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-24 22:32
# Software:  
# Description:   
# ----------------------------------------------
from utils.config import path_db
from utils.util_server import SQLite3Tool


def run():
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

    sql_list = [sql1, sql2]
    for i, sql in enumerate(sql_list, 1):
        db.execute(sql)
        print(i)

    print()
    res = db.fetch_all('select * from usr')
    [print(it) for it in res]


if __name__ == '__main__':
    run()
