from token import STRING
from tokenize import String

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
import sys
from GeoTiffViewer import *
import math
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QKeySequence, QIcon, QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QAction, QLabel, QShortcut, QPushButton
import GLWidget
import serial
import re
from datetime import datetime

from PyQt5.QtWidgets import QShortcut, QPushButton, QHBoxLayout
from RecoveryViewClass import *
from LiveViewClass import *
from CameraViewClass import *
from RadioViewClass import *
from ResearchViewClass import *
from SerialManagerMain import *
from Title import *
from DataModelMain import *
from SerialManagerBackup import *
from DataModelBackup import *

from screeninfo import get_monitors


BaudRate = 9600
alt = 0
time = 0


monitor = get_monitors()[0]  # Primary monitor
SCREEN_WIDTH = monitor.width
SCREEN_HEIGHT = monitor.height





geotiff_path = "maps/tim.tif"

global initial_volt_check, initial_volt

class loading_video(QWidget):
    def __init__(self, main_window_class):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.main_window_class = main_window_class

        self.video_widget = QVideoWidget(self)
        self.video_widget.setGeometry(0, 0, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)
        self.video_widget.raise_()
        self.video_widget.show()

        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_widget)
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("bg/OTSR Logo Animation_1.avi")))



        self.player.play()
        self.player.mediaStatusChanged.connect(self.showMain)

        

    def showMain(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.stop()
            self.player.deleteLater()
            self.video_widget.deleteLater()

            self.main_window_class = self.main_window_class(geotiff_path)
            self.main_window_class.show()
            self.close()

class MainWindow(QMainWindow):
    def __init__(self, geotiff_path, coordinate_data=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint) #removes title bar
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.showMaximized()
        self.cursor = 0
        self.setStyleSheet("""QMainWindow {
                           background-color: #1E1E24 ;
                           }
                           QPushButton {
                           background: transparent;
                           }
                           """)

        QShortcut(QKeySequence("esc"), self, self.close)
        QShortcut(QKeySequence("Ctrl+M"), self, self.showMinimized)

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.current_view = None

        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bg_label.setParent(self.central_widget)
        self.bg_label.lower()

        movie = QMovie("bg/Space_bg.gif")
        movie.setScaledSize(QSize(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_label.setMovie(movie)
        movie.start()

        self.serial_manager_main = SerialManagerMain("", 0)
        self.thread_main = QThread()
        self.serial_manager_main.moveToThread(self.thread_main)
        self.thread_main.started.connect(self.serial_manager_main.run)


        self.data_model_main = DataModelMain()
        self.serial_manager_main.data_received.connect(self.data_model_main.update_data)

        self.serial_manager_backup = SerialManagerBackup("", 0)
        self.thread_backup = QThread()
        self.serial_manager_backup.moveToThread(self.thread_backup)
        self.thread_backup.started.connect(self.serial_manager_backup.run)

        self.data_model_backup = DataModelBackup()
        self.serial_manager_backup.data_received.connect(self.data_model_backup.update_data)


        self.title = FLARE(self)
        self.title.setParent(self.central_widget)

        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #2A2A2F; color: white;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)

        Live_Display = QPushButton("")
        Recovery_Display = QPushButton("")
        Research_Display = QPushButton("")
        Radio_Display = QPushButton("")
        Camera_Display = QPushButton("")
        Runback_Display = QPushButton("")

        Blank1 = QPushButton("")


        for btn in [Live_Display, Recovery_Display, Research_Display, Radio_Display, Camera_Display, Runback_Display]:
            btn.setFixedHeight(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60)
            btn.setStyleSheet("""
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


        Live_Display.setIcon(QIcon("btn_icons/live.png"))
        Live_Display.setIconSize(QSize(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60, SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60))
        Recovery_Display.setIcon(QIcon("btn_icons/recovery.png"))
        Recovery_Display.setIconSize(QSize(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60, SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60))
        Research_Display.setIcon(QIcon("btn_icons/research.png"))
        Research_Display.setIconSize(QSize(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60, SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60))
        Radio_Display.setIcon(QIcon("btn_icons/radio.png"))
        Radio_Display.setIconSize(QSize(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60, SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60))
        Camera_Display.setIconSize(QSize(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60, SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60))
        Camera_Display.setIcon(QIcon("btn_icons/camera.png"))
        Runback_Display.setIconSize(QSize(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60, SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60))
        Runback_Display.setIcon(QIcon("btn_icons/runback.png"))



        top_layout.addWidget(Live_Display)
        top_layout.addWidget(Recovery_Display)
        top_layout.addWidget(Research_Display)
        top_layout.addWidget(Radio_Display)
        top_layout.addWidget(Camera_Display)
        top_layout.addWidget(Runback_Display)


        Blank1.setFixedHeight(SCREEN_HEIGHT // 12 - SCREEN_HEIGHT // 60)
        top_layout.addWidget(Blank1)


        Live_Display.clicked.connect(self.live_view)
        Recovery_Display.clicked.connect(self.recovery_view)
        Research_Display.clicked.connect(self.research_view)
        Radio_Display.clicked.connect(self.radio_view)
        Camera_Display.clicked.connect(self.camera_view)
        #Runback_Display.clicked.connect(self.runback_view)

        self.current_view = None

        self.top_bar = top_bar
        self.top_bar.setParent(self.central_widget)

        self.top_bar.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 12)

        self.title.setGeometry(SCREEN_WIDTH // 8,SCREEN_HEIGHT // 5,SCREEN_WIDTH, SCREEN_HEIGHT)

    def live_view(self):
        self.switch_view(LiveView(self.data_model_main, self.data_model_backup, geotiff_path, SCREEN_WIDTH, SCREEN_HEIGHT))

    def recovery_view(self):
        self.switch_view(RecoveryView(self.data_model_main, self.data_model_backup, geotiff_path, SCREEN_WIDTH, SCREEN_HEIGHT))

    def research_view(self):
        self.switch_view(ResearchView(self.data_model_main, SCREEN_WIDTH, SCREEN_HEIGHT))

    def radio_view(self):
        self.switch_view(RadioView(self.serial_manager_main, self.data_model_main, self.thread_main, self.serial_manager_backup, self.data_model_backup, self.thread_backup, SCREEN_WIDTH, SCREEN_HEIGHT))

    def camera_view(self):
        self.switch_view(CameraView(SCREEN_WIDTH, SCREEN_HEIGHT))

    #def runback_view(self(RunbackView(SCREEN_WIDTH,SCREEN_HEIGHT)):

    def switch_view(self, new_widget):

        try:
            if hasattr(self, 'current_view') and self.current_view is not None:
                self.current_view.setParent(None)
                self.current_view.deleteLater()

            self.current_view = new_widget
            self.current_view.setParent(self.central_widget)
            # Place the new view below the top bar and keep it within the window
            view_height = self.central_widget.height() - 200
            self.current_view.setGeometry(0, 200, self.central_widget.width(), view_height)
            self.current_view.show()
            self.bg_label.deleteLater()
            self.title.deleteLater()

        except Exception as e:
            print(f"[switch_view error] {e}")
    def closeEvent(self, event):
        self.serial_manager_main.stop()
        event.accept()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    loading = loading_video(MainWindow)
    loading.show()
    loading.showMain(QMediaPlayer.EndOfMedia)
    sys.exit(app.exec_())

