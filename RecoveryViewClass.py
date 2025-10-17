try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
import sys
from GeoTiffViewer import *

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QKeySequence, QPixmap, QMovie, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QAction, QLabel, QShortcut, QPushButton, QHBoxLayout, QLabel
import GLWidget
import serial
import re
import math
from nmea_read import *
from RecoveryViewClass import *
from SpeedDial import *

class RecoveryView(QWidget):
    def __init__(self, data_model_main, data_model_backup, geotiff_path, SCREEN_WIDTH, SCREEN_HEIGHT, coordinate_data=None):
        super().__init__()
        self.setObjectName("Recovery")

        self.data_model_main = data_model_main

        self.data_model_backup = data_model_backup

        widget_width = SCREEN_WIDTH // 2 - 5
        widget_height = SCREEN_HEIGHT * 7 // 13

        # GeoTIFF Viewer
        self.geotiff_viewer_can = GeoTIFFViewer(geotiff_path, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT * 7 // 13 - 100)
        self.geotiff_viewer_can.setParent(self)

        self.geotiff_viewer_nmea = GeoTIFFViewer(geotiff_path, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT * 7 // 13 - 100)
        self.geotiff_viewer_nmea.setParent(self)

        # Speed Dial (for updating velocity)
        self.speed_dial = SpeedDial(self, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.speed_dial.setParent(self)

        self.nmea_read = NMEA_Read(self, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.nmea_read.setParent(self)

        self.geotiff_viewer_can.setGeometry(5, 10, widget_width, widget_height)

        self.geotiff_viewer_nmea.setGeometry(SCREEN_WIDTH - widget_width + 5, 10, widget_width, widget_height)

        self.speed_dial.setGeometry(5, widget_height + 20, widget_width, SCREEN_HEIGHT - widget_height - 300)

        self.nmea_read.setGeometry(widget_width + SCREEN_WIDTH // 9 - 15,widget_height + SCREEN_HEIGHT // 100 - 5, 0,0)

        self.data_model_main.new_data.connect(self.update_output_main)
        self.data_model_backup.new_data.connect(self.update_output_backup)

        
    def update_output_main(self, data):
        """Update GUI elements and forward coordinate data to the map viewer."""

        speed_match = re.search('Speed: ([0-9]+\\.[0-9]+)', data)
        alt_match = re.search('Altitude: ([0-9]+\\.[0-9]+)', data)
        volt_match = re.search('Voltage: ([0-9]+\\.[0-9]+)', data)
        temp_match = re.search('Temperature: ([0-9]+\\.[0-9]+)', data)


        if speed_match != None:
            self.speed = float(speed_match.group(1))
            self.speed_dial.update_velocity(self.speed)
        if alt_match != None:
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
        gga_match = re.search('GPGGA', data)
        rmc_match = re.search('GPRMC', data)

        if gga_match != None:

            fields = data.split(",")


            lat = float(fields[2])/ 100
            lon = float(fields[4])/ 100
            alt = float(fields[9])

            self.nmea_read.set_Lat(lat)
            self.nmea_read.set_Lon(lon)
            self.nmea_read.set_altitude(alt)
            final_data = [[
                0,
                alt,
                lat,
                lon,
            ]]
            self.geotiff_viewer_nmea.update_coordinate_data(final_data)


        if rmc_match != None:
            fields = data.split(",")

            speed = float(fields[7]) * 1.94384
            self.nmea_read.update_velocity(speed)

