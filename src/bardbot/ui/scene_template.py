# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scene_template.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SceneWindow(object):
    def setupUi(self, SceneWindow):
        SceneWindow.setObjectName("SceneWindow")
        SceneWindow.resize(112, 182)
        self.scene_frame = QtWidgets.QFrame(SceneWindow)
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
        icon.addPixmap(QtGui.QPixmap("../ui_forms/icons/icons8-audio-90.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mute_button.setIcon(icon)
        self.mute_button.setCheckable(True)
        self.mute_button.setObjectName("mute_button")
        self.balance_label = QtWidgets.QLabel(self.scene_frame)
        self.balance_label.setGeometry(QtCore.QRect(50, 93, 61, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.balance_label.setFont(font)
        self.balance_label.setObjectName("balance_label")
        self.balance_pot = QtWidgets.QDial(self.scene_frame)
        self.balance_pot.setGeometry(QtCore.QRect(44, 41, 61, 61))
        self.balance_pot.setMinimum(-100)
        self.balance_pot.setMaximum(100)
        self.balance_pot.setProperty("value", 50)
        self.balance_pot.setObjectName("balance_pot")
        self.volume_slide = QtWidgets.QSlider(self.scene_frame)
        self.volume_slide.setGeometry(QtCore.QRect(10, 33, 21, 71))
        self.volume_slide.setMaximum(100)
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
        self.preset_list.setCurrentText("")
        self.preset_list.setObjectName("preset_list")
        self.next_preset_button = QtWidgets.QPushButton(self.scene_frame)
        self.next_preset_button.setGeometry(QtCore.QRect(90, 160, 21, 21))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../GUI/icons/icons8-end-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.next_preset_button.setIcon(icon1)
        self.next_preset_button.setObjectName("next_preset_button")
        self.timed_button = QtWidgets.QPushButton(self.scene_frame)
        self.timed_button.setGeometry(QtCore.QRect(39, 110, 36, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.timed_button.setFont(font)
        self.timed_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../GUI/icons/icons8-sand-timer-30.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.timed_button.setIcon(icon2)
        self.timed_button.setObjectName("timed_button")
        self.add_channel_button = QtWidgets.QPushButton(self.scene_frame)
        self.add_channel_button.setGeometry(QtCore.QRect(74, 110, 36, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.add_channel_button.setFont(font)
        self.add_channel_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/icons8-add-song-90.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_channel_button.setIcon(icon3)
        self.add_channel_button.setObjectName("add_channel_button")
        self.play_button = QtWidgets.QPushButton(self.scene_frame)
        self.play_button.setGeometry(QtCore.QRect(0, 130, 111, 31))
        self.play_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("../ui_forms/icons/icons8-play-90.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon4.addPixmap(QtGui.QPixmap("../ui_forms/icons/icons8-pause-90.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.play_button.setIcon(icon4)
        self.play_button.setIconSize(QtCore.QSize(22, 22))
        self.play_button.setCheckable(True)
        self.play_button.setObjectName("play_button")
        self.scene_button = QtWidgets.QToolButton(self.scene_frame)
        self.scene_button.setGeometry(QtCore.QRect(0, 0, 111, 28))
        font = QtGui.QFont()
        font.setFamily("Cantarell Extra Bold")
        font.setPointSize(12)
        font.setStrikeOut(False)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.scene_button.setFont(font)
        self.scene_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.scene_button.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.scene_button.setIconSize(QtCore.QSize(22, 22))
        self.scene_button.setCheckable(True)
        self.scene_button.setChecked(False)
        self.scene_button.setObjectName("scene_button")
        self.mute_button.raise_()
        self.balance_label.raise_()
        self.balance_pot.raise_()
        self.volume_slide.raise_()
        self.horizontal_line.raise_()
        self.preset_list.raise_()
        self.vertical_line.raise_()
        self.next_preset_button.raise_()
        self.timed_button.raise_()
        self.add_channel_button.raise_()
        self.play_button.raise_()
        self.scene_button.raise_()
        self.actionNew_Preset = QtWidgets.QAction(SceneWindow)
        self.actionNew_Preset.setObjectName("actionNew_Preset")

        self.retranslateUi(SceneWindow)
        self.mute_button.toggled['bool'].connect(self.mute_button.showNormal)
        QtCore.QMetaObject.connectSlotsByName(SceneWindow)

    def retranslateUi(self, SceneWindow):
        _translate = QtCore.QCoreApplication.translate
        SceneWindow.setWindowTitle(_translate("SceneWindow", "Tavern"))
        self.balance_label.setText(_translate("SceneWindow", "L               R"))
        self.scene_button.setText(_translate("SceneWindow", "Scene name"))
        self.actionNew_Preset.setText(_translate("SceneWindow", "New Preset"))
