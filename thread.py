import importlib

from PySide2 import QtWidgets, QtGui, QtCore

from libs.algorithm.library import BitMask

class Constant:
    """
    pause, stop에 대한 BitMask 설정
    """
    __slots__ = ()
    pause: int = 1
    stop: int = 2

Constant = Constant()

class Signals(QtCore.QObject):
    """
    number 시그널 설정
    """
    number = QtCore.Signal(int)

class UIThread(QtCore.QThread):
    def __init__(self, num: int):
        """
        :param num: 타이머 설정 전 default 숫자
        """
        super().__init__()
        self.__num = num

        self.__bitfield = BitMask()

        # stop, pause의 default Bitmask는 0으로 설정
        self.__bitfield.deactivate(Constant.stop | Constant.pause)

        self.signals = Signals()

        self.__condition = QtCore.QWaitCondition()
        self.__mutex = QtCore.QMutex()

    @property
    def bitfield(self):
        return self.__bitfield

    def resume(self):
        """
        pause나 stop이 활성화되어있을 때, 깨운다.
        """
        if self.bitfield.confirm(Constant.pause | Constant.stop):
            self.__condition.wakeAll()

    def set_num(self, val: int):
        """
        :param val: 타이머에 설정된 값
        """
        self.__num = val

    def run(self):
        numm = int(self.__num)

        # 카운트다운 구현
        for i in range(numm, -1, -1):
            if self.bitfield.confirm(Constant.pause):
                self.__condition.wait(self.__mutex)

            if not self.bitfield.confirm(Constant.stop):
                self.signals.number.emit(i)
                self.sleep(1)
            else:
                break

if __name__ == '__main__':
    pass