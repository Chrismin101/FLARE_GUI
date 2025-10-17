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
from PyQt5.QtGui import QPainter, QColor, QPixmap, QPen, QPalette, QFont, QPainterPath, QRegion
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame
import rasterio
import os
import re

class Status_Checks(QFrame):
    def __init__(self, parent, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Status_Checks, self).__init__(parent)
        self.current_velocity = 0
        self.altitude = 0
        self.lat,self.lon = 0,0
        self.speed = 0

        self.status_width = SCREEN_WIDTH - SCREEN_WIDTH * 3 // 5 - 10

        self.status_height = SCREEN_HEIGHT - SCREEN_HEIGHT * 7 // 13 - 350

        self.setFixedSize(self.status_width, self.status_height)
        self.setStyleSheet("""
                            QFrame {
                                background-color: #35353A;
                                border-radius: 20px;
                            }
                            QLabel {
                                background: transparent;
                            }
                        """)

        icon_height = self.status_height * 3 // 14

        self.red_pixmap = QPixmap("Status_Lights/SquidGameR.png")
        self.red_pixmap = self.red_pixmap.scaled(icon_height,icon_height)
        self.green_pixmap = QPixmap("Status_Lights/SquidGameG.png")
        self.green_pixmap = self.green_pixmap.scaled(icon_height,icon_height)

        self.armed = QLabel(self)
        self.armed.setGeometry(100, 75, icon_height,icon_height)
        self.armed.setPixmap(self.red_pixmap)


        self.live = QLabel(self)
        self.live.setPixmap(self.red_pixmap)
        self.live.setGeometry(100,275,icon_height,icon_height)

        self.booster = QLabel(self)
        self.booster.setPixmap(self.red_pixmap)
        self.booster.setGeometry(850, 75, icon_height,icon_height)

        self.main = QLabel(self)
        self.main.setPixmap(self.red_pixmap)
        self.main.setGeometry(850, 275, icon_height,icon_height)

        self.drogue = QLabel(self)
        self.drogue.setPixmap(self.red_pixmap)
        self.drogue.setGeometry(850, 475, icon_height,icon_height)

        self.landed = QLabel(self)
        self.landed.setPixmap(self.red_pixmap)
        self.landed.setGeometry(100, 475, icon_height,icon_height)

        self.background = QPixmap(self.width(), self.height())
        self.background.fill(Qt.transparent)

        painter = QPainter(self.background)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor('#3E3E44'))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(50, 50, self.status_width * 16 // 17 - 10, self.status_height * 6 // 7, 30, 30)

        painter.setFont(QtGui.QFont("OCR A Extended", 24))
        painter.setPen(Qt.white)  # Make sure text is visible
        painter.drawText(100, 100, "Armed")
        painter.drawText(100, 300, "Live")
        painter.drawText(850, 100, "Booster")
        painter.drawText(850, 300, "Main")
        painter.drawText(850, 500, "Drogue")
        painter.drawText(100, 500, "Landed")
        painter.end()

        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(self.background)
        self.bg_label.lower()
        self.bg_label.setGeometry(0, 0, self.width(), self.height())






        painter.end()



    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.background)

    def live_check(self, ready):
            if ready:
                self.live.setPixmap(self.green_pixmap)
            else:
                self.live.setPixmap(self.red_pixmap)
    def armed_check(self,ready):
        if ready:
            self.armed.setPixmap(self.green_pixmap)
        else:
            self.armed.setPixmap(self.red_pixmap)
    def booster_check(self,ready):
        if ready:
            self.booster.setPixmap(self.green_pixmap)
        else:
            self.booster.setPixmap(self.red_pixmap)
    def main_check(self, ready):
        if ready:
            self.main.setPixmap(self.green_pixmap)
        else:
            self.main.setPixmap(self.red_pixmap)
    def drogue_check(self, ready):
        if ready:
            self.drogue.setPixmap(self.green_pixmap)
        else:
            self.drogue.setPixmap(self.red_pixmap)
    def landed_check(self, ready):
        if ready:
            self.landed.setPixmap(self.green_pixmap)
        else:
            self.landed.setPixmap(self.red_pixmap)

