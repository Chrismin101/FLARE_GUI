from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import serial
import time

class SerialManagerBackup(QObject):
    data_received = pyqtSignal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self._running = True
        self.port = port
        self.baudrate = baudrate

    @pyqtSlot()
    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            while self._running:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    self.data_received.emit(line)
                time.sleep(0.01)
        except Exception as e:
            self.data_received.emit(f"[ERROR] {str(e)}")


    def configure(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

    def stop(self):
        self._running = False
        if hasattr(self, "ser") and self.ser.is_open:
            self.ser.close()