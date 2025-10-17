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
import rasterio
import os
import re

class NMEA_Read(QFrame):
    def __init__(self, parent, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(NMEA_Read, self).__init__(parent)
        self.current_velocity = 0
        self.altitude = 0
        self.lat,self.lon = 0,0
        self.width = SCREEN_WIDTH - SCREEN_WIDTH * 61 // 100 + 5
        self.height = SCREEN_HEIGHT - SCREEN_HEIGHT * 7 // 13 + 20

        self.setFixedSize(self.width, self.height * 2 // 3  + 15)
        self.setStyleSheet("""
            QFrame {
                background-color: #35353A;
                border-radius: 20px;
            }
        """)

        self.background = QPixmap(self.size())
        self.background.fill(Qt.transparent)

        painter = QPainter(self.background)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QtCore.QRect(45, 45, self.width - 90, self.height * 2 // 3 - 90)
        painter.setBrush(QColor('#3E3E44'))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 30, 30)
        painter.end()



    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0,0,self.background)

        # Velocity display
        painter.setPen(Qt.white)
        painter.setFont(QtGui.QFont("OCR A Extended", 16))
        painter.drawText(self.width // 12, self.height // 8, f"{self.current_velocity:.2f} m/s")

        painter.drawText(self.width // 12, self.height // 4, f"Altitude : {self.altitude} m")
        painter.drawText(self.width // 2, self.height // 8, f"Latitude : {self.lat}°")
        painter.drawText(self.width // 2, self.height // 4, f"Longitude : {self.lon}°")

        painter.drawText(self.width // 12, self.height * 3 // 4, "# of Satellite Connections:")

        self.label = QLabel()
        self.label.setPixmap(QPixmap('nmea_pics/satellite_dish_icon.png'))
        self.label.setParent(self)
        self.label.setScaledContents(True)

    def update_velocity(self, velocity):
        self.current_velocity = float(velocity)
        self.update()

    def set_altitude(self, altitude):
        self.altitude = altitude
        self.update()

    def set_Lat(self, latitude):
        self.lat= latitude
        self.update()
    def set_Lon(self, longitude):
        self.lon= longitude
        self.update()