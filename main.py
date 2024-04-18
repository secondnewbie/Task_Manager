import datetime
import importlib
import pathlib
import logging

from PySide2 import QtWidgets, QtGui, QtCore

from libs.qt import library as qt_lib

from thread import Constant, Signals, UIThread
from view import Todo_Viewer

importlib.reload(qt_lib)

class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.view = Todo_Viewer()

        self.view.set_ui()
        self.setWindowTitle('Task Manager')
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.main_signal()

        self.__msg = qt_lib.LogHandler(out_stream=self.view.debug)
        self.__ui_thread = UIThread(0)

        # emit된 number를 연결
        self.__ui_thread.signals.number.connect(self.print_time)

        self.view.btn_stop.setEnabled(False)
        self.view.btn_pause.setEnabled(False)

        self.view.show()

    def main_signal(self):
        self.view.btn_start.clicked.connect(self.run_start)
        self.view.btn_stop.clicked.connect(self.run_stop)
        self.view.btn_pause.clicked.connect(self.run_pause)
        self.view.todo_list.doubleClicked.connect(self.set_workname)
        self.view.btn_add.clicked.connect(self.slot_add)
        self.view.btn_del.clicked.connect(self.slot_del)

    def slot_add(self):
        """
        todo_list에 아이템을 추가한다.
        """
        ok, text = qt_lib.QtLibs.input_dialog('Add Task', 'write new task', self)
        if len(text):
            self.view.todo_list.addItem(text)

    def slot_del(self):
        """
        todo_list의 아이템을 삭제한다.
        """
        if qt_lib.QtLibs.question_dialog('Delete Task', f'Do you really delete "{self.view.todo_list.currentItem().text()}"?', self):
            self.view.todo_list.takeItem(self.view.todo_list.currentRow())

    def set_workname(self):
        """
        아이템 클릭시 debug창에 알람을 보낸다.
        """
        item = self.view.todo_list.currentItem()
        self.view.todo_work.setText(item.text())
        self.__msg.log_msg(logging.warning, f'Ready to start : {item.text()}')

    @property
    def total_time(self):
        """
        timer에 설정된 시, 분, 초를 초단위로 환산한다.
        """
        time = self.view.timer.text()
        num = time.split(":")
        return int(num[0])*3600+int(num[1])*60+int(num[2])

    def run_start(self):
        """
        작업을 시작할 때 혹은 재개할 때 타이머가 작동할 수 있도록 한다.
        """
        if not self.view.todo_work.text():
            self.__msg.log_msg(logging.warning, 'Choose Task')

        elif self.view.timer.time() == QtCore.QTime(0, 0, 0, 0):
            self.__msg.log_msg(logging.warning, 'Set Timer')

        else:
            self.view.btn_start.setEnabled(False)
            self.view.btn_stop.setEnabled(True)
            self.view.btn_pause.setEnabled(True)

            # 작업을 시작할 때
            if not self.__ui_thread.isRunning():
                self.__ui_thread.bitfield.deactivate(Constant.stop | Constant.pause)

                self.__ui_thread.set_num(self.total_time)

                self.__ui_thread.start()
                self.__ui_thread.daemon = True
                self.__msg.log_msg(logging.warning, 'Start Task!')

                # 작업 시작 시간 기록
                self.start_time = datetime.datetime.now()

            # 작업을 재개할 때
            else:
                if self.__ui_thread.bitfield.confirm(Constant.pause):
                    self.__ui_thread.resume()
                    self.__ui_thread.bitfield.deactivate(Constant.stop | Constant.pause)
                    self.__msg.log_msg(logging.warning, 'Resume Task!')

    def run_stop(self):
        """
        작업을 중단할 때 타이머를 멈출 수 있도록 하거나, 작업이 종료될 때 타이머가 리셋될 수 있도록 한다.
        """
        self.view.btn_start.setEnabled(True)
        self.view.btn_stop.setEnabled(False)
        self.view.btn_pause.setEnabled(False)

        self.__ui_thread.bitfield.activate(Constant.stop)
        self.__ui_thread.bitfield.deactivate(Constant.pause)

        self.__ui_thread.resume()

        # 작업을 중단할 때
        if self.__ui_thread.isRunning():
            self.__msg.log_msg(logging.warning, 'Stop Task!')
        # 작업이 종료될 때
        else:
            self.__msg.log_msg(logging.warning, 'Ready to Start Another Task')
            self.view.btn_stop.setText('Stop')

    def run_pause(self):
        """
        작업을 일시중지할 때 타이머가 멈출 수 있도록 한다.
        """
        self.view.btn_start.setEnabled(True)
        self.view.btn_stop.setEnabled(True)
        self.view.btn_pause.setEnabled(False)

        self.__ui_thread.bitfield.activate(Constant.pause)
        self.__ui_thread.bitfield.deactivate(Constant.stop)
        self.__msg.log_msg(logging.warning, 'Take a break')

    @QtCore.Slot(int)
    def print_time(self, val: int):
        """
        countdown이 lcd화면으로 나올 수 있도록 한다.
        :param val: 초단위로 환산된 시간
        """
        self.view.countdown.display('{0:02d}:{1:02d}:{2:02d}'.format(val//3600, val%3600//60, val%60))
        if val == 0:
            self.__msg.log_msg(logging.warning, f'Finish Task')
            self.view.btn_stop.setText('Reset')

            # 작업 종료 시간 기록
            self.end_time = datetime.datetime.now()
            self.end_msg()

    def end_msg(self):
        """
        작업 종료시 기록할 것인가를 묻는 메시지
        """
        if qt_lib.QtLibs.question_dialog('Info', f'Do you want to make a "{self.view.todo_work.text()}" log?', self):
            self.save_log()

    def save_log(self):
        """
        작업명, 예상소요시간(타이머 설정시간), 시작시간, 끝난시간, 소요시간을 txt 파일로 저장
        """
        log_time = self.end_time - self.start_time
        ok, text = qt_lib.QtLibs.input_dialog('Make Task Log', 'Write file name with ".txt"\nIt saves in $HOME', self)
        with open(pathlib.Path('C:\\Users\\Admin\\Desktop', text), 'wt') as fp:
            fp.write(f'Task name : {self.view.todo_work.text()}'
                     f'\nEstimated Time : {self.total_time//3600}hour {self.total_time%3600//60}minute {self.total_time%60}second'
                     f'\nStart Time : {self.start_time}'
                     f'\nEnd Time : {self.end_time}'
                     f'\nTotal Time : {log_time}')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main = Main()
    app.exec_()
