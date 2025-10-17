try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from PyQt5.QtWidgets import *
import math
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QPalette, QFont, QPainterPath, QRegion, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame


class SpeedDial(QFrame):
    def __init__(self, parent, SCREEN_WIDTH, SCREEN_HEIGHT, *args, **kwargs):
        super(SpeedDial, self).__init__(parent)
        self.current_velocity = 0
        self.altitude = 0
        self.lat,self.lon = 0,0
        self.max_velocity = 3.0

        self.dial_width = SCREEN_WIDTH * 3 // 5
        self.dial_height = SCREEN_HEIGHT - SCREEN_HEIGHT * 7 // 13 - 350

        self.initial_volt = 1
        self.initial_volt_check = True


        self.temp = 0

        self.temp_images = []
        for i in range(11):
            self.temp_images.append(QPixmap(f"temp_gauges/temp_{i}.png"))

        self.label = QLabel()
        self.label.setPixmap(self.temp_images[0])
        self.label.setParent(self)
        self.label.setScaledContents(True)
        self.label.setGeometry(self.dial_width * 2 // 3,100, self.dial_width // 21,self.dial_height * 4 // 7)

        self.volt = 0

        self.volt_images = []
        for i in range(4):
            self.volt_images.append(QPixmap(f"battery_levels/battery_{i}.png"))

        self.label2 = QLabel()
        self.label2.setPixmap(self.volt_images[0])
        self.label2.setParent(self)
        self.label2.setScaledContents(True)
        self.label2.setGeometry(self.dial_width * 5 // 6, 100, self.dial_width // 12, self.dial_height // 2)

        self.label3 = QLabel()
        self.label3.setPixmap(QPixmap("Rocket_Pics/Rocket_Flight.png"))
        self.label3.setParent(self)
        self.label3.setScaledContents(True)
        self.label3.setGeometry(self.dial_width // 2, self.dial_height * 6// 7, self.dial_width // 25, self.dial_width // 15)

        self.setFixedSize(self.dial_width, self.dial_height)
        self.setStyleSheet("""
            QFrame {
                background-color: #35353A;
                border-radius: 20px;
            }
            QLabel {
                background: transparent;
            }
        """)

        self.background = QPixmap(self.dial_width, self.dial_height)
        self.background.fill(Qt.transparent)

        painter = QPainter(self.background)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QtCore.QRect(50, 50, self.dial_width - 100, self.dial_height - 100)
        painter.setBrush(QColor('#3E3E44'))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 30, 30)

        self.radius = self.dial_height * 2 // 7
        self.center = QtCore.QPoint(self.dial_height * 2 // 5, self.dial_height // 2 - 40)
        radius = self.radius

        # Outer ring
        painter.setPen(QPen(QColor(200, 200, 200), 4))
        painter.setBrush(QColor(10, 10, 10))
        painter.drawEllipse(self.center, radius, radius)

        # Tick marks and labels
        painter.setPen(QPen(Qt.white, 2))
        font = QtGui.QFont("Arial", 12)
        font.setBold(True)
        painter.setFont(font)

        tick_radius_outer = radius * 0.95
        tick_radius_inner = radius * 0.85
        label_radius = radius * 0.7

        num_ticks = 9
        for i in range(num_ticks + 1):
            angle = -90 + (i * 324 / num_ticks)  # start from -90 degrees
            rad = math.radians(angle)
            x1 = int(self.center.x() + tick_radius_inner * math.cos(rad))
            y1 = int(self.center.y() + tick_radius_inner * math.sin(rad))
            x2 = int(self.center.x() + tick_radius_outer * math.cos(rad))
            y2 = int(self.center.y() + tick_radius_outer * math.sin(rad))
            painter.drawLine(x1, y1, x2, y2)

            # Mach number labels (M0.0 to M3.0)
            mach_number = round(i * self.max_velocity / num_ticks, 1)
            lx = int(self.center.x() + label_radius * math.cos(rad))
            ly = int(self.center.y() + label_radius * math.sin(rad))
            painter.drawText(lx - 30, ly + 5, f"M{mach_number:.1f}")

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.blue)
        painter.drawRect(self.dial_width // 2, self.dial_height // 7, self.dial_width // 25, self.dial_height * 5 // 7)
        painter.end()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.background)

        mach = self.current_velocity / 343.0
        needle_angle = (mach / self.max_velocity) * 180
        rad = math.radians(needle_angle)
        needle_length = self.radius * 0.8
        x_needle = int(self.center.x() + needle_length * math.cos(rad))
        y_needle = int(self.center.y() + needle_length * math.sin(rad))

        painter.setPen(QPen(Qt.red, 6, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(self.center.x(), self.center.y(), x_needle, y_needle)

        # self.center circle (pivot)
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.center, 8, 8)

        # Velocity display
        painter.setPen(Qt.white)
        painter.setFont(QtGui.QFont("OCR A Extended", 18))
        painter.drawText(self.radius, self.radius * 3, f"{self.current_velocity:.2f} m/s")

        painter.drawText(self.dial_width * 2 // 3, self.radius * 3, f"{self.temp:.1f} °C")
        painter.drawText(self.dial_width * 5 // 6 + 10, self.radius * 3, f"{self.volt:.1f} V")

        # Altitude and Coordinates
        painter.setFont(QtGui.QFont("OCR A Extended", 16))
        painter.drawText(600, 210, f"Altitude : {self.altitude} m")
        painter.drawText(600, 340, f"Latitude : {self.lat}°")
        painter.drawText(600, 470, f"Longitude : {self.lon}°")

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)
        painter.drawRect(self.dial_width // 2, self.dial_height // 7, self.dial_width // 25, self.dial_height * 5 // 7 - int(math.ceil(float(self.altitude) * 600 / 18800) ))
        self.label3.setGeometry(self.dial_width // 2, self.dial_height * 6// 7 - int(math.ceil(float(self.altitude) * 600 / 18800)), self.dial_width // 25, self.dial_width // 15)

        index = min(10, int((self.temp / 100) * 10))
        self.label.setPixmap(self.temp_images[index])

        index = min(3, int((self.volt / self.initial_volt) * 3))
        self.label2.setPixmap(self.volt_images[index])

    def update_velocity(self, velocity):
        self.current_velocity = float(velocity)
        self.update()

    def update_temp(self, temp):
        self.temp = temp
        self.update()

    def update_volt(self,volt):
        if self.initial_volt_check:
            self.initial_volt = volt
            self.initial_volt_check = False
        else:
            self.volt = volt

    def set_altitude(self, altitude):
        self.altitude = altitude
        self.update()

    def set_Lat(self, latitude):
        self.lat= latitude
        self.update()
    def set_Lon(self, longitude):
        self.lon= longitude
        self.update()
    def falling(self, ready):
        if ready:
            self.label3.setPixmap(QPixmap("Rocket_Pics/Rocket_Landing.png"))
            ready = False
    def landed(self, ready):
        if ready:
            self.label3.setPixmap(QPixmap("Rocket_Pics/Rocket_Landed.png"))
            ready = False