from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QSequentialAnimationGroup
from PyQt5.QtGui import QFont, QFontDatabase
import sys
from functools import partial


class FLARE(QWidget):
    def __init__(self, *args, **kwargs):
        super(FLARE, self).__init__(*args, **kwargs)
        self.title = "F.L.A.R.E."

        font_id = QFontDatabase.addApplicationFont("super-mario-256/SuperMario256.ttf")
        if font_id == -1:
            print("Failed to load font!")
            custom_font = 'OCR A extended'
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            print("Loaded font families:", font_families)

            custom_font = QFont(font_families[0], 12)
            custom_font.setPointSize(128)
            custom_font.setWeight(QFont.Bold)

        x = 0
        x_offset = 100

        self.animations = []
        self.letter_labels = []

        for i, char in enumerate(self.title):
            label = QLabel(char, self)
            label.setFont(custom_font)
            label.setStyleSheet("color: #FFFFFF;")
            label.adjustSize()
            label.move(x, 500)

            opacity = QGraphicsOpacityEffect()
            label.setGraphicsEffect(opacity)
            opacity.setOpacity(0)

            opacity_anim = QPropertyAnimation(opacity, b"opacity")
            opacity_anim.setDuration(100)
            opacity_anim.setStartValue(0)
            opacity_anim.setEndValue(1)

            QTimer.singleShot(i * 500, partial(self.startAnimations, opacity_anim))
            x += x_offset + label.width()

            self.animations.extend([opacity_anim])
            self.letter_labels.append(label)

            """period = QLabel(".", self)
            period.setFont(QFont('OCR A extended', 128, QFont.Bold))
            period.setStyleSheet("color: #FFFFFF;")

            period.move(x, 0)

            period.opacity_effect = QGraphicsOpacityEffect()
            label.setGraphicsEffect(self.opacity_effect)
            period.opacity_effect.setOpacity(0)
            QTimer.singleShot(100, lambda: self.renderTitle(period, x))
            x += x_offset"""

    def startAnimations(self, opacity_anim):
        opacity_anim.start()
    def startOpacity(self, opacity_anim):
        opacity_anim.start()