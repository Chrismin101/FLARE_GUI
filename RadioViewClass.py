try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
import sys
from GeoTiffViewer import *

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QSize, QThread
from PyQt5.QtGui import QKeySequence, QPixmap, QMovie
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QAction, QLabel, QShortcut, QPushButton, QHBoxLayout, QLabel, QComboBox, QListView
import GLWidget
import serial
import re
import math
from nmea_read import *
from RecoveryViewClass import *
from status_checks import *
import serial
from serial.tools import list_ports
from datetime import datetime
from RSSIMeter import *
from LinkQuality import *

geotiff_path = "maps/hillshade.tif"

class ClickToEditLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)


    def mousePressEvent(self, event):
        self.setReadOnly(False)
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
            BaudRate = event.key()
        else:
            super().keyPressEvent(event)


class RadioView(QWidget):
    def __init__(self, serial_manager_main, data_model_main, thread_main, serial_manager_backup, data_model_backup, thread_backup, SCREEN_WIDTH, SCREEN_HEIGHT):
        super().__init__()
        self.file_cursor = 0
        self.sm_baudrate = 1200
        self.sb_baudrate = 1200
        self.b_baudrate = 1200
        self.sm_PORT = ''
        self.sb_PORT = ''
        self.b_PORT = ''
        self.setObjectName("Radio")

        self.time = 0

        self.data_model_main = data_model_main

        self.serial_manager_main = serial_manager_main

        self.thread_main = thread_main

        self.data_model_backup = data_model_backup

        self.serial_manager_backup = serial_manager_backup

        self.thread_backup = thread_backup

        self.RSSIMeter = RSSIMeter(SCREEN_WIDTH)
        self.RSSIMeter.setParent(self)
        self.RSSIMeter.setGeometry(-SCREEN_WIDTH // 12,SCREEN_HEIGHT * 4// 9 - SCREEN_WIDTH // 9, SCREEN_WIDTH * 8//9,SCREEN_WIDTH // 4)

        self.link_signal = LinkQuality()
        self.link_signal.setParent(self)
        self.link_signal.setGeometry(150 + SCREEN_WIDTH // 5, SCREEN_HEIGHT * 4 // 9, SCREEN_WIDTH // 4, SCREEN_WIDTH // 4)


        self.radio_select = QComboBox()
        self.radio_select.addItems([
            "Sustainer - Main",
            "Booster",
            "Sustainer - Backup"
        ])
        self.radio_select.setParent(self)
        self.radio_select.activated.connect(self.radio_select_activated)
        self.radio_select.setGeometry(0, 0, 960, 100)
        self.radio_select.setStyleSheet("""
    QComboBox {
        font-size: 48px;
        min-height: 40px;
    }
    QComboBox QAbstractItemView {
        font-size: 48px;
        min-height: 40px;
    }
""")



        self.port_select = QComboBox()
        ports = serial.tools.list_ports.comports()
        self.port_select.addItem("Not_Selected", userData = "")
        for port, desc, hwid in sorted(ports):
            self.port_select.addItem("{}: {} [{}]".format(port, desc, hwid), userData = port)

        self.port_select.setParent(self)
        self.port_select.setGeometry(0, 100, 960, 100)
        self.port_select.hide()
        self.port_select.activated.connect(self.port_select_activated)
        self.port_select.setStyleSheet("""
    QComboBox {
        font-size: 54px;
        min-height: 40px;
    }
    QComboBox QAbstractItemView {
        font-size: 54px;
        min-height: 40px;
    }
""")

        self.sm_baudrate_select = QComboBox()
        self.sm_baudrate_select.addItems([
            '1200',
            '2400',
            '4800',
            '9600',
            '19200',
            '38400'
        ])
        self.sm_baudrate_select.setParent(self)
        self.sm_baudrate_select.setGeometry(0, 200, 480, 100)
        self.sm_baudrate_select.hide()
        self.sm_baudrate_select.activated.connect(self.sm_baudrate_select_activated)
        self.sm_baudrate_select.setStyleSheet("""
    QComboBox {
        font-size: 48px;
        min-height: 40px;
    }
    QComboBox QAbstractItemView {
        font-size: 48px;
        min-height: 40px;
    }
""")
        self.x = []
        self.y = []

        self.plot_rssi = pg.PlotWidget(title="RSSI vs Time")
        self.plot_rssi.setLabel('left', 'Altitude', units='dBm')
        self.plot_rssi.setLabel('bottom', 'Time', units='s')
        self.plot_rssi.showGrid(x=True, y=True)
        self.plot_rssi.setParent(self)
        self.plot_rssi.setGeometry(SCREEN_WIDTH // 2 + SCREEN_WIDTH // 800, SCREEN_HEIGHT // 3 + 100 , SCREEN_WIDTH // 2 - SCREEN_WIDTH // 100, SCREEN_HEIGHT * 4 // 9)
        self.plot_rssi.setYRange(0, -127)
        self.plot_rssi.setBackground(QColor('#35353A'))

        self.curve = self.plot_rssi.plot(pen='r')

        self.sb_baudrate_select = QComboBox()
        self.sb_baudrate_select.addItems([
            '1200',
            '2400',
            '4800',
            '9600',
            '19200',
            '38400'
        ])
        self.sb_baudrate_select.setParent(self)
        self.sb_baudrate_select.setGeometry(0, 200, 480, 100)
        self.sb_baudrate_select.hide()
        self.sb_baudrate_select.activated.connect(self.sb_baudrate_select_activated)
        self.sb_baudrate_select.setStyleSheet("""
    QComboBox {
        font-size: 48px;
        min-height: 40px;
    }
    QComboBox QAbstractItemView {
        font-size: 48px;
        min-height: 40px;
    }
""")

        self.b_baudrate_select = QComboBox()
        self.b_baudrate_select.addItems([
            '1200',
            '2400',
            '4800',
            '9600',
            '19200',
            '38400'
        ])
        self.b_baudrate_select.setParent(self)
        self.b_baudrate_select.setGeometry(0, 200, 480, 100)
        self.b_baudrate_select.hide()
        self.b_baudrate_select.activated.connect(self.b_baudrate_select_activated)
        self.b_baudrate_select.setStyleSheet("""
    QComboBox {
        font-size: 48px;
        min-height: 40px;
    }
    QComboBox QAbstractItemView {
        font-size: 48px;
        min-height: 40px;
    }
""")

        self.freq_input = ClickToEditLineEdit()
        self.freq_input.setText("Freq (MHz)")
        self.freq_input.setParent(self)
        self.freq_input.setGeometry(480, 200, 480, 100)
        self.freq_input.hide()
        self.freq_input.setStyleSheet("""
    QLineEdit {
        font-size: 48px;
        min-height: 40px;
    }
""")

        self.smconnect = QPushButton("SM Connect")
        self.smconnect.setParent(self)
        self.smconnect.setGeometry(25, SCREEN_HEIGHT * 3 // 5, SCREEN_HEIGHT * 2 // 3, SCREEN_HEIGHT // 4)
        self.smconnect.clicked.connect(self.rf_sm_connect)
        self.smconnect.setIcon(QIcon("Status_Lights/SquidGameR.png"))
        self.smconnect.setIconSize(QSize(250,250))
        self.smconnect.hide()
        self.smconnect.setStyleSheet("""
    QPushButton {
        font-size: 104px;
        min-height: 40px;
    }
""")

        self.sbconnect = QPushButton("SB Connect")
        self.sbconnect.setParent(self)
        self.sbconnect.setGeometry(25, SCREEN_HEIGHT * 3 // 5, SCREEN_HEIGHT * 2 // 3, SCREEN_HEIGHT // 4)
        self.sbconnect.clicked.connect(self.rf_sb_connect)
        self.sbconnect.setIcon(QIcon("Status_Lights/SquidGameR.png"))
        self.sbconnect.setIconSize(QSize(250, 250))
        self.sbconnect.hide()
        self.sbconnect.setStyleSheet("""
    QPushButton {
        font-size: 104px;
        min-height: 40px;
    }
""")

        self.bconnect = QPushButton("B Connect")
        self.bconnect.setParent(self)
        self.bconnect.setGeometry(25, SCREEN_HEIGHT * 3 // 5, SCREEN_HEIGHT * 2 // 3, SCREEN_HEIGHT // 4)
        self.bconnect.clicked.connect(self.rf_b_connect)
        self.bconnect.setIcon(QIcon("Status_Lights/SquidGameR.png"))
        self.bconnect.setIconSize(QSize(250, 250))
        self.bconnect.hide()
        self.bconnect.setStyleSheet("""
    QPushButton {
        font-size: 104px;
        min-height: 40px;
    }
""")

        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet(
            "background-color: black; color: lime; font-family: monospace; font-size: 24px;")
        self.output_display.setParent(self)
        self.output_display.setGeometry(SCREEN_WIDTH // 2 + SCREEN_WIDTH // 800, 50, SCREEN_WIDTH // 2 - SCREEN_WIDTH // 100, SCREEN_HEIGHT // 3)



    def update_output(self, data):
        self.output_display.append(data)

        time_match = re.search('Time: ([0-9]+\\.[0-9])', data)
        rssi_match = re.search('RSSI: (-*[0-9]+)',data)
        link_quality_match = re.search('Link Quality: ([0-9]{2})', data)

        if time_match != None:
            self.time = float(time_match.group(1))
        if rssi_match != None:
            rssi = float(rssi_match.group(1))
            self.x.append(self.time)
            self.y.append(rssi)
            self.update_rssi()
            self.RSSIMeter.update_goods(rssi)
        if link_quality_match != None:
            link_quality = int(link_quality_match.group(1))
            self.link_signal.update_goods(link_quality)
    def update_rssi(self):
        self.curve.setData(self.x, self.y)

    def rf_sm_connect(self, index):

        try:
            self.serial_manager_main.configure(self.sm_PORT, self.sm_baudrate)

            self.thread_main.start()

            self.smconnect.setIcon(QIcon("Status_Lights/SquidGameG.png"))

            self.data_model_main.new_data.connect(self.update_output)

            self.port_select.removeItem(self.port_select.currentIndex())
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_port = None
    def rf_sb_connect(self, index):

        try:
            self.serial_manager_main.configure(self.sb_PORT, self.sb_baudrate)

            self.thread_main.start()

            self.sbconnect.setIcon(QIcon("Status_Lights/SquidGameG.png"))

            self.port_select.removeItem(self.port_select.currentIndex())
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_port = None
    def rf_b_connect(self, index):

        try:
            self.serial_manager_backup.configure(self.b_PORT, self.b_baudrate)

            self.thread_backup.start()

            self.bconnect.setIcon(QIcon("Status_Lights/SquidGameG.png"))

            self.data_model_backup.new_data.connect(self.update_output)

            self.port_select.removeItem(self.port_select.currentIndex())

        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_port = None
        
    def sm_baudrate_select_activated(self):
        self.sm_baudrate = int(self.sm_baudrate_select.currentText())

    def sb_baudrate_select_activated(self):
        self.sb_baudrate = int(self.sm_baudrate_select.currentText())

    def b_baudrate_select_activated(self):
        self.b_baudrate = int(self.sm_baudrate_select.currentText())

    def radio_select_activated(self, index):
        if index == 0:
            self.smconnect.show()
            self.sbconnect.hide()
            self.bconnect.hide()
        if index == 1:
            self.bconnect.show()
            self.smconnect.hide()
            self.sbconnect.hide()
        if index == 2:
            self.sbconnect.show()
            self.smconnect.hide()
            self.bconnect.hide()
        self.output_display.clear()
        self.port_select.show()
        self.sm_baudrate_select.show()
        self.freq_input.show()

    def port_select_activated(self, index):
        if self.radio_select.currentIndex() == 0:

            self.sm_PORT = self.port_select.itemData(index)
        if self.radio_select.currentIndex() == 2:
            self.sb_PORT = self.port_select.itemData(index)

        if self.radio_select.currentIndex() == 1:
            self.b_PORT = self.port_select.itemData(index)

