# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitled.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QSizePolicy,
    QWidget)

class Ui_N_image_downloader_and_image_transformer(object):
    def setupUi(self, N_image_downloader_and_image_transformer):
        if not N_image_downloader_and_image_transformer.objectName():
            N_image_downloader_and_image_transformer.setObjectName(u"N_image_downloader_and_image_transformer")
        N_image_downloader_and_image_transformer.resize(538, 292)
        self.progressBar = QProgressBar(N_image_downloader_and_image_transformer)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(10, 210, 511, 31))
        self.progressBar.setValue(0)
        self.url = QLabel(N_image_downloader_and_image_transformer)
        self.url.setObjectName(u"url")
        self.url.setGeometry(QRect(20, 30, 48, 16))
        self.url_input = QLineEdit(N_image_downloader_and_image_transformer)
        self.url_input.setObjectName(u"url_input")
        self.url_input.setGeometry(QRect(80, 30, 381, 22))
        self.save_path = QLabel(N_image_downloader_and_image_transformer)
        self.save_path.setObjectName(u"save_path")
        self.save_path.setGeometry(QRect(20, 70, 48, 16))
        self.dir_path = QLineEdit(N_image_downloader_and_image_transformer)
        self.dir_path.setObjectName(u"dir_path")
        self.dir_path.setGeometry(QRect(80, 70, 381, 22))
        self.load_dir = QPushButton(N_image_downloader_and_image_transformer)
        self.load_dir.setObjectName(u"load_dir")
        self.load_dir.setGeometry(QRect(460, 70, 75, 24))
        self.groupBox = QGroupBox(N_image_downloader_and_image_transformer)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 120, 505, 56))
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.is_random_size = QCheckBox(self.groupBox)
        self.is_random_size.setObjectName(u"is_random_size")
        self.is_random_size.setChecked(True)

        self.horizontalLayout.addWidget(self.is_random_size)

        self.is_random_angle = QCheckBox(self.groupBox)
        self.is_random_angle.setObjectName(u"is_random_angle")
        self.is_random_angle.setChecked(True)

        self.horizontalLayout.addWidget(self.is_random_angle)

        self.is_random_pixel = QCheckBox(self.groupBox)
        self.is_random_pixel.setObjectName(u"is_random_pixel")
        self.is_random_pixel.setChecked(True)

        self.horizontalLayout.addWidget(self.is_random_pixel)

        self.is_add_outline = QCheckBox(self.groupBox)
        self.is_add_outline.setObjectName(u"is_add_outline")
        self.is_add_outline.setChecked(True)

        self.horizontalLayout.addWidget(self.is_add_outline)

        self.buttonBox = QDialogButtonBox(N_image_downloader_and_image_transformer)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(320, 250, 211, 24))
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Close|QDialogButtonBox.StandardButton.Yes)
        self.simple_log = QLabel(N_image_downloader_and_image_transformer)
        self.simple_log.setObjectName(u"simple_log")
        self.simple_log.setGeometry(QRect(20, 245, 281, 31))

        self.retranslateUi(N_image_downloader_and_image_transformer)

        QMetaObject.connectSlotsByName(N_image_downloader_and_image_transformer)
    # setupUi

    def retranslateUi(self, N_image_downloader_and_image_transformer):
        N_image_downloader_and_image_transformer.setWindowTitle(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"Dialog", None))
        self.url.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"URL", None))
        self.save_path.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"\uc800\uc7a5\uacbd\ub85c", None))
        self.load_dir.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"...", None))
        self.groupBox.setTitle(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"\uc774\ubbf8\uc9c0 \ubcc0\ud615 \uc124\uc815", None))
        self.is_random_size.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"\ub79c\ub364\ube44\uc728\uc870\uc815(\u00b15%)", None))
        self.is_random_angle.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"\ub79c\ub364 \uae30\uc6b8\uae30 (\u00b13\u00ba)", None))
        self.is_random_pixel.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"\ub79c\ub364 \ud53d\uc140 (3~5\uac1c)", None))
        self.is_add_outline.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"\ud14c\ub450\ub9ac \ucd94\uac00", None))
        self.simple_log.setText(QCoreApplication.translate("N_image_downloader_and_image_transformer", u"TextLabel", None))
    # retranslateUi

