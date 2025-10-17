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

class RSSIMeter(QFrame):
    def __init__(self, SCREEN_WIDTH, parent=None):
        super(RSSIMeter, self).__init__(parent)
        self.current_rssi = 0
        self.SCREEN_WIDTH = SCREEN_WIDTH

        self.background = QPixmap(SCREEN_WIDTH, SCREEN_WIDTH)
        print(self.size())
        self.background.fill(Qt.transparent)

        painter = QPainter(self.background)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(Qt.black, 10))

        R = self.SCREEN_WIDTH // 10  # Outer radius
        r = self.SCREEN_WIDTH * 3 //80  # Inner radius

        outer_rect = QRectF(self.SCREEN_WIDTH // 5 - R, self.SCREEN_WIDTH // 5 - R, 2 * R, 2 * R)
        inner_rect = QRectF(self.SCREEN_WIDTH // 5 - r, self.SCREEN_WIDTH // 5 - r, 2 * r, 2 * r)

        start_angle = 30
        self.span_angle = 120

        self.inner_radius = R * 0.85
        self.outer_radius = R * 1

        segment_colors = [Qt.red, Qt.green, Qt.blue]
        segment_span = self.span_angle / len(segment_colors)

        path = QPainterPath()
        path.moveTo(self.SCREEN_WIDTH // 5, self.SCREEN_WIDTH // 5)
        path.arcTo(outer_rect, start_angle, self.span_angle)
        path.closeSubpath()

        painter.drawPath(path)

        segment_colors = [QColor("#60a757"), QColor("#9cc357"), QColor("#dcd14b"), QColor("#e5ab43"), QColor("#d46f38"),
                          QColor("#cb3831")]
        segment_span = 15
        seg_start = start_angle
        for i, color in enumerate(segment_colors):
            if i == 0 or i == len(segment_colors) - 1:
                segment_span = 15
            else:
                segment_span = 22.5

            path = QPainterPath()
            outer_rect = QRectF(self.SCREEN_WIDTH // 5 - R, self.SCREEN_WIDTH // 5 - R, 2 * R, 2 * R)
            inner_rect = QRectF(self.SCREEN_WIDTH // 5 - r, self.SCREEN_WIDTH // 5 - r, 2 * r, 2 * r)

            path.arcMoveTo(outer_rect, seg_start)
            path.arcTo(outer_rect, seg_start, segment_span)
            path.arcTo(inner_rect, seg_start + segment_span, -segment_span)
            path.closeSubpath()

            seg_start += segment_span

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.black, 0))
            painter.drawPath(path)
        painter.end()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, self.background)
        
        painter.setPen(QPen(Qt.black, 2))
        for i in range(int(self.span_angle / 2) + 1):
            angle = -135 + (i * 90 / 60)  # start from -90 degrees
            rad = math.radians(angle)

            if i % 10 == 0:
                x1 = int(self.SCREEN_WIDTH // 5 + self.inner_radius * math.cos(rad) * 0.85)
                y1 = int(self.SCREEN_WIDTH // 5 + self.inner_radius * math.sin(rad) * 0.85)
            elif i % 5 == 0:
                x1 = int(self.SCREEN_WIDTH // 5 + self.inner_radius * math.cos(rad) * 0.95)
                y1 = int(self.SCREEN_WIDTH // 5 + self.inner_radius * math.sin(rad) * 0.95)
            else:
                x1 = int(self.SCREEN_WIDTH // 5 + self.inner_radius * math.cos(rad))
                y1 = int(self.SCREEN_WIDTH // 5 + self.inner_radius * math.sin(rad))
            x2 = int(self.SCREEN_WIDTH // 5 + self.outer_radius * math.cos(rad))
            y2 = int(self.SCREEN_WIDTH // 5 + self.outer_radius * math.sin(rad))
            painter.drawLine(x1, y1, x2, y2)

        if (-90 <= self.current_rssi <= -30):
            needle_angle = (self.current_rssi / 60) * 90
        elif self.current_rssi > -30:
            needle_angle = (self.current_rssi / 30) * 15 - 30
        elif self.current_rssi < -90:
            needle_angle = (self.current_rssi / 30) * 15 - 90

        rad = math.radians(needle_angle)
        needle_length = self.inner_radius
        x_needle = int(self.SCREEN_WIDTH // 5 + needle_length * math.cos(rad))
        y_needle = int(self.SCREEN_WIDTH // 5 + needle_length * math.sin(rad))

        painter.setPen(QPen(Qt.red, 6, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(self.SCREEN_WIDTH // 5, self.SCREEN_WIDTH // 5, x_needle, y_needle)



    def update_goods(self, rssi):
        self.current_rssi = float(rssi)
        self.update()
