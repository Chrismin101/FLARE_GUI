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
from PyQt5.QtGui import QPainter, QColor, QPen, QPalette, QFont, QPainterPath, QRegion, QPixmap, QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QDesktopWidget

import rasterio
import os
import re



def getColor(alt):
    color_map = [
        (100, (0, 64, 0)),       # dark green
        (1000, (0, 200, 0)),     # green
        (2000, (0, 128, 255)),   # blue
        (10000, (128, 0, 255)),  # violet
        (float('inf'), (255, 0, 0))  # red
    ]
    for threshold, color in color_map:
        if alt < threshold:
            return pg.mkBrush(*color, 255)



class CustomViewBox(pg.ViewBox):
    def __init__(self, parent=None, on_mouse_release_callback=None):
        super().__init__(parent)
        self._callback = on_mouse_release_callback

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        if ev.button() == ev.Buttons.LeftButton and self._callback:
            self._callback()


class GeoTIFFViewer(QMainWindow):
    def __init__(self, geotiff_path, SCREEN_WIDTH, SCREEN_HEIGHT, coordinate_data=None, parent=None):
        super().__init__(parent)
        self.coordinate_data = None
        self.arrows = []
        self.scatter = None
        self.text_item = None
        self.highlighted_index = None
        self.cursor = 0
        self._plotted_marker_count = 0

        # Create a central widget without setting a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        rounded_box = QWidget(central_widget)
        rounded_box.move(100,100)
        central_widget.setStyleSheet("""
            background-color: #35353A;
            border-radius: 20px;
        """)



        self.graphics_layout = pg.GraphicsLayoutWidget(central_widget)
        self.graphics_layout.setGeometry(45, 45, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.graphics_layout.setBackground('#3E3E44')


        # Load GeoTIFF image and transformation
        im21,im22,im23 = self.load_geotiff(geotiff_path, [1,2,3])
        self.image_data, self.transform, self.dims = self.load_geotiff(geotiff_path)
        self.image_data = np.rot90(self.image_data, k=1)

        self.raw_image_data, self.transform, self.dims = self.load_geotiff(geotiff_path, [1, 2, 3])
        self.raw_image_data = np.rot90(self.raw_image_data, k=1)
     
        
        self.view_box = CustomViewBox(on_mouse_release_callback=None)
        self.plot_item = self.graphics_layout.addPlot(viewBox=self.view_box)

        # Add RGB ImageItem
        self.image_item = pg.ImageItem(self.raw_image_data)
        # self.image_item.setTransform(QtGui.QTransform().scale(1, -1))
        self.plot_item.addItem(self.image_item)

        # Lock aspect ratio
        self.plot_item.setAspectLocked(True, ratio=self.dims[0] / self.dims[1])

        # Enable auto-range for proper scaling
        self.plot_item.enableAutoRange()

        # Enable grid
        self.plot_item.showGrid(x=True, y=True, alpha=1)
        self.plot_item.getAxis('left').setPen(pg.mkPen(color='#35353A', width = 2))
        self.plot_item.getAxis('bottom').setPen(pg.mkPen(color='#35353A', width = 2))

        font = QtGui.QFont("Arial", 14)
        self.plot_item.getAxis('bottom').setTickFont(font)
        self.plot_item.getAxis('left').setTickFont(font)

        def update_x_axis():
            x_range = self.plot_item.viewRange()[0]
            x_min = max(0, x_range[0])
            x_max = min(self.raw_image_data.shape[0], x_range[1])
            num = 7

            tick_positions = np.linspace(x_min, x_max, num=num)
            W = self.raw_image_data.shape[0]
            x_ticks = [
                (x, f"{self.transform.c + (W - x) * self.transform.a:.4f}")
                for x in tick_positions
            ]
            self.plot_item.getAxis("bottom").setTicks([x_ticks])

          

        # def update_y_axis():
        #     y_range = self.plot_item.viewRange()[1]  # visible Y range
        #     y_min = min(self.raw_image_data.shape[1], y_range[1])
        #     y_max = self.raw_image_data.shape[1] - min(self.raw_image_data.shape[1], y_range[1])

        #     tick_positions = np.linspace(y_min, y_max, num=7)
        #     y_ticks = [
        #         (y, f"{self.transform[5] + y * self.transform[4]:.4f}")
        #         for y in tick_positions
        #     ]
        #     self.plot_item.getAxis("left").setTicks([y_ticks])



        def update_y_axis():
            y_range = self.plot_item.viewRange()[1]  # visible Y range
            y_min = min(self.raw_image_data.shape[1], y_range[1])
            y_max = max(0,y_range[0])
            num = 7
            tick_positions = np.linspace(y_min,y_max,  num=num)[::-1]
            y_ticks = []
            for i, tick in enumerate(tick_positions):
                y_ticks.append((tick, f"{self.transform.f + self.transform.e * tick:.4f}"))
                
            self.plot_item.getAxis("left").setTicks([y_ticks])
            # self.plot_item.getAxis("left").setScale(-1)
            self.plot_item.invertY(True)
            self.plot_item.invertX(True)

        # Keep axis labels updated while panning/zooming so gridlines appear on both axes
        self.plot_item.sigXRangeChanged.connect(update_x_axis)
        self.plot_item.sigYRangeChanged.connect(update_y_axis)

        # Use a timer to detect when view stops moving before firing update_color_grading
        # self._color_grading_timer = QTimer(self)
        # self._color_grading_timer.setSingleShot(True)
        # self._color_grading_timer.setInterval(1000)  # ms, adjust as needed

        # def schedule_color_grading():
        #     self._color_grading_timer.start()

        # self.plot_item.sigXRangeChanged.connect(schedule_color_grading)
        # self.plot_item.sigYRangeChanged.connect(schedule_color_grading)
        # self._color_grading_timer.timeout.connect(self.update_color_grading)

        # self.update_color_grading()

        # Initial update
        update_x_axis()
        update_y_axis()

        if coordinate_data is not None:
            self.add_markers(coordinate_data)

        # self.update_color_grading_timer = QTimer(self)
        # self.update_color_grading_timer.setInterval(5000)
        # self.update_color_grading_timer.timeout.connect(self.update_color_grading)
        # self.update_color_grading_timer.start()

        self.highlight_circle = pg.ScatterPlotItem()
        self.plot_item.addItem(self.highlight_circle)


    def update_coordinate_data(self, final_data):
        """Add new coordinate data to the map and plot it."""
        if self.coordinate_data is None:
            self.coordinate_data = []

        # store new coordinates and immediately plot only the fresh points
        self.coordinate_data += final_data
        self.add_markers(final_data)


    def load_geotiff(self, file_path, read_bands=None):
        with rasterio.open(file_path) as dataset:
            if read_bands is None:
                image_data = dataset.read(1)  # grayscale fallback
            else:
                image_data = dataset.read(read_bands)  # RGB shape: (3, H, W)
                image_data = np.transpose(image_data, (1, 2, 0))  # -> (H, W, 3)
                image_data = np.clip(image_data, 0, 255).astype(np.uint8)
            transform = dataset.transform
            dims = (transform[0], -transform[4])
        return image_data, transform, dims


    def on_click(self, plot, points):
        if len(points) == 0:
            return

        point = points[0]  # Only handle one for simplicity
        datum = point.data()
        altitude = datum[1]
        lat = datum[2]
        lon = datum[3]
        timestamp = datum[0]

        # self.highlight_marker(point)
        self.highlighted_index = point.index()
        self.show_info_box(altitude, lat, lon, timestamp)

        # Draw a green hollow circle at the clicked point
        pos = point.pos()
        self.highlight_circle.setData([
            {
                'pos': (pos.x(), pos.y()),
                'brush': pg.mkBrush(0, 0, 0, 0),  # Fully transparent fill
                'pen': pg.mkPen('b', width=4),
                'size': 24
            }
        ])

        self.highlight_circle.setZValue(10)  # Ensure highlight_circle is on top

    def show_info_box(self, altitude, lat, lon, timestamp):
        text_str = f"Alt: {altitude}\nLat: {lat}\nLon: {lon}\nTime: {timestamp}"

        if self.text_item is not None:
            self.text_item.setPlainText(text_str)
            return

        self.text_item = QGraphicsTextItem(text_str)
        self.text_item.setDefaultTextColor(QColor(0, 0, 255))
        self.text_item.setFont(QtGui.QFont("Arial", 12, QFont.Weight.Bold))
        self.text_item.setPos(self.graphics_layout.width() - self.text_item.boundingRect().width() - 10,
                              10)  # Set position relative to the top-left corner
        self.graphics_layout.scene().addItem(self.text_item)

        rect_item = QGraphicsRectItem()
        rect_item.setBrush(QColor(0, 0, 0))
        rect_item.setRect(self.text_item.boundingRect().adjusted(-5, -5, 5, 5))
        rect_item.setPos(self.text_item.pos())
        self.graphics_layout.scene().addItem(rect_item)
        self.text_item.setZValue(rect_item.zValue() + 1)  # Ensure the text item is in front of the rectangle

    def highlight_marker(self, point):

        # self.update_color_grading()
        point.setBrush(pg.mkBrush(255, 255, 0, 255))  # Highlight the clicked marker in yellow

    def sanitize(self, data):
        # Sanitize data by removing the youngest entries with the same lat and lon within 0.01
        if not data or len(data) < 2:
            return data
        sanitized = []
        seen = set()
        for entry in reversed(data):
            lat = round(entry[2], 2)
            lon = round(entry[3], 2)
            key = (lat, lon)
            if key in seen:
                continue
            seen.add(key)
            sanitized.append(entry)
        return list(reversed(sanitized))

    def add_markers(self, data, MAX_PLOT_POINTS=999999999):
        data = self.sanitize(data)
        if not data:
            return

        if not hasattr(self, '_all_line_coords'):
            self._all_line_coords = []
        if not hasattr(self, '_plotted_marker_count'):
            self._plotted_marker_count = 0
        if self.scatter is None:
            self.scatter = pg.ScatterPlotItem()
            self.plot_item.addItem(self.scatter)
            self.scatter.setZValue(5)  # Ensure scatter is on top
            self.scatter.sigClicked.connect(self.on_click)

        total_points = self._plotted_marker_count + len(data)
        RESOLUTION = max(1, total_points // MAX_PLOT_POINTS)

        spots = []
        new_line_coords = []

        for i, datum in enumerate(data):
            global_index = self._plotted_marker_count + i
            if global_index % RESOLUTION != 0 and global_index != total_points - 1:
                continue

            lat, lon = datum[2], datum[3]
            x, y = self.latlon_to_pixel(lat, lon)
            altitude = datum[1]

            spots.append({
                'pos': (x, y),
                'data': datum,
                'brush': getColor(altitude),
                'pen': pg.mkPen(None),
                'size': 10
            })
            new_line_coords.append((x, y))

        if spots:
            self.scatter.addPoints(spots)
            self._all_line_coords.extend(new_line_coords)

        if not hasattr(self, 'line_item') or self.line_item is None:
            self.line_item = pg.PlotDataItem(pen=pg.mkPen('r', width=2))
            self.plot_item.addItem(self.line_item)
            self.scatter.setZValue(2)
            self.line_item.setZValue(1)

        if self._all_line_coords:
            x_coords, y_coords = zip(*self._all_line_coords)
            self.line_item.setData(x=x_coords, y=y_coords)

        self._plotted_marker_count = total_points


    def update_arrow_sizes(self):
        x_range, _ = self.plot_item.viewRange()
        view_width = x_range[1] - x_range[0]
        scale_factor = view_width / 5  # Adjust this factor to control scaling sensitivity

        for arrow in self.arrows:
            arrow.setStyle(headLen=15 / scale_factor, tailLen=1, headWidth=10 / scale_factor,
                           tailWidth=1 / scale_factor)

    def update_color_grading(self):
        print("Updating color grading with", len(self.get_visible_nodes()), "points")
        nodes = self.get_visible_nodes()
        if not nodes:
            return

        altitudes = [node.data()[1] for node in nodes]
        min_altitude = min(altitudes)
        max_altitude = max(altitudes)

        for node in nodes:
            altitude = node.data()[1]
            color = getColor(altitude, min_altitude, max_altitude)
            node.setBrush(pg.mkBrush(*color, 255))

    def get_visible_nodes(self):
        if (self.scatter is None):
            return []
        x_range, y_range = self.plot_item.viewRange()
        visible_nodes = [point for point in self.scatter.points() if
                         x_range[0] <= point.pos()[0] <= x_range[1] and y_range[0] <= point.pos()[1] <= y_range[1]]
        return visible_nodes

    def latlong2decimal(filtered_gpgga):
        for datum in filtered_gpgga:
            datum[1] = np.round(datum[1] / 100, 6)
            datum[3] = np.round(datum[3] / 100, 6)
        return filtered_gpgga

    def latlon_to_pixel(self, lat, lon):
        # map lon/lat to pixel indices in source grid
        col, row = ~self.transform * (lon, lat)

        # mirror the X mapping used in update_x_axis (lon = c + (W - x) * a)
        W = self.raw_image_data.shape[0]
        x = W - col

        # Y ticks use lat = f + e * y, so keep y as the row index
        y = row

        return x, y
