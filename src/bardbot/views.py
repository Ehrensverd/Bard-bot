import os
from pprint import pprint

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QGridLayout, \
    QScrollArea, QLabel, QDial, QDesktopWidget, QApplication, QGraphicsOpacityEffect, QTabWidget, QSpinBox


from bardbot.ui.channel_template import Ui_ChannelWindow
from bardbot.ui.docked_channels_template import Ui_channel_dock_main
from bardbot.ui.docked_channels_template2 import Ui_channel_dock_main2
from bardbot.ui.main_template import Ui_MainWindow
from bardbot.ui.scene_template import Ui_SceneWindow
from bardbot.ui import scene_channel_resources

class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)





class SceneView(QWidget, Ui_SceneWindow):
    #parent interface
    play_pause = pyqtSignal(bool)
    mute_unmute = pyqtSignal(bool)
    # View ->
    volume_changed = pyqtSignal(int)
    balance_changed = pyqtSignal(int)
    add_channel = pyqtSignal()
    # -> View
    change_volume = pyqtSignal(int)
    animation_finished = pyqtSignal()
    scene_button_checked = pyqtSignal(bool)

    def __init__(self, scene_name="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        flags = QtCore.Qt.WindowFlags(
            QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowFlags(flags)
        self.setupUi(self)

        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.scene_frame.setStyleSheet('background-color: palette(window)')
        self._height = 181
        self.setFixedHeight(self._height)
        self.setup_tab_area()

        self.scene_button.setText(scene_name)
        self.setup_buttons()

        self.center()
        self.scene_frame.raise_()
        self.show()

    def test(self):
        print("duble trouble")

    def setup_tab_area(self):
        self.preset_tab = PresetTabs(parent=None)


        self.preset_tab.raise_()
        vbox = QVBoxLayout()
        vbox.addWidget(self.preset_tab)

        self.channel_dock = ChannelDock(self.preset_tab)
        inner_vbox = QVBoxLayout()
        page = QWidget()
        inner_vbox.addWidget(self.channel_dock)
        page.setLayout(inner_vbox)

        self.preset_tab.addTab(self.channel_dock, "Eerie")
        self.preset_tab.show()

        # Channel dock

        self.channel_dock.show()
        self.channel_dock.new_channel_dock()
        #
        self.channel_dock.new_channel_dock()
        self.channel_dock.new_channel_dock()
        self.channel_dock.new_channel_dock()

        self.channel_dock.new_channel_dock()
        self.channel_dock.new_channel_dock()
        self.channel_dock.new_channel_dock()
        self.channel_dock.new_channel_dock()

        self.channel_dock.new_channel_dock()
        self.channel_dock.new_channel_dock()

    def mouse_in_tab_area(self):

        if inside_rectangle(self.preset_tab.frameGeometry().topLeft(), self.frameGeometry().bottomRight(), QCursor.pos()):
            self.preset_tab.show()
        else:
            self.preset_tab.show()


    def setup_buttons(self):

        # Type
        # Icons
        # Misc
        # Parent interface
        # Self
        # Children
        # Balance
        self.balance_pot.setRange(-100, 100)
        self.balance_pot.mouseReleaseEvent = lambda event: self.balance_pot.setValue(0) if (
                    event.button() == QtCore.Qt.RightButton) else None

        self.balance_pot.valueChanged.connect(self.balance_changed)


        #Volume
        self.volume_slide.setRange(0, 100)
        self.volume_slide.valueChanged.connect(self.volume_changed)

        #self.volume_changed.connect(mute_slide_toggle(self.mute_button))
        self.change_volume.connect(self.volume_slide.setValue)
        # Mute
        unmuted = QIcon(QPixmap(":/icons/unmute.png"))
        muted = QIcon(QPixmap(":/icons/mute.png"))
        self.mute_button.setIcon(unmuted)

        self.mute_button.clicked.connect(self.mute_unmute)
        self.change_mute_icons = toggle_button_slot(self.mute_button, muted, unmuted)
        self.mute_unmute.connect(toggle_button_slot(self.mute_button, muted, unmuted))
        # Play
        play = QIcon(QPixmap(":/icons/play.png"))
        pause = QIcon(QPixmap(":/icons/pause.png"))
        self.play_button.setIcon(play)

        self.play_button.clicked.connect(self.play_pause)

        self.play_pause.connect(toggle_button_slot(self.play_button, play, pause))

        # Expand Animation - Scene button
        self.scene_button.clicked.connect(self.scene_button_checked)

        #self.animation_view.animation_finished.connect(self.animation_finished)  # Proxy

        #self.scene_button.clicked.connect(self.animation_view.start_animation)

        # Add Channel
        self.add_channel_button.setIcon(QIcon(QPixmap(":/icons/add_channel.png")))
        self.add_channel_button.clicked.connect(self.add_channel)

        # TODO
        self.timed_button.setIcon(QIcon(QPixmap(":/icons/timed.png")))
        self.next_preset_button.setIcon(QIcon(QPixmap(":/icons/next_preset.png")))


    def center(self):
        qr = self.frameGeometry()

        print("QR",qr)
        desktop_widget = QApplication.desktop()
        second_monitor = desktop_widget.screenGeometry(1)
        cp = second_monitor.center()
        tab_geometry = self.preset_tab.frameGeometry()

        qr.moveCenter(cp)
        tab_geometry.moveCenter(qr.topRight())

        print("QR", qr)
        print(self.pos())
        print(cp)
        self.oldPos = cp
        self.move(qr.center().x(), second_monitor.bottomLeft().y()-self.height())
        self.preset_tab.move(self.frameGeometry().topRight().x()-3,  second_monitor.bottomLeft().y()- self.preset_tab.height()-5)
        self.tab_static_delta = self.frameGeometry().topLeft() - self.preset_tab.frameGeometry().topLeft()
        print(self.tab_static_delta)


    def mousePressEvent(self, event):
        print(self.oldPos)
        modifierPressed = QApplication.keyboardModifiers()
        if event.buttons () == QtCore.Qt.LeftButton: # and (modifierPressed & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier:

            self.oldPos = event.globalPos()
            print(self.oldPos)

    def mouseMoveEvent(self, event):
        top_left = self.preset_tab.frameGeometry().topLeft()
        bottom_right = self.frameGeometry().bottomRight()
        mouse_position = event.globalPos()
        if inside_rectangle(top_left, bottom_right, mouse_position):
            self.preset_tab.show()
        else:
            self.preset_tab.show()

        modifierPressed = QApplication.keyboardModifiers()
        if event.buttons() == QtCore.Qt.LeftButton: #  and (modifierPressed & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier:
            delta = QPoint(event.globalPos() - self.oldPos)

            self.move(self.x() + delta.x(), self.y() + delta.y() )
            self.preset_tab.move( self.frameGeometry().topLeft().x() -self.tab_static_delta.x() , self.frameGeometry().topLeft().y() - self.tab_static_delta.y())
            self.oldPos = event.globalPos()


def mute_slide_toggle(mute_button):
    def generic_slot(value):
        if value == 0 and not mute_button.isChecked():
            mute_button.setChecked(True)
        elif value > 0 and mute_button.isChecked():
            mute_button.setChecked(False)

    return generic_slot


def toggle_button_slot(button, checked_icon, unchecked_icon):
    def generic_slot(checked):
        if checked:
            button.setIcon(checked_icon)
        else:
            button.setIcon(unchecked_icon)
    return generic_slot


def inside_rectangle(a, b, c):
    answer = a.x() < c.x() < b.x() and a.y() < c.y() < b.y()
    print("anseer",  answer)
    return answer


def compare(a, b):
    return (a > b) - (a < b)


class ChannelView(QWidget, Ui_ChannelWindow):
    # Parent interface
    play_pause = pyqtSignal(bool)
    mute_unmute = pyqtSignal(bool)
    # View ->
    volume_changed = pyqtSignal(int)
    balance_changed = pyqtSignal(int)
    change_volume = pyqtSignal(int)

    def __init__(self,  parent=None, *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.setupUi(self)
        self.setFixedWidth(87)
        self.setFixedHeight(135)
        self.setup_buttons()
        self.show()

    def setup_buttons(self):
        # Type
        # Icons
        # Misc
        # Parent interface
        # Self
        # Children
        # Balance
        self.balance_pot.setRange(-100, 100)
        self.balance_pot.mouseReleaseEvent = lambda event: self.balance_pot.setValue(0) if (
                event.button() == QtCore.Qt.RightButton) else None

        self.balance_pot.valueChanged.connect(self.balance_changed)

        # Volume
        self.volume_slide.setRange(0, 100)
        self.volume_slide.valueChanged.connect(self.volume_changed)

        # self.volume_changed.connect(mute_slide_toggle(self.mute_button))
        self.change_volume.connect(self.volume_slide.setValue)
        # Mute
        unmuted = QIcon(QPixmap(":/icons/unmute.png"))
        muted = QIcon(QPixmap(":/icons/mute.png"))
        self.mute_button.setIcon(unmuted)

        self.mute_button.clicked.connect(self.mute_unmute)
        self.change_mute_icons = toggle_button_slot(self.mute_button, muted, unmuted)
        self.mute_unmute.connect(toggle_button_slot(self.mute_button, muted, unmuted))
        # Play
        play = QIcon(QPixmap(":/icons/play.png"))
        pause = QIcon(QPixmap(":/icons/pause.png"))
        self.play_button.setIcon(play)

        self.play_button.clicked.connect(self.play_pause)

        self.play_pause.connect(toggle_button_slot(self.play_button, play, pause))
        lute = QIcon(QPixmap(":/icons/lute.png"))
        self.trigger_button.setIcon(lute)

        crossfade = QIcon(QPixmap(":/icons/crossfade.png"))
        self.pushButton.setIcon(crossfade)
        infinite = QIcon(QPixmap(":/icons/infinite.png"))
        self.pushButton.setIcon(crossfade)
        self.channel_mode_box.setItemIcon(4 ,  infinite)


class FileFinderView(QWidget):
    pass

class ConfigView(QWidget):
    pass

class ChannelExpander(QWidget):
    animation_finished = pyqtSignal()
    animation_trigger = pyqtSignal(bool)
    def __init__(self, height, parent=None, animation_duration=502):
        super().__init__(parent=parent)

        self.animation_duration = animation_duration
        self.animation_area = QScrollArea() #Base for animation
        self.animation = QtCore.QPropertyAnimation(self.animation_area, b"maximumWidth")
        #self.animation_area.move(-3,-3)
        # initial state
        self.animation_area.setMaximumWidth(0)
        self.animation_area.setMinimumWidth(0)
        self.animation_area.setFixedHeight(height+1)

        # GridLayout needed for animation
        self.base_layout = QGridLayout()
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.addWidget(self.animation_area, 0, 0, 0, 2, QtCore.Qt.AlignTop)
        super().setLayout(self.base_layout)

        # signals
        self.animation.finished.connect(self.finished)
        self.animation_trigger.connect(self.start_animation)

    @pyqtSlot()
    def finished(self):
        self.animation_finished.emit()

    def start_animation(self, checked):
        direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
        #self.animation.setStartValue(0)
        self.animation.setDirection(direction)
        self.animation.start()

    def setLayout(self, outer_tab_layout, width):
        self.animation_area.destroy()
        self.animation_area.setLayout(outer_tab_layout)

        self.animation.setDuration(self.animation_duration)
        self.animation.setStartValue(0)
        self.animation.setEndValue(width)

class PresetTabs(QTabWidget):
    def __init__(self, parent=None, width=0, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        flags = QtCore.Qt.WindowFlags(
            QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.setStyleSheet("QTabBar::tab {height: 21px;  font-size:8pt;}"
                           "QDockWidget::title {text-align: left; border: 1px solid grey; padding-left: 5px;}")
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMaximumWidth(0)
        self.setFixedHeight(165)
class ChannelDock(QMainWindow, Ui_channel_dock_main):
    adjusted = pyqtSignal()

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.channel_docks = []
        self.setupUi(self)
        self.setCorner(QtCore.Qt.TopRightCorner, QtCore.Qt.TopDockWidgetArea)
        corner = self.corner(QtCore.Qt.TopRightCorner)
        self.setMaximumWidth(1500)

        self.adjusted.connect(self.repaint)
        self.show()

    def new_channel_dock(self):
        template_dock = QtWidgets.QDockWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(template_dock.sizePolicy().hasHeightForWidth())
        template_dock.setSizePolicy(sizePolicy)


        template_dock.setMinimumSize(QtCore.QSize(87, 155))
        template_dock.setMaximumSize(QtCore.QSize(87, 155))
        font = QtGui.QFont()
        font.setFamily("Cantarell")
        font.setPointSize(9)
        template_dock.setFont(font)
        template_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        template_dock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)


        dockWidgetContents = ChannelView(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dockWidgetContents.sizePolicy().hasHeightForWidth())
        dockWidgetContents.setSizePolicy(sizePolicy)
        dockWidgetContents.setMinimumSize(QtCore.QSize(87, 155))
        dockWidgetContents.setMaximumSize(QtCore.QSize(87, 155))
        dockWidgetContents.setObjectName("dockWidgetContents")

        template_dock.setWindowTitle("Channel name")
        temp = template_dock.titleBarWidget()
        print(temp)

        print(type(temp))

        #template_dock.barsetStyleSheet("Qborder: 2px solid lightgrey;")
        template_dock.setWidget(dockWidgetContents)
        #dockWidgetContents.mouseMoveEvent = lambda event: print("clicked")
        template_dock.dockLocationChanged.connect(self.adjusted)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, template_dock)
        self.channel_docks.append(template_dock)
        return template_dock

