try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
import sys

import pyqtgraph as pg
import random

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QKeySequence, QPixmap, QMovie, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QAction, QLabel, QShortcut, QPushButton, QHBoxLayout, QLabel
import GLWidget
import serial
import re
import math
from RecoveryViewClass import *

alt = 0
time = 0

class ResearchView(QWidget):
    def __init__(self, data_model, SCREEN_WIDTH, SCREEN_HEIGHT):
        super().__init__()
        self.setObjectName("Live")

        self.data_model = data_model

        self.plot_alt = pg.PlotWidget(title="Altitude vs Time")
        self.plot_alt.setLabel('left', 'Altitude', units='m')
        self.plot_alt.setLabel('bottom', 'Time', units='s')
        self.plot_alt.showGrid(x=True, y=True)
        self.plot_alt.setParent(self)
        self.plot_alt.setBackground(QColor('#35353A'))

        self.plot_vel = pg.PlotWidget(title="Velocity vs Time")
        self.plot_vel.setLabel('left', 'Altitude', units='m/s')
        self.plot_vel.setLabel('bottom', 'Time', units='s')
        self.plot_vel.showGrid(x=True, y=True)
        self.plot_vel.setParent(self)
        self.plot_vel.setBackground(QColor('#35353A'))

        self.plot_acc = pg.PlotWidget(title="Acceleration vs Time")
        self.plot_acc.setLabel('left', 'Acceleration', units='m/s\u00B2')
        self.plot_acc.setLabel('bottom', 'Time', units='s')
        self.plot_acc.showGrid(x=True, y=True)
        self.plot_acc.setParent(self)
        self.plot_acc.setBackground(QColor('#35353A'))

        # Arrange plots to fit within a 1080p window
        plot_width = SCREEN_WIDTH * 4 // 9
        plot_height = SCREEN_HEIGHT * 1 // 4
        spacing = 40
        left_margin = 40
        top_margin = 40

        self.plot_alt.setGeometry(left_margin, top_margin, plot_width, plot_height)
        self.plot_vel.setGeometry(left_margin,
                                  top_margin + plot_height + spacing,
                                  plot_width, plot_height)
        self.plot_acc.setGeometry(left_margin,
                                  top_margin + 2 * (plot_height + spacing),
                                  plot_width, plot_height)

        self.x_alt = []
        self.x_vel = []
        self.x_acc = []
        self.y_alt = []
        self.y_vel = []
        self.y_acc = []
        self.max_altitude = 0
        self.max_velocity = 0
        self.max_acceleration = 0

        self.curve = self.plot_alt.plot(pen='r')
        self.curve2 = self.plot_vel.plot(pen='g')
        self.curve3 = self.plot_acc.plot(pen='b')

        self.data_model.new_data.connect(self.update_output)

    def update_output(self, data):
        time_match = re.search('Time: ([0-9]+\\.[0-9])', data)
        if time_match != None:
            time = float(time_match.group(1))

        alt_match = re.search('Altitude: ([0-9]+\\.[0-9]+)',data)
        if alt_match != None:
            alt = float(alt_match.group(1))
            self.y_alt.append(alt)
            self.x_alt.append(time)

        vel_match = re.search('Velocity: ([0-9]+\\.[0-9]+)',data)
        if vel_match != None:
            vel = float(vel_match.group(1))
            self.y_vel.append(vel)
            self.x_vel.append(time)

        acc_match = re.search('Accel: ([0-9]+\\.[0-9]+)',data)
        if acc_match != None:
            acc = float(acc_match.group(1))
            self.y_acc.append(acc)
            self.x_acc.append(time)

        if alt_match != None:
            self.update_alt(time, alt)

        if vel_match != None:
            self.update_vel(time, vel)

        if acc_match != None:
            self.update_accel(time, acc)


    def update_alt(self, time, alt):
        self.curve.setData(self.x_alt, self.y_alt)

        self.max_altitude = max(self.max_altitude, alt)
        rounded_max = ((int(self.max_altitude) // 100) + 1) * 100
        self.plot_alt.enableAutoRange(axis='y')

    def update_vel(self, time, vel):
        self.curve2.setData(self.x_vel, self.y_vel)

        self.max_velocity = max(self.max_velocity, vel)
        rounded_max = ((int(self.max_velocity) // 100) + 1) * 100
        self.plot_vel.enableAutoRange(axis='y')

    def update_accel(self, time, acc):
        self.curve3.setData(self.x_acc, self.y_acc)

        self.max_acceleration = max(self.max_acceleration, acc)
        rounded_max = ((int(self.max_acceleration) // 100) + 1) * 100
        self.plot_acc.enableAutoRange(axis='y')