import sys
import os
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTextEdit, QMessageBox, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt

def parse_csv_points(path, lat_col='latitude', lon_col='longitude', alt_col='altitude', time_col='time', time_format=None):
    """
    Reads CSV and returns list of dicts: {'lat':float,'lon':float,'alt':float,'time':ISO8601 str}
    time_format: optional str to pass to datetime.strptime if times are not already ISO-8601
    """
    points = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                lat = float(r[lat_col])
                lon = float(r[lon_col])
                alt = float(r.get(alt_col, 0))
                t_raw = r[time_col]
                if time_format:
                    dt = datetime.strptime(t_raw, time_format)
                    t_iso = dt.isoformat() + 'Z'  # assume UTC unless otherwise specified
                else:
                    # try to be forgiving: if already ISO-like, use as-is (ensure Z or offset)
                    t_iso = t_raw
                    # if no timezone and no 'Z', append 'Z' (assume UTC)
                    if 'Z' not in t_iso and '+' not in t_iso and '-' not in t_iso[10:]:
                        t_iso = t_iso + 'Z'
                points.append({'lat': lat, 'lon': lon, 'alt': alt, 'time': t_iso})
            except Exception as e:
                # skip malformed rows but could log
                print(f"Skipping row due to parse error: {e}")
    # sort by time in case CSV not ordered
    try:
        points.sort(key=lambda p: p['time'])
    except Exception:
        pass
    return points

def build_gx_track_kml(points, name='Trajectory', description='', model_href=None):
    """
    Build a KML string with a gx:Track containing the provided points.
    If model_href is provided, creates a Model placemark that uses gx:Track to move the model.
    """
    header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <name>{name}</name>
    <description>{desc}</description>
'''.format(name=name, desc=description)

    # Style for a line and icon
    style = '''
    <Style id="trajLine">
      <LineStyle>
        <width>3</width>
      </LineStyle>
    </Style>
    <Style id="pointStyle">
      <IconStyle>
        <scale>1.0</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/arrow.png</href></Icon>
      </IconStyle>
    </Style>
    
    <LookAt>
      <longitude>-75.6975</longitude>
      <latitude>45.4218</latitude>
      <altitude>1500</altitude>
      <heading>0</heading>
      <tilt>45</tilt>
      <range>2000</range> <!-- distance from track in meters -->
      <altitudeMode>absolute</altitudeMode>
    </LookAt>
'''

    track_start = '''
    <Placemark>
      <name>{name} - Track</name>
      <styleUrl>#trajLine</styleUrl>
      <gx:Track>
'''.format(name=name)

    # append when/time and coords
    when_lines = []
    coord_lines = []
    for p in points:
        # KML requires <when> time values and <gx:coord> lon lat alt
        when_lines.append('        <when>{}</when>\n'.format(p['time']))
        coord_lines.append('        <gx:coord>{} {} {}</gx:coord>\n'.format(p['lon'], p['lat'], p['alt']))

    track_mid = ''.join(when_lines) + ''.join(coord_lines)
    track_end = '      </gx:Track>\n    </Placemark>\n'

    model_block = ''
    if model_href:
        # Create a Model placemark that references the gx:Track (via gx:MultiTrack is one approach),
        # but simplest is to create a Placemark with Model and duplicate the gx:Track inside a gx:MultiTrack.
        model_block = '''
    <Placemark>
      <name>{name} - Model</name>
      <gx:MultiTrack>
        <gx:interpolate>1</gx:interpolate>
        <gx:Track>
{when_block}
{coord_block}
        </gx:Track>
      </gx:MultiTrack>
      <Model>
        <altitudeMode>absolute</altitudeMode>
        <Link>
          <href>{model_href}</href>
        </Link>
        <Location>
          <longitude>{lon0}</longitude>
          <latitude>{lat0}</latitude>
          <altitude>{alt0}</altitude>
        </Location>
      </Model>
    </Placemark>
'''.format(
    name=name,
    when_block=''.join(when_lines),
    coord_block=''.join(coord_lines),
    model_href=model_href,
    lon0=points[0]['lon'] if points else 0,
    lat0=points[0]['lat'] if points else 0,
    alt0=points[0]['alt'] if points else 0
)
    footer = '  </Document>\n</kml>\n'
    kml = header + style + track_start + track_mid + track_end + model_block + footer
    return kml

class KMLTrajectoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trajectory -> KML (Google Earth)")
        self.resize(800, 600)
        layout = QVBoxLayout()

        row = QHBoxLayout()
        self.csv_label = QLabel("CSV file: (lat,lon,alt,time)")
        row.addWidget(self.csv_label)
        self.load_btn = QPushButton("Load CSV")
        self.load_btn.clicked.connect(self.load_csv)
        row.addWidget(self.load_btn)
        layout.addLayout(row)

        mh_row = QHBoxLayout()
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Optional: public .dae/.kmz URL for 3D model (leave blank for just a track)")
        mh_row.addWidget(self.model_input)
        layout.addLayout(mh_row)

        btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("Preview KML")
        self.preview_btn.clicked.connect(self.preview_kml)
        btn_row.addWidget(self.preview_btn)

        self.save_btn = QPushButton("Save KML")
        self.save_btn.clicked.connect(self.save_kml)
        btn_row.addWidget(self.save_btn)

        layout.addLayout(btn_row)

        self.kml_text = QTextEdit()
        self.kml_text.setReadOnly(True)
        layout.addWidget(self.kml_text)

        self.setLayout(layout)

        self.points = []
        self.kml_string = ''

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        # You can change column names/time format here if your CSV uses different headings
        try:
            self.points = parse_csv_points(path, lat_col='latitude', lon_col='longitude', alt_col='altitude', time_col='time', time_format=None)
            if not self.points:
                QMessageBox.warning(self, "No points", "No valid points parsed from CSV. Check column names and formats.")
                return
            QMessageBox.information(self, "Loaded", f"Loaded {len(self.points)} points from:\n{path}")
            self.csv_label.setText(f"CSV: {os.path.basename(path)} ({len(self.points)} points)")
            # build KML immediately
            self.kml_string = build_gx_track_kml(self.points, name=os.path.basename(path), description="Generated by KMLTrajectoryWidget", model_href=self.model_input.text() or None)
            self.kml_text.setPlainText(self.kml_string)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV: {e}")

    def preview_kml(self):
        if not self.kml_string:
            QMessageBox.warning(self, "No KML", "Load CSV first.")
            return
        self.kml_text.setPlainText(self.kml_string)
        QMessageBox.information(self, "Preview", "KML preview shown. Save KML and open with Google Earth to visualize animation.")

    def save_kml(self):
        if not self.kml_string:
            QMessageBox.warning(self, "No KML", "Load CSV first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save KML", "trajectory.kml", "KML Files (*.kml);;All Files (*)")
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.kml_string)
            QMessageBox.information(self, "Saved", f"KML saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save KML: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = KMLTrajectoryWidget()
    w.show()
    sys.exit(app.exec_())