# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scene_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import os

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_scene_widget(object):
    def setupUi(self, scene_widget):
        scene_widget.setObjectName("scene_widget")
        scene_widget.resize(902, 181)
        self.preset_tabs = QtWidgets.QTabWidget(scene_widget)
        self.preset_tabs.setGeometry(QtCore.QRect(111, -2, 791, 200))
        self.preset_tabs.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.preset_tabs.setObjectName("preset_tabs")
        self.scene_frame = QtWidgets.QFrame(scene_widget)
        self.scene_frame.setGeometry(QtCore.QRect(0, 0, 111, 181))
        self.scene_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.scene_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.scene_frame.setObjectName("scene_frame")
        self.mute_button = QtWidgets.QPushButton(self.scene_frame)
        self.mute_button.setGeometry(QtCore.QRect(0, 110, 40, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.mute_button.setFont(font)
        self.mute_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-no-audio-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mute_button.setIcon(icon)
        self.mute_button.setObjectName("mute_button")
        self.balance_label = QtWidgets.QLabel(self.scene_frame)
        self.balance_label.setGeometry(QtCore.QRect(50, 93, 61, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.balance_label.setFont(font)
        self.balance_label.setObjectName("balance_label")
        self.balance_pot = QtWidgets.QDial(self.scene_frame)
        self.balance_pot.setGeometry(QtCore.QRect(44, 41, 61, 61))
        self.balance_pot.setProperty("value", 0)
        self.balance_pot.setObjectName("balance_pot")
        self.scene_label = QtWidgets.QLabel(self.scene_frame)
        self.scene_label.setGeometry(QtCore.QRect(2, -1, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Cantarell Extra Bold")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.scene_label.setFont(font)
        self.scene_label.setObjectName("scene_label")
        self.volume_slide = QtWidgets.QSlider(self.scene_frame)
        self.volume_slide.setGeometry(QtCore.QRect(10, 33, 21, 71))
        self.volume_slide.setOrientation(QtCore.Qt.Vertical)
        self.volume_slide.setObjectName("volume_slide")
        self.horizontal_line = QtWidgets.QFrame(self.scene_frame)
        self.horizontal_line.setGeometry(QtCore.QRect(0, 18, 111, 20))
        self.horizontal_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontal_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontal_line.setObjectName("horizontal_line")
        self.vertical_line = QtWidgets.QFrame(self.scene_frame)
        self.vertical_line.setGeometry(QtCore.QRect(30, 27, 20, 104))
        self.vertical_line.setFrameShape(QtWidgets.QFrame.VLine)
        self.vertical_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_line.setObjectName("vertical_line")
        self.preset_list = QtWidgets.QComboBox(self.scene_frame)
        self.preset_list.setGeometry(QtCore.QRect(0, 160, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.preset_list.setFont(font)
        self.preset_list.setObjectName("preset_list")
        self.preset_list.addItem("")
        self.preset_list.addItem("")
        self.preset_list.addItem("")
        self.preset_list.addItem("")
        self.play_next_button = QtWidgets.QPushButton(self.scene_frame)
        self.play_next_button.setGeometry(QtCore.QRect(90, 160, 21, 21))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-end-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.play_next_button.setIcon(icon1)
        self.play_next_button.setObjectName("play_next_button")
        self.proxy_button = QtWidgets.QPushButton(self.scene_frame)
        self.proxy_button.setGeometry(QtCore.QRect(61, 110, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.proxy_button.setFont(font)
        self.proxy_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-proximity-sensor-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.proxy_button.setIcon(icon2)
        self.proxy_button.setObjectName("proxy_button")
        self.timed_button = QtWidgets.QPushButton(self.scene_frame)
        self.timed_button.setGeometry(QtCore.QRect(40, 110, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.timed_button.setFont(font)
        self.timed_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-sand-timer-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.timed_button.setIcon(icon3)
        self.timed_button.setObjectName("timed_button")
        self.settings_button = QtWidgets.QPushButton(self.scene_frame)
        self.settings_button.setGeometry(QtCore.QRect(90, 110, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.settings_button.setFont(font)
        self.settings_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-settings-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settings_button.setIcon(icon4)
        self.settings_button.setObjectName("settings_button")
        self.play_button = QtWidgets.QPushButton(self.scene_frame)
        self.play_button.setGeometry(QtCore.QRect(0, 130, 81, 31))
        self.play_button.setText("")
        icon5 = QtGui.QIcon()

        icon5.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-play-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.play_button.setIcon(icon5)
        self.play_button.setIconSize(QtCore.QSize(22, 22))
        self.play_button.setObjectName("play_button")
        self.expand_button = QtWidgets.QPushButton(self.scene_frame)
        self.expand_button.setGeometry(QtCore.QRect(80, 130, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.expand_button.setFont(font)
        self.expand_button.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("src/bardbot/GUI/icons/icons8-adjustment-100.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.expand_button.setIcon(icon6)
        self.expand_button.setIconSize(QtCore.QSize(22, 22))
        self.expand_button.setObjectName("expand_button")
        self.mute_button.raise_()
        self.balance_label.raise_()
        self.balance_pot.raise_()
        self.scene_label.raise_()
        self.volume_slide.raise_()
        self.horizontal_line.raise_()
        self.preset_list.raise_()
        self.vertical_line.raise_()
        self.play_next_button.raise_()
        self.proxy_button.raise_()
        self.timed_button.raise_()
        self.settings_button.raise_()
        self.play_button.raise_()
        self.expand_button.raise_()
        self.actionNew_Preset = QtWidgets.QAction(scene_widget)
        self.actionNew_Preset.setObjectName("actionNew_Preset")

        self.retranslateUi(scene_widget)

        QtCore.QMetaObject.connectSlotsByName(scene_widget)

    def retranslateUi(self, scene_widget):
        _translate = QtCore.QCoreApplication.translate
        scene_widget.setWindowTitle(_translate("scene_widget", "Tavern"))
        # self.preset_tabs.setTabText(self.preset_tabs.indexOf(self.brawl_tab), _translate("scene_widget", "brawl"))
        # self.preset_tabs.setTabText(self.preset_tabs.indexOf(self.festive_tab), _translate("scene_widget", "festive"))
        # self.preset_tabs.setTabText(self.preset_tabs.indexOf(self.morning_tab), _translate("scene_widget", "morning"))
        self.balance_label.setText(_translate("scene_widget", "L               R"))
        self.scene_label.setText(_translate("scene_widget", "Tavern: Preset"))
        # self.preset_list.setItemText(0, _translate("scene_widget", "brawl"))
        # self.preset_list.setItemText(1, _translate("scene_widget", "morning"))
        # self.preset_list.setItemText(2, _translate("scene_widget", "night"))
        # self.preset_list.setItemText(3, _translate("scene_widget", "festive"))
        self.actionNew_Preset.setText(_translate("scene_widget", "New Preset"))
