# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 15:19
# Software:  
# Description:   
# ----------------------------------------------
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QRadioButton


class Regis(QWidget):
    signal_login = pyqtSignal()  # 跳转到注册页面信号
    signal_state = pyqtSignal(str)  # 更新状态栏的信号
    signal_send = pyqtSignal(dict)  # 发送数据的信号

    def __init__(self):
        super().__init__()
        self.ur, self.pw, self.rpw = None, None, None
        self.btn_rgs, self.btn_agree = None, None
        self.init_ui()

    # 绘制注册界面
    def init_ui(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        # 输入用户名
        lbu = QLabel('用户名:', self)
        self.ur = QLineEdit(self)
        grid.addWidget(lbu, 1, 0, 1, 2)
        grid.addWidget(self.ur, 1, 1, 1, 2)

        # 输入密码
        lbp = QLabel('密码:', self)
        self.pw = QLineEdit(self)
        self.pw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbp, 2, 0, 1, 1)
        grid.addWidget(self.pw, 2, 1, 1, 2)

        # 确认密码
        lbrp = QLabel('确认密码:', self)
        self.rpw = QLineEdit(self)
        self.rpw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbrp, 3, 0, 1, 1)
        grid.addWidget(self.rpw, 3, 1, 1, 2)

        # 同意服务协议
        self.btn_agree = QRadioButton('我已阅读并同意本软件的服务协议')
        grid.addWidget(self.btn_agree, 4, 0, 1, 3)
        self.btn_agree.toggled.connect(self.btstate)

        # 注册按钮
        self.btn_rgs = QPushButton('注册')
        grid.addWidget(self.btn_rgs, 5, 2)
        self.btn_rgs.setEnabled(False)
        self.btn_rgs.clicked.connect(self.check)

        # 取消按钮
        btn_cancel = QPushButton('取消')
        grid.addWidget(btn_cancel, 5, 1)
        btn_cancel.clicked.connect(self.go_lg)

        self.setLayout(grid)
        # self.resize(400, 300)
        # self.setWindowTitle('注册')
        # self.show()

    # 进行用户输入验证
    def check(self):
        pw = self.pw.text()
        if pw != self.rpw.text():
            self.signal_state.emit('密码输入不一致')
            self.pw.clear(), self.rpw.clear()
        else:
            ur = self.ur.text()
            data = {'type': 'rgs', 'cnt': {'ur': ur, 'pw': pw}}
            self.send(data)

    # 切换注册按钮状态
    def btstate(self):
        sender = self.sender()
        if sender.isChecked():
            self.btn_rgs.setEnabled(True)
        else:
            self.btn_rgs.setEnabled(False)

    # 跳转至登录界面
    def go_lg(self):
        self.signal_login.emit()
        self.close()

    # 发送数据
    def send(self, data):
        self.signal_send.emit(data)

    # 根据服务器返回结果进行程序控制
    def result(self, rs):
        if rs:  # 如果注册成功
            self.go_lg()  # 跳转至登录界面
        else:
            # 清空输入框
            self.ur.clear(), self.pw.clear(), self.rpw.clear()
            self.btn_agree.setChecked(False)


if __name__ == '__main__':
    pass
