# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 15:18
# Software:  
# Description:   
# ----------------------------------------------
import sys
import qdarkstyle
from login import Login
from cform import CForm
from queue import Queue
from client import Client
from register import Regis
from form_info import AutoCloseWindow
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import pyqtSignal, QThread, QCoreApplication


class MForm(QMainWindow):
    signal_finish = pyqtSignal()  # 断开连接的信号

    def __init__(self):
        super().__init__()
        self.ur = ''
        self.stat = self.statusBar()  # 初始化状态栏
        self.q = Queue()  # 新建一个用于传输数据的队列
        self.cthread = QThread()  # 新建一个QThread实例

        self.client = Client(self.q)  # 新建一个继承QObject类的实例
        self.client.signal_state.connect(self.change_stat)
        self.client.moveToThread(self.cthread)  # 利用moveToThread方法把处理程序移动到Qthread上
        self.cthread.started.connect(self.client.run)  # 绑定两者
        self.client.signal_finish.connect(self.cthread.quit)  # 绑定信号
        self.cthread.finished.connect(self.close)
        self.cthread.start()  # 启动线程执行
        self.init_ui()

    # 初始化界面
    def init_ui(self):
        self.resize(400, 300)
        self.to_login()

    # 跳转至注册页面
    def to_rgs(self):
        rgs = Regis()  # 新建注册对象
        # 绑定信号与槽
        rgs.signal_state.connect(self.change_stat)
        rgs.signal_login.connect(self.to_login)
        rgs.signal_send.connect(self.send)

        self.client.signal_register.connect(rgs.result)
        self.setWindowTitle('注册')
        self.setCentralWidget(rgs)

    # 跳转至登录界面
    def to_login(self):
        login = Login()  # 新建登录对象
        # 绑定信号与槽
        login.signal_register.connect(self.to_rgs)
        login.signal_cf.connect(self.to_cf)
        login.signal_send.connect(self.send)
        login.signal_state.connect(self.change_stat)
        self.client.signal_login.connect(login.result)
        self.setWindowTitle('登录')
        self.setCentralWidget(login)

    # 跳转至主界面
    def to_cf(self, ur):
        # 传递参数实例化主界面
        self.ur = ur
        cf = CForm(ur)
        # 绑定信号与槽
        cf.signal_state.connect(self.change_stat)
        cf.signal_send.connect(self.send)

        self.client.signal_upl_s.connect(cf.upSList)
        self.client.signal_ufl_c.connect(cf.upCList)
        self.client.signal_ufl_c.emit(cf.fpath.text())
        self.client.signal_msg.connect(cf.show_msg)
        self.client.signal_upp.connect(cf.update_pro)
        self.client.signal_setmax.connect(cf.set_max_pro)

        self.resize(640, 640)
        self.setWindowTitle('客户端')
        self.setCentralWidget(cf)

    # 更新状态栏
    def change_stat(self, s):
        self.stat.showMessage(s)

    # 向处理程序发送数据
    def send(self, data):
        self.q.put(data)

    # 自定义关闭事件, 覆盖写父类方法
    def closeEvent(self, event):
        data = {'type': 'end'}
        if self.ur:
            data['ur'] = self.ur
        self.send(data)  # 向客户端以及服务器发送关闭命令


# 启动程序
if __name__ == '__main__':
    QCoreApplication.addLibraryPath('.')
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    try:
        mf = MForm()
    except ConnectionRefusedError:
        mf = AutoCloseWindow()
    mf.show()
    sys.exit(app.exec_())
