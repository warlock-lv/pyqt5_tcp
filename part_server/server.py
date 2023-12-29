# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 11:50
# Software:  
# Description:   
# ----------------------------------------------
import json
import socket
import struct
import hashlib
from queue import Queue
from threading import Thread
from os import listdir, remove
from os.path import getsize, isfile, join
from PyQt5.QtCore import QObject, pyqtSignal
from utils.util_server import now_hms, Secrecy, SQLite3Tool
from utils.config import path_db, skey


class Server(QObject):
    signal_msg = pyqtSignal(str, str)  # 更新消息栏的信号
    signal_login = pyqtSignal(str)  # 登录的信号
    signal_state = pyqtSignal(str)  # 更新日志的信号
    signal_quit = pyqtSignal(str)  # 退出的信号

    def __init__(self, host, port, num, path):
        super().__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.path = path  # 工作文件夹路径
        self.cnum = 0  # 已连接用户数
        self.num = num  # 最大连接数
        if host == 'localhost':
            host = socket.gethostname()
            host = '127.0.0.1' if host == 'edith' else host
        self.s.bind((host, port))  # 绑定端口
        self.s.listen(num + 1)
        self.users = {}  # 已连接用户字典

    # 主线程
    def run(self):
        now = now_hms()
        self.signal_state.emit(f'[{now}]：服务器已启动！')  # 打印启动信息

        while True:
            c, addr = self.s.accept()  # 每接收到一个连接请求
            self.cnum += 1  # 连接数加1
            cq = Queue()  # 实例化一个队列作为发送线程与接收线程间传递数据的通道

            # 开启接收线程
            crthread = Thread(target=self.crec, args=(c, addr, cq))
            crthread.daemon = True  # 设置随主线程退出
            crthread.start()  # 开始运行
            # 开启发送线程
            csthread = Thread(target=self.csend, args=(c, addr, cq))
            csthread.daemon = True  # 设置随主线程退出
            csthread.start()  # 开始运行

    # 接收线程
    def crec(self, c, addr, q):
        while True:
            head_dic = self.decode_read(c)  # 接收报头
            tp = head_dic['type']  # 提起报头的命令

            if tp == 'end':  # 如果要求结束
                q.put(head_dic)  # 将其传递给发送线程并跳出
                break
            else:
                cnt = head_dic['cnt']  # 提取命令内容

            if tp == 'lg':  # 要求登录则调用登录处理方法
                self.login(cnt, q)
            elif tp == 'rgs':
                self.rgs(cnt, q)  # 要求注册则调用注册处理方法
            elif tp == 'msg':
                # 对消息的处理
                now = now_hms()
                ur, msg = cnt['ur'], cnt['msg']
                self.signal_msg.emit(ur, f'{ur} - {now}：{msg}')  # 更新消息栏
            elif tp == 'dwnf':
                q.put(head_dic)  # 要求下载文件将命令传递给发送线程
            elif tp == 'sendf':
                self.recf(c, cnt, q)  # 要求发送文件则调用接收文件处理方法

    # 发送线程
    def csend(self, c, addr, q):
        while True:
            data = q.get()  # 获取接收线程的信息
            if data['type'] == 'dwnf':  # 用户请求下载文件
                self.sendf(c, data)  # 调用发送文件的处理方法
            elif data['type'] == 'end':  # 要求退出
                # 打印退出日志信息并跳出循环
                if 'ur' in data:
                    ur = data['ur']
                    self.signal_quit.emit(ur)
                    self.users.pop(ur)
                else:
                    ur = str(addr)
                now = now_hms()
                self.signal_state.emit(f'[{now}]【{ur}】：退出')
                self.cnum -= 1
                self.encode_send(c, data)
                break
            else:
                self.encode_send(c, data)  # 否则，就将接收的命令发送给客户端

    # 接收用户上传的文件
    def recf(self, c, cnt, q):
        ur, fmd5, fname, fsize = cnt['ur'], cnt['fmd5'], cnt['fname'], cnt['fsize']
        data = {'type': 'sendf', 'cnt': {}}  # 构建命令

        dsize = 0  # 已接收文件大小
        dmd5 = hashlib.md5()
        with open(self.path + '/' + fname, 'wb') as f:
            # 打开文件持续接收
            while dsize < fsize:
                block = c.recv(1024)
                f.write(block)
                dmd5.update(block)
                dsize += len(block)  # 更新已接收文件大小

        # 校验文件
        if fmd5 == dmd5.hexdigest():
            # 发送成功接收信息
            data['cnt']['result'] = True
            data['cnt']['flist'] = [f for f in listdir(self.path) if isfile(join(self.path, f))]
            msg = f'发送成功!{fname}'
        else:
            remove(fname)  # 删除文件
            data['cnt']['result'] = False
            msg = f'发送失败!{fname}'

        data['cnt']['msg'] = msg  # 发送失败信息
        now = now_hms()
        self.signal_state.emit(f'[{now}]【{ur}】：{msg}')  # 更新服务器日志
        q.put(data)  # 将命令送给发送线程

    # 发送用户下载的文件
    def sendf(self, c, data):
        ur = data['cnt']['ur']  # 获取用户名
        fname = data['cnt']['fname']  # 获取文件名
        fsize = getsize(self.path + '/' + fname)  # 文件大小
        data['cnt']['fsize'] = fsize  # 设置命令中的文件大小字段
        data['cnt']['fmd5'] = self.get_md5(data['cnt'])  # 设置命令中的MD5字段
        self.encode_send(c, data)  # 向客户端发送控制命令

        dsize = 0
        # 打开文件进行发送
        with open(self.path + '/' + fname, 'rb') as f:
            while dsize < fsize:
                block = f.read(1024)
                c.send(block)
                dsize += len(block)  # 更新发送文件大小

        now, msg = now_hms(), f'发送完毕！{fname}'
        self.signal_state.emit(f'[{now}]【{ur}】：{msg}')  # 更新日志信息

    # 用户验证
    def login(self, cnt, q):
        db = SQLite3Tool(path_db)
        data = {'type': 'lg', 'cnt': {}}  # 构造命令
        ur, pw = cnt['ur'], cnt['pw']
        # 如果已达最大连接数量
        if self.cnum > self.num:
            msg = '连接已达最大数！'
            data['cnt']['result'] = False  # 返回失败信息
        else:
            dur, dpw = Secrecy.encrypt(ur, skey), Secrecy.encrypt(pw, skey)
            # SQL查询该用户的密码
            sql = f"SELECT pw FROM usr WHERE ur='{dur}'"
            rpw = db.fetch_one(sql)[0]
            # 只有密码正确且该用户没有登录时
            if dpw == rpw and ur not in self.users:
                msg = '登录成功！'
                data['cnt']['result'] = True  # 返回正确信息
                data['cnt']['flist'] = [f for f in listdir(self.path) if isfile(join(self.path, f))]  # 发送服务器文件列表
                self.users[ur] = q  # 为该用户建立消息传输队列
                self.signal_login.emit(ur)  # 更新日志已消息框可选用户列表
            # 若用户已登录
            elif ur in self.users:
                msg = '此用户已登录！'
                data['cnt']['result'] = False  # 返回失败信息
            # 若查询结果为空或密码错误
            else:
                msg = '用户名或密码错误！'
                data['cnt']['result'] = False  # 返回错误信息

        data['cnt']['msg'] = msg  # 设置返回信息
        now = now_hms()
        self.signal_state.emit(f'[{now}]【{ur}】：{msg}')  # 更新日志
        db.close()  # 关闭数据库
        q.put(data)  # 发送登录结果

    # 用户注册
    def rgs(self, cnt, q):
        db = SQLite3Tool(path_db)
        ur, pw = cnt['ur'], cnt['pw']
        data = {'type': 'rgs', 'cnt': {}}  # 构造命令
        dur, dpw = Secrecy.encrypt(ur, skey), Secrecy.encrypt(pw, skey)
        # 使用SQL语句来查询该用户
        result = db.fetch_one(f"SELECT * FROM usr WHERE ur='{dur}'")

        if result:
            msg = '用户已存在！'
            data['cnt']['result'] = False  # 返回错误信息
        else:
            msg = '注册成功！'
            csql = f"INSERT INTO usr (ur, pw) VALUES ('{dur}', '{dpw}')"  # 加入该用户
            db.execute(csql)
            data['cnt']['result'] = True  # 返回成功信息

        data['cnt']['msg'] = msg  # 设置命令中的返回信息
        now = now_hms()
        self.signal_state.emit(f'[{now}][{ur}]：{msg}')  # 更新日志

        db.close()  # 关闭数据库
        q.put(data)  # 返回消息

    # 将收到的信息转化为报头
    def decode_read(self, c):
        # 接收报头长度
        head_struct = c.recv(4)
        head_len = struct.unpack('i', head_struct)[0]
        # 接收报头
        head_bytes = c.recv(head_len)
        head_json = head_bytes.decode('utf-8')
        head_dic = json.loads(head_json)
        return head_dic

    # 将要发送的信息转化为报头发送
    def encode_send(self, c, data):
        # 制作报头
        head_json = json.dumps(data)
        head_bytes = head_json.encode('utf-8')  # 要发送需要转换成字节数据
        # 发送报头的长度
        head_len = len(head_bytes)
        c.send(struct.pack('i', head_len))
        # 发送报头
        c.send(head_bytes)

    # 获取文件MD5值
    def get_md5(self, cnt):
        fmd5 = hashlib.md5()
        fname, fsize = cnt['fname'], cnt['fsize']  # 发送 文件名, 文件大小
        # 逐块计算文件的MD5值
        with open(self.path + '/' + fname, 'rb') as f:
            dsize = 0
            while dsize < fsize:
                block = f.read(1024)
                fmd5.update(block)
                dsize += len(block)
        return fmd5.hexdigest()


if __name__ == '__main__':
    pass
