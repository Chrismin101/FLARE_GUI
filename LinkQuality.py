try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from PyQt5.QtWidgets import *
import math
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QPalette, QFont, QPainterPath, QRegion, QBrush, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame
import rasterio
import os
import re

class LinkQuality(QFrame):
    def __init__(self, *args, **kwargs):
        super(LinkQuality, self).__init__(*args, **kwargs)
        self.current_quality = 0

        self.label = QLabel()
        no_pixmap = QPixmap("wifi_signals/no_wifi.png")
        self.red_pixmap = QPixmap("wifi_signals/wifi_red.png")
        self.yellow_pixmap = QPixmap("wifi_signals/wifi_yellow.png")
        self.blue_pixmap = QPixmap("wifi_signals/wifi_blue.png")
        self.green_pixmap = QPixmap("wifi_signals/wifi_green.png")

        self.label.setPixmap(no_pixmap)

        self.label.setParent(self)

        self.label.setScaledContents(True)
        self.label.resize(350,250)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.current_quality == 0:
            pass
        elif self.current_quality < 40:
            self.label.setPixmap(self.red_pixmap)
        elif self.current_quality < 60:
            self.label.setPixmap(self.yellow_pixmap)
        elif self.current_quality < 80:
            self.label.setPixmap(self.blue_pixmap)
        elif self.current_quality < 100:
            self.label.setPixmap(self.green_pixmap)






    def update_goods(self, quality):
        self.current_quality = quality
        self.update()
