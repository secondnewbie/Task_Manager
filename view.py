import datetime
import importlib
import pathlib
import logging

from PySide2 import QtWidgets, QtGui, QtCore

from libs.qt import library as qt_lib

importlib.reload(qt_lib)

class Todo_Viewer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.set_ui()
        self.setWindowTitle('Task Manager')
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

    def set_ui(self):
        # list_name
        list_name = QtWidgets.QLabel()
        list_name.setText('TODO LIST')

        # todo_list
        self.todo_list = QtWidgets.QListWidget()

        # todo_btn
        self.btn_add = QtWidgets.QPushButton('Add')
        self.btn_del = QtWidgets.QPushButton('Delete')

        # todo_work
        self.todo_work = QtWidgets.QLineEdit()
        self.todo_work.setDisabled(True)

        # timer
        self.timer = QtWidgets.QTimeEdit()
        self.timer.setDisplayFormat('hh:mm:ss')

        # countdown
        self.countdown = QtWidgets.QLCDNumber()
        self.countdown.setDigitCount(10)
        self.countdown.display('00:00:00')
        self.countdown.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        # timer_button
        self.btn_start = QtWidgets.QPushButton('START')
        self.btn_pause = QtWidgets.QPushButton('PAUSE')
        self.btn_stop = QtWidgets.QPushButton('STOP')

        # debug
        self.debug = QtWidgets.QTextBrowser()

        # layout 설정
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addWidget(self.todo_work)
        v_layout.addWidget(self.countdown)
        v_layout.addWidget(self.timer)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.btn_start)
        h_layout.addWidget(self.btn_pause)
        h_layout.addWidget(self.btn_stop)

        v_layout_2 = QtWidgets.QVBoxLayout()
        v_layout_2.addLayout(v_layout)
        v_layout_2.addLayout(h_layout)
        v_layout_2.addWidget(self.debug)

        h_layout_2 = QtWidgets.QHBoxLayout()
        h_layout_2.addWidget(self.btn_add)
        h_layout_2.addWidget(self.btn_del)

        v_layout_3 = QtWidgets.QVBoxLayout()
        v_layout_3.addWidget(list_name)
        v_layout_3.addWidget(self.todo_list)
        v_layout_3.addLayout(h_layout_2)

        h_layout_3 = QtWidgets.QHBoxLayout()
        h_layout_3.addLayout(v_layout_3)
        h_layout_3.addLayout(v_layout_2)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(h_layout_3)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    todoview = Todo_Viewer()
    todoview.show()
    app.exec_()
