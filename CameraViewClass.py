import sys
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout

class CameraView(QWidget):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super().__init__()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")


        self.image_label.setParent(self)
        self.start_button.setParent(self)
        self.stop_button.setParent(self)

        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        
        

        self.image_label.setGeometry(0, 0, 1920, 1080)

        self.bottom_bar = QWidget()
        self.bottom_bar.setStyleSheet("background-color: #2A2A2F; color: white;")
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(20, 0, 20, 0)
        self.bottom_bar.setParent(self)

        self.bottom_bar.setGeometry(0,SCREEN_HEIGHT - 700, SCREEN_WIDTH, 300)

        self.start_button.setFixedHeight(300)
        self.start_button.setStyleSheet("""
                        QPushButton {
                            background-color: #35353A;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                        }
                        QPushButton:hover {
                            background-color: #72A1EF;
                        }
                        QPushButton:pressed {
                            background-color: #222;
                            padding-top: 10px; 
                            padding-bottom: 6px;
                        }
                    """)

        self.stop_button.setFixedHeight(300)
        self.stop_button.setStyleSheet("""
                                QPushButton {
                                    background-color: #35353A;
                                    color: white;
                                    border: none;
                                    padding: 8px 16px;
                                }
                                QPushButton:hover {
                                    background-color: #72A1EF;
                                }
                                QPushButton:pressed {
                                    background-color: #222;
                                    padding-top: 10px;  /* simulate a press-down effect */
                                    padding-bottom: 6px;
                                }
                            """)

        bottom_layout.addWidget(self.start_button)
        bottom_layout.addWidget(self.stop_button)

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Could not open camera.")
            return
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.image_label.setPixmap(pixmap)
        else:
            print("Failed to grab frame")

    def stop_camera(self):
        self.timer.stop()
        if self.capture:
            self.capture.release()
        self.image_label.clear()

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
