# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 15:22
# Software:  
# Description:   
# ----------------------------------------------
from os import listdir
from os.path import getsize, isfile, join
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QListView,
                             QToolButton, QProgressBar, QFileDialog, QVBoxLayout, QGroupBox)
from res.util_client import now_hms, get_download_folder, desc, MyQTextBrowser, MyProgressBar


class CForm(QWidget):
    signal_state = pyqtSignal()  # 更新窗口状态的信号
    signal_send = pyqtSignal(dict)  # 发送数据的信号

    def __init__(self, ur):
        super().__init__()
        self.ur = ur
        self.clist_num = 0  # 本机文件数量
        self.slist_num = 0  # 服务器文件数量
        self.input, self.fpath, self.msgbox, self.progress = None, None, None, None
        self.init_ui()

    # 绘制主界面
    def init_ui(self):
        layout_main = QVBoxLayout()
        grid1 = QGridLayout()
        grid1.setSpacing(10)

        # 消息框
        self.msgbox = MyQTextBrowser()
        self.msgbox.setReadOnly(True)
        self.msgbox.append(desc)
        grid1.addWidget(self.msgbox, 0, 0, 1, 4)
        # 发送消息框
        self.input = QLineEdit()
        btn_send_msg = QPushButton('发送消息')
        btn_send_msg.setStyleSheet('QPushButton {background-color: green;}')
        grid1.addWidget(self.input, 1, 0, 1, 3)
        grid1.addWidget(btn_send_msg, 1, 3, 1, 1)
        btn_send_msg.clicked.connect(self.send_msg)

        # 消息发送板块
        group_box_msg = QGroupBox('消息发送')
        group_box_msg.setLayout(grid1)
        # 文件传输板块
        group_box_file = QGroupBox('文件传输')
        grid2 = QGridLayout()
        grid2.setSpacing(10)
        # 选择工作文件夹
        label_wk = QLabel('文件夹:')
        self.fpath = QLineEdit(get_download_folder())
        btn_sel_file = QPushButton('选择文件夹')
        grid2.addWidget(label_wk, 2, 0, 1, 1)
        grid2.addWidget(self.fpath, 2, 1, 1, 3)
        grid2.addWidget(btn_sel_file, 2, 4, 1, 1)
        btn_sel_file.clicked.connect(self.show_dialog)

        # 展示本机文件列表
        label_file_client = QLabel('本机文件:')
        self.cflist = QListView()
        self.cmodel = QStandardItemModel(self.cflist)
        grid2.addWidget(label_file_client, 4, 0, 1, 2)
        grid2.addWidget(self.cflist, 5, 0, 8, 2)

        # 展示服务器文件列表
        label_file_server = QLabel('服务器文件:')
        self.sflist = QListView()
        self.smodel = QStandardItemModel(self.sflist)
        grid2.addWidget(label_file_server, 4, 3, 1, 2)
        grid2.addWidget(self.sflist, 5, 3, 8, 2)

        # 添加操作按钮
        btn_sendf, btn_recef = QToolButton(), QToolButton()
        btn_sendf.setArrowType(Qt.RightArrow), btn_recef.setArrowType(Qt.LeftArrow)
        btn_recef.setEnabled(False), btn_sendf.setEnabled(False)
        grid2.addWidget(btn_sendf, 7, 2, 1, 1), grid2.addWidget(btn_recef, 9, 2, 1, 1)
        btn_sendf.clicked.connect(lambda: self.get_list(self.cmodel, self.clist_num, 'sendf'))
        btn_recef.clicked.connect(lambda: self.get_list(self.smodel, self.slist_num, 'dwnf'))

        self.cmodel.itemChanged.connect(lambda: self.on_changed(self.clist_num, btn_sendf))
        self.smodel.itemChanged.connect(lambda: self.on_changed(self.slist_num, btn_recef))

        # 添加进度条
        # self.progress = QProgressBar()
        self.progress = MyProgressBar()
        self.progress.setStyleSheet("""
                QProgressBar {
                    border-radius: 1px;
                    color: black;
                }
                QProgressBar::chunk {
                    background-color: #05B8CC;
                    border-radius: 0px;
                }
            """)
        # pp.setStyleSheet(f"""
        #         QProgressBar {{
        #             border: solid grey;
        #             border-radius: 15px;
        #             color: black;
        #         }}
        #         QProgressBar::chunk {{
        #             background-color: {colors[i]};
        #             border-radius: 15px;
        #         }}
        #     """)
        grid2.addWidget(self.progress, 13, 0, 1, 5)
        group_box_file.setLayout(grid2)

        layout_main.addWidget(group_box_msg)
        layout_main.addWidget(group_box_file)
        self.setLayout(layout_main)
        self.resize(640, 640)

    # 跳出文件夹选择对话框
    def show_dialog(self):
        path_curr = self.fpath.text()
        upath = QFileDialog.getExistingDirectory(self, '选择文件夹', '.')
        if not upath:
            upath = path_curr
        self.fpath.setText(upath)
        self.upCList(upath)

    # 更新客户端文件列表
    def upCList(self, upath=None):
        if not upath:
            upath = self.fpath.text()
        self.cmodel.clear()
        f_list = [f for f in listdir(upath) if isfile(join(upath, f))]
        self.clist_num = len(f_list)
        for fname in f_list:
            item = QStandardItem()
            item.setText(fname)
            item.setCheckable(True)
            self.cmodel.appendRow(item)  # 将新文件添加进视图中
        self.cflist.setModel(self.cmodel)

    # 更新服务器文件列表
    def upSList(self, slist):
        self.smodel.clear()
        self.slist_num = len(slist)
        for fname in slist:
            item = QStandardItem()
            item.setText(fname)
            item.setCheckable(True)
            self.smodel.appendRow(item)  # 将新文件添加进视图中
        self.sflist.setModel(self.smodel)

    # 获取用户选择的文件列表
    def get_list(self, model, num, tp):
        path = self.fpath.text()
        # 遍历整个视图
        for i in range(num):
            data = {'type': tp, 'cnt': {'ur': self.ur, 'path': path}}
            item = model.item(i)
            # 如果该选项被选中
            if item and item.checkState() == 2:
                fname = item.text()
                data['cnt']['fname'] = fname
                if tp == 'sendf':
                    fsize = getsize(path + '/' + fname)
                    # 判断是否为空文件
                    if fsize > 0:
                        data['cnt']['fsize'] = fsize
                    else:
                        # 空文件报错
                        self.signal_state.emit(fname + '为空文件，无法发送！')
                        continue
                self.signal_send.emit(data)

    # 设置发送下载按钮的可以状态
    def on_changed(self, num, btn):
        sender = self.sender()
        flag = False
        for i in range(num):
            item = sender.item(i)
            if item and item.checkState() == 2:
                flag = True
        btn.setEnabled(flag)

    # 设置进度条最大值
    def set_max_pro(self, num):
        self.progress.setMaximum(num)

    # 更新进度条
    def update_pro(self, num):
        self.progress.setValue(num)

    # 发送信息
    def send_msg(self):
        now = now_hms()
        msg = self.input.text()
        self.msgbox.append('%-15s: %-40s' % (f'本机 - {now}', msg))  # 将信息在对话框中显示
        data = {'type': 'msg', 'cnt': {'ur': self.ur, 'msg': msg}}  # 封装发送的数据
        self.signal_send.emit(data)
        self.input.clear()

    # 显示服务器的信息
    def show_msg(self, msg):
        now = now_hms()
        self.msgbox.append('%-15s: %-40s' % (f'服务器 - {now}', msg))


if __name__ == '__main__':
    pass
