# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 11:58
# Software:  
# Description:   
# ----------------------------------------------
import sys
import traceback
import qdarkstyle
from server import Server
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QApplication, QGroupBox, QPushButton, QLabel, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QFormLayout, QLineEdit, QFileDialog, QComboBox,
                             QMessageBox, QStackedWidget, QSizePolicy)
from utils.util_server import now_hms, MyQTextBrowser
from utils.config import conf


class SForm(QWidget):
    signal_finish = pyqtSignal()  # 结束线程的信号
    numc = 0  # 已连接客户端数量

    def __init__(self):
        super().__init__()
        self.label_numc = None
        self.btn_run, self.btn_send, self.sel_user, self.box_umsg = None, None, None, None
        self.sthread, self.max_link, self.wk_folder, self.btn_sel_path = None, None, None, None
        self.group_box_conf, self.group_box_log, self.group_box_msg = None, None, None
        self.ip, self.log, self.port, self.stack, self.server = None, None, None, None, None
        self.user_box = {}  # 每个用户对话框的字典
        self.init_ui()

    # 绘制界面
    def init_ui(self):
        self.create_group_box_conf()
        self.create_group_box_log()
        self.create_group_box_msg()
        layout_main = QVBoxLayout()
        layout_hbox = QHBoxLayout()
        layout_hbox.addStretch()
        # 调用方法绘制界面
        self.setWindowTitle('服务器软件')
        layout_hbox.addWidget(self.group_box_conf)
        layout_hbox.addWidget(self.group_box_log)
        layout_main.addLayout(layout_hbox)
        layout_main.addWidget(self.group_box_msg)
        self.setLayout(layout_main)

    # 绘制服务器配置部分
    def create_group_box_conf(self):
        self.group_box_conf = QGroupBox('服务器配置')
        layout = QGridLayout()

        # 设置标签、输入框
        label_ip, self.ip = QLabel('服务地址'), QLineEdit('localhost')
        label_port, self.port = QLabel('服务端口'), QLineEdit(str(conf.get('port')))
        self.ip.setEnabled(False), self.port.setEnabled(False)

        label_max_link, self.max_link = QLabel('最大连接'), QLineEdit(str(conf.get('max_link')))
        label_wk_folder, self.wk_folder = QLabel('文件路径'), QLineEdit(conf.get('wk_folder'))

        self.btn_sel_path = QPushButton('选择')
        self.btn_sel_path.clicked.connect(self.show_dialog)  # 为按钮绑定点击事件

        self.btn_run = QPushButton('启动服务')
        self.btn_run.setStyleSheet('QPushButton {background-color: green;}')
        self.btn_run.clicked.connect(self.start_server)  # 为启动按钮绑定服务器启动方法

        layout.setSpacing(10)
        layout.addWidget(label_ip, 1, 0)
        layout.addWidget(self.ip, 1, 1)
        layout.addWidget(label_port, 2, 0)
        layout.addWidget(self.port, 2, 1)
        layout.addWidget(label_max_link, 3, 0)
        layout.addWidget(self.max_link, 3, 1)
        layout.addWidget(label_wk_folder, 4, 0)
        layout.addWidget(self.wk_folder, 4, 1)
        layout.addWidget(self.btn_sel_path, 5, 0)
        layout.addWidget(self.btn_run, 5, 1)

        layout.setColumnStretch(1, 10)
        self.group_box_conf.setLayout(layout)

    # 绘制服务日志部分
    def create_group_box_log(self):
        self.group_box_log = QGroupBox('服务日志')
        layout = QVBoxLayout()
        self.log = MyQTextBrowser()
        layout.addWidget(self.log)
        self.group_box_log.setLayout(layout)

    # 绘制消息对话框
    def create_group_box_msg(self):
        self.group_box_msg = QGroupBox('消息发送')
        layout = QFormLayout()
        msgbox = MyQTextBrowser()

        self.stack = QStackedWidget(self)  # 设置一个堆栈以切换不同用户的对话界面
        self.stack.addWidget(msgbox)  # 每个用户有一个文本框展示信息

        self.user_box['无'] = msgbox
        self.msg_show('无', conf.get('desc'))

        self.sel_user = QComboBox()  # 使用下拉列表选择用户对话框
        self.sel_user.setStyleSheet("""
            QComboBox { width: 100px; height: 5px;
                /* background-color: #FF0000;   设置背景颜色 */
            }""")
        self.sel_user.addItem('---')
        self.sel_user.currentTextChanged.connect(self.change_box)  # 绑定处理方法
        self.sel_user.setDisabled(True)

        # 绘制输入框和发送按钮
        childgrid = QGridLayout()
        self.box_umsg = QLineEdit()
        self.btn_send = QPushButton('发送消息')
        self.btn_send.setStyleSheet('QPushButton {background-color: green;}')
        self.label_numc = QLabel('已连接 - 0')
        self.label_numc.setStyleSheet("""QLabel {color: #FFFF00;}""")
        # childgrid.addWidget(self.box_umsg, 0, 0)
        # childgrid.addWidget(self.btn_send, 0, 1)
        childgrid.addWidget(self.box_umsg, 0, 0, 2, 1)
        childgrid.addWidget(self.btn_send, 0, 1, 2, 1)
        childgrid.addWidget(self.label_numc, 0, 2, 2, 1)
        # 修改 create_group_box_msg 方法中的布局代码，使得 self.box_umsg 和 self.btn_send 的宽度比例为 3:1
        childgrid.setColumnStretch(0, 4)  # todo, 不生效 不清楚原因
        childgrid.setColumnStretch(1, 1)
        layout.addRow(self.stack)
        layout.addRow(self.sel_user, childgrid)
        self.btn_send.clicked.connect(self.msg_send)

        # 一开始禁用输入框和发送按钮
        self.box_umsg.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.group_box_msg.setLayout(layout)

    # 展示选择文件夹对话框
    def show_dialog(self):
        path_curr = self.wk_folder.text()
        upath = QFileDialog.getExistingDirectory(self, '选择文件夹', '.')
        if not upath:
            upath = path_curr
        self.wk_folder.setText(upath)

    # 开始服务器线程
    def start_server(self):
        host = self.ip.text()
        path = self.wk_folder.text()
        port = int(self.port.text())
        link = int(self.max_link.text())

        if not all([host, port, path, link]):
            QMessageBox.information(self, '警告', '配置项不能为空!')  # 发出警告
            return

        # 检测要求输入的字段是否为空
        if host and port and link and path:
            self.sel_user.setEnabled(True)
            self.btn_run.setEnabled(False)
            self.btn_sel_path.setEnabled(False)
            self.max_link.setEnabled(False)
            self.wk_folder.setEnabled(False)

            # 实例化服务器线程
            self.sthread = QThread()
            self.server = Server(host, port, link, path)
            # 绑定信号与槽
            self.server.signal_state.connect(self.add_log)
            self.server.signal_login.connect(self.user_add)
            self.server.signal_msg.connect(self.msg_show)
            self.server.signal_quit.connect(self.user_remove)
            # 启动线程运行
            self.server.moveToThread(self.sthread)
            self.sthread.started.connect(self.server.run)
            self.sthread.start()
        return

    # 更新服务器日志
    def add_log(self, log):
        self.log.append(log)

    # 为选择用户下拉列表中添加用户
    def user_add(self, ur):
        self.sel_user.addItem(ur)
        umsgBox = MyQTextBrowser()
        self.user_box[ur] = umsgBox
        self.stack.addWidget(umsgBox)
        self.numc += 1
        self.label_numc.setText(f'已连接 - {self.numc}')

    # 移除用户
    def user_remove(self, ur):
        user = self.sel_user.findText(ur)
        self.sel_user.removeItem(user)
        self.stack.removeWidget(self.user_box[ur])
        self.numc -= 1
        self.label_numc.setText(f'已连接 - {self.numc}')

    # 显示信息
    def msg_show(self, ur, msg):
        self.user_box[ur].append(msg)

    # 根据选择的用户改变当前对话框
    def change_box(self, ur):
        if ur != '无':
            self.box_umsg.setEnabled(True)
            self.btn_send.setEnabled(True)
        if ur not in self.user_box:
            ur = '无'
        self.stack.setCurrentWidget(self.user_box[ur])

    # 发送消息
    def msg_send(self):
        msg = self.box_umsg.text()
        now = now_hms()
        umsg = f'本机 - {now}：{msg}'
        self.stack.currentWidget().append(umsg)  # 在对话框中展示消息
        self.box_umsg.clear()  # 清空输入框
        ur = self.sel_user.currentText()
        data = {'type': 'msg', 'cnt': {'msg': msg}}  # 构造命令
        self.server.users[ur].put(data)  # 发送数据

    # 自定义关闭事件，覆盖父类方法
    def closeEvent(self, event):
        if self.server:
            users = self.server.users
            for ur in users:
                data = {'type': 'end', 'ur': ur}
                users[ur].put(data)
        self.close()


# 服务器程序启动
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 美化界面
        sf = SForm()
        sf.show()
        sys.exit(app.exec_())
    except Exception:
        err = traceback.format_exc()
        print(err)
