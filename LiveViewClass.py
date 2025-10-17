try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
import sys
from GeoTiffViewer import *

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QKeySequence, QPixmap, QMovie
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QAction, QLabel, QShortcut, QPushButton, QHBoxLayout, QLabel
import GLWidget
import serial
import re
import math
from nmea_read import *
from RecoveryViewClass import *
from status_checks import *
from SpeedDial import *

PORT = 'COM11'
BaudRate = 9600

class LiveView(QWidget):
    def __init__(self, data_model_main, data_model_backup, geotiff_path, SCREEN_WIDTH, SCREEN_HEIGHT, coordinate_data=None):
        super().__init__()
        # Get the logical DPI)
        self.setObjectName("Live")
        self.speed = 0
        self.alt = 0
        self.temp = 0
        self.volt = 0
        self.lat = 0
        self.lon = 0
        self.first = True

        self.data_model_main = data_model_main
        self.data_model_backup = data_model_backup

        # GeoTIFF Viewer
        self.geotiff_viewer_can = GeoTIFFViewer(geotiff_path, SCREEN_WIDTH * 5 // 9, SCREEN_HEIGHT * 7 // 13 - 100)
        self.geotiff_viewer_can.setParent(self)

        self.output_display_can = QTextEdit(self)
        self.output_display_can.setReadOnly(True)
        self.output_display_can.setStyleSheet("background-color: black; color: lime; font-family: monospace; font-size: 20px;")
        self.output_display_can.setParent(self)

        self.output_display_nmea = QTextEdit(self)
        self.output_display_nmea.setReadOnly(True)
        self.output_display_nmea.setStyleSheet(
            "background-color: black; color: lime; font-family: monospace; font-size: 20px;")
        self.output_display_nmea.setParent(self)

        self.data_model_main.new_data.connect(self.update_output_main)
        self.data_model_backup.new_data.connect(self.update_output_backup)

        # Speed Dial (for updating velocity)
        self.speed_dial = SpeedDial(self, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.speed_dial.setParent(self)

        self.status_checks = Status_Checks(self, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.status_checks.setParent(self)

        widget_width = SCREEN_WIDTH * 3 // 5
        widget_height = SCREEN_HEIGHT * 7 // 13

        self.geotiff_viewer_can.setGeometry(5, 10, widget_width, widget_height)

        # Scale the speed dial to fit within a 1920x1080 display. The original
        # widget size was larger than the available space which caused it and
        # neighbouring widgets to be clipped at the bottom of the screen.

        self.output_display_can.setGeometry(widget_width + 20, 10, SCREEN_WIDTH - widget_width - 25, widget_height // 2 - 10)

        self.output_display_nmea.setGeometry(widget_width + 20, widget_height // 2 + 10, SCREEN_WIDTH - widget_width - 25, widget_height // 2 - 10)

        self.speed_dial.setGeometry(5, widget_height + 20, widget_width, SCREEN_HEIGHT - widget_height - 300)

        self.status_checks.setGeometry(widget_width + 20,widget_height + 10, SCREEN_WIDTH - widget_width - 10,SCREEN_HEIGHT - widget_height + 20)

    def update_output_main(self, data):
        """Update GUI elements and forward coordinate data to the map viewer."""

        self.output_display_can.append(data)
        self.status_checks.armed_check(True)

        speed_match = re.search('Speed: ([0-9]+\\.[0-9]+)', data)
        alt_match = re.search('Altitude: ([0-9]+\\.[0-9]+)', data)
        volt_match = re.search('Voltage: ([0-9]+\\.[0-9]+)', data)
        temp_match = re.search('Temperature: ([0-9]+\\.[0-9]+)', data)
        #lat_match
        #lon_match

        if speed_match != None:
            if abs(self.speed - float(speed_match.group(1))) < 0.1:
                self.status_checks.drogue_check(True)
                self.speed_dial.falling(True)

            self.speed = float(speed_match.group(1))
            self.speed_dial.update_velocity(self.speed)
        if alt_match != None:
            if self.alt < 20 and self.alt != 0 and abs(self.alt - float(alt_match.group(1))) > 0.1:
                self.status_checks.live_check(True)
                self.status_checks.landed_check(False)
            if self.alt < 20 and self.alt != 0 and abs(self.alt - float(alt_match.group(1))) < 0.1:
                self.status_checks.landed_check(True)
                self.status_checks.live_check(False)
                self.speed_dial.landed(True)
            self.alt = float(alt_match.group(1))
            self.speed_dial.set_altitude(self.alt)
        if volt_match != None:
            self.volt = float(volt_match.group(1))
            self.speed_dial.update_volt(self.volt)
        if temp_match != None:
            self.temp = float(temp_match.group(1))
            self.speed_dial.update_temp(self.temp)
        # A new line beginning with "Time" indicates a fresh telemetry packet.
        # Clear any previously stored fields so coordinates from different
        # packets are not mixed together.
        if data.startswith("Time"):
            self._pending_fields = {}

        # Extract telemetry fields from the incoming line
        time_match = re.search(r'Time:?\s*([0-9]+\.?[0-9]*)', data)
        if time_match:
            self._pending_fields['time'] = float(time_match.group(1))

        alt_match = re.search(r'Altitude:?\s*([-0-9]+\.?[0-9]*)', data)
        if alt_match:
            altitude = float(alt_match.group(1))
            self._pending_fields['alt'] = altitude
            self.speed_dial.set_altitude(altitude)

        lat_match = re.search(r'Latitude:?\s*([-0-9]+\.?[0-9]*)', data)
        if lat_match:
            latitude = float(lat_match.group(1))
            self._pending_fields['lat'] = latitude
            self.speed_dial.set_Lat(latitude)

        lon_match = re.search(r'Longitude:?\s*([-0-9]+\.?[0-9]*)', data)
        if lon_match:
            longitude = float(lon_match.group(1))
            self._pending_fields['lon'] = longitude
            self.speed_dial.set_Lon(longitude)

        vel_match = re.search(r'(?:Speed|Velocity):?\s*([-0-9]+\.?[0-9]*)', data)
        if vel_match:
            velocity = float(vel_match.group(1))
            self._pending_fields['vel'] = velocity
            self.speed_dial.update_velocity(velocity)

        # Once all required fields are available, update the GeoTIFF viewer
        required = ('time', 'alt', 'lat', 'lon')
        if all(field in self._pending_fields for field in required):
            final_data = [[
                self._pending_fields['time'],
                self._pending_fields['alt'],
                self._pending_fields['lat'],
                self._pending_fields['lon'],
            ]]
            self.geotiff_viewer_can.update_coordinate_data(final_data)
            # reset buffer for next coordinate set
            self._pending_fields = {}

    def update_output_backup(self, data):
        self.output_display_nmea.append(data)


        

