# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 15:17
# Software:  
# Description:   
# ----------------------------------------------
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QPushButton
from res.util_client import RdmCode, PLable, conf, path_rdmc


class Login(QWidget):
    signal_register = pyqtSignal()  # 跳转至注册界面的信号
    signal_state = pyqtSignal(str)  # 更新面板状态栏的信号
    signal_send = pyqtSignal(dict)  # 向服务器发送数据的信号
    signal_cf = pyqtSignal(str)  # 跳转至主界面的信号

    def __init__(self):
        super().__init__()
        self.ur, self.pw, self.rdmc = None, None, None
        self.init_ui()
        # t2 = Thread(target=self.startservice, args=(q, ))
        # t2.start()

    # 绘制图形界面
    def init_ui(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        # 用户名输入
        lbu = QLabel('用户：', self)
        self.ur = QLineEdit(self)
        grid.addWidget(lbu, 1, 0, 1, 2)
        grid.addWidget(self.ur, 1, 1, 1, 2)
        # 密码输入
        lbp = QLabel('密码：', self)
        self.pw = QLineEdit(self)
        self.pw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbp, 2, 0, 1, 1)
        grid.addWidget(self.pw, 2, 1, 1, 2)

        # 验证码输入
        lbrn = QLabel('验证：', self)
        self.input_rdmc = QLineEdit(self)
        self.label_rdmp = PLable()
        self.rdmc = RdmCode().gen(120, 60, path=path_rdmc)
        pict = QPixmap(path_rdmc)
        self.label_rdmp.setPixmap(pict)
        grid.addWidget(lbrn, 3, 0, 1, 1)
        grid.addWidget(self.input_rdmc, 3, 1, 1, 1)
        grid.addWidget(self.label_rdmp, 3, 2, 1, 1)
        self.label_rdmp.clicked.connect(self.change_rdmc)

        # 登录按钮
        bt1 = QPushButton('登录')
        grid.addWidget(bt1, 4, 2)
        bt1.clicked.connect(self.send)
        # 注册按钮
        bt2 = QPushButton('注册账号')
        grid.addWidget(bt2, 4, 1)
        bt2.clicked.connect(self.go_rgs)
        # 设置布局
        self.setLayout(grid)
        # self.resize(400, 300)
        # self.setWindowTitle('登录')
        # self.show()

    # 当用户点击或登录报错时更换验证码
    def change_rdmc(self):
        self.input_rdmc.clear()
        self.rdmc = RdmCode().gen(120, 60, path=path_rdmc)
        pict = QPixmap(path_rdmc)
        self.label_rdmp.setPixmap(pict)

    # 将用户名与密码发送至服务器端
    def send(self):
        # 将用户输入的验证码转为小写
        urn = self.input_rdmc.text().lower()
        ur, pw = self.ur.text(), self.pw.text()
        if conf.get('debug'):
            urn = self.rdmc
            ur = ur if ur else 'warlock'
            pw = pw if pw else 'warlock'
            self.ur.setText(ur)
        if self.rdmc == urn:
            data = {'type': 'lg', 'cnt': {'ur': ur, 'pw': pw}}  # 定义传输数据结构
            self.signal_send.emit(data)
        else:
            self.signal_state.emit('验证码错误！')
            self.input_rdmc.clear()

    # 跳转至注册页面
    def go_rgs(self):
        self.close()
        self.signal_register.emit()

    # 根据从服务器返回的结果执行相应操作
    def result(self, rs):
        if rs:  # 如果登录成功
            ur = self.ur.text()
            self.signal_cf.emit(ur)  # 发送跳转至主界面的信号
        else:
            self.ur.clear()
            self.pw.clear()
            self.change_rdmc()


if __name__ == '__main__':
    pass
