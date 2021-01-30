import os

import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QDialog, QDialogButtonBox, QFileDialog, QAbstractButton, QApplication, QSizePolicy, QWidget
from validator_collection import checkers

import bardbot.ui.scene_channel_resources

from bardbot.ui.add_channel_template import Ui_AddChannelDialog
from bardbot.ui.channel_template import Ui_ChannelWindow
from bardbot.ui.docked_channels_template import Ui_channel_dock_main
from bardbot.ui.main_template import Ui_MainWindow
from bardbot.ui.scene_template import Ui_SceneWindow

keep = bardbot.ui.scene_channel_resources

class MainView(QMainWindow, Ui_MainWindow):
    discord_playback = pyqtSignal(bool)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.discord_switch = Switch(self)

        self.playback_layout.addWidget(self.discord_switch)
        self.discord_switch.setDisabled(True)
        self.discord_switch.toggled.connect(self.discord_playback)







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
        self.scene_button.setText(scene_name)
        self._height = 181
        self.setFixedHeight(self._height)
        self.setup_tab_area()
        self.setup_buttons()

        self.center()
        self.show()

    def setup_tab_area(self):
        self.preset_tab = PresetTabs(parent=None)
        self.channel_dock = ChannelDock(self.preset_tab)

        self.preset_tab.addTab(self.channel_dock, "Default")
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
        self.change_volume.connect(self.volume_slide.setValue)

        # Mute
        unmuted = QIcon(QPixmap(":/icons/unmute.png"))
        muted = QIcon(QPixmap(":/icons/mute.png"))
        self.mute_button.setIcon(unmuted)

        self.mute_button.clicked.connect(self.mute_unmute)
        self.change_mute_icons = toggle_button_slot(self.mute_button, muted, unmuted)
        self.mute_unmute.connect(self.change_mute_icons)

        # Play
        play = QIcon(QPixmap(":/icons/play.png"))
        pause = QIcon(QPixmap(":/icons/pause.png"))
        self.play_button.setIcon(play)

        self.play_button.clicked.connect(self.play_pause)
        self.play_pause.connect(toggle_button_slot(self.play_button, pause, play))

        # Expand Animation - Scene button
        self.scene_button.clicked.connect(self.scene_button_checked)

        # Add Channel
        self.add_channel_button.setIcon(QIcon(QPixmap(":/icons/add_channel.png")))
        self.add_channel_button.clicked.connect(self.add_channel)

        # TODO
        self.timed_button.setIcon(QIcon(QPixmap(":/icons/timed.png")))
        self.next_preset_button.setIcon(QIcon(QPixmap(":/icons/next_preset.png")))


    def center(self):
        qr = self.frameGeometry()

        desktop_widget = QApplication.desktop()
        second_monitor = desktop_widget.screenGeometry(1) # Change this for monitor
        cp = second_monitor.center()
        tab_geometry = self.preset_tab.frameGeometry()

        qr.moveCenter(cp)
        tab_geometry.moveCenter(qr.topRight())
        self.oldPos = cp
        self.move(qr.center().x(), second_monitor.bottomLeft().y()-self.height())
        self.preset_tab.move(self.frameGeometry().topRight().x()-3,  second_monitor.bottomLeft().y()- self.preset_tab.height()-5)
        self.tab_static_delta = self.frameGeometry().topLeft() - self.preset_tab.frameGeometry().topLeft()


    def mousePressEvent(self, event):
        #print(self.oldPos)
        modifierPressed = QApplication.keyboardModifiers()
        if event.buttons () == QtCore.Qt.LeftButton: # and (modifierPressed & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier:
            self.oldPos = event.globalPos()


    def mouseMoveEvent(self, event):
        modifierPressed = QApplication.keyboardModifiers()
        if event.buttons() == QtCore.Qt.LeftButton: #  and (modifierPressed & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y() )
            self.preset_tab.move( self.frameGeometry().topLeft().x() -self.tab_static_delta.x() , self.frameGeometry().topLeft().y() - self.tab_static_delta.y())
            self.oldPos = event.globalPos()


class ChannelView(QWidget, Ui_ChannelWindow):
    # Parent interface
    play_pause = pyqtSignal(bool)
    mute_unmute = pyqtSignal(bool)
    # View ->
    volume_changed = pyqtSignal(int)
    balance_changed = pyqtSignal(int)
    change_volume = pyqtSignal(int)

    triggered = pyqtSignal()
    crossfaded = pyqtSignal(bool)
    combo_changed = pyqtSignal(int)
    #

    def __init__(self,  parent=None, channel_name="channel", *args, **kwargs):
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
        self.change_volume.connect(self.volume_slide.setValue)

        # Mute
        unmuted = QIcon(QPixmap(":/icons/unmute.png"))
        muted = QIcon(QPixmap(":/icons/mute.png"))
        self.mute_button.setIcon(unmuted)

        self.mute_button.clicked.connect(self.mute_unmute)
        self.change_mute_icons = toggle_button_slot(self.mute_button, muted, unmuted)
        self.mute_unmute.connect(self.change_mute_icons)

        # Play
        play = QIcon(QPixmap(":/icons/play.png"))
        pause = QIcon(QPixmap(":/icons/pause.png"))
        self.play_button.setIcon(play)
        self.play_button.clicked.connect(self.play_pause)
        self.play_pause.connect(toggle_button_slot(self.play_button, pause, play))

        #Lute Trigger
        lute = QIcon(QPixmap(":/icons/lute.png"))
        self.trigger_button.setIcon(lute)

        #Crossfade
        crossfade = QIcon(QPixmap(":/icons/crossfade.png"))
        self.pushButton.setIcon(crossfade)

        #Misc Modes
        infinite = QIcon(QPixmap(":/icons/infinite.png"))
        self.pushButton.setIcon(crossfade)
        self.pushButton.clicked.connect(self.crossfaded)
        self.channel_mode_box.setItemIcon(4 ,  infinite)
        self.channel_mode_box.currentIndexChanged.connect(self.combo_changed)

# generic function generators for Scene and Channel
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

# FileViews
class AddChannelDialog(QDialog, Ui_AddChannelDialog):
    def __init__(self, scene_name="Scene", parent=None, *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.setupUi(self)
        self.scene_name = scene_name

        btn = self.open_box.button(QDialogButtonBox.Open)
        btn.clicked.connect(self.open_files)

        btn2 = self.buttons_box.button(QDialogButtonBox.Ok)
        btn2.setDisabled(True)

        self.accepted.connect(self.url_edited)
        self.rejected.connect(self.canceled)
        self.url_edit_line.textEdited.connect(self.url_edited)
        self.result = False

    def canceled(self):
        self.result = "canceled", "canceled"


#https://www.soundboard.com/handler/DownLoadTrack.ashx?cliptitle=Never+Gonna+Give+You+Up-+Original&filename=mz/Mzg1ODMxNTIzMzg1ODM3_JzthsfvUY24.MP3

    def check_url(self):
        url = self.url_edit_line.text()
        valid = checkers.is_url(url)
        if valid:
            try:
                response = requests.get(url)
                if "audio/mpeg" in response.headers["content-type"] or "application/octet-stream" in response.headers["content-type"]:
                    #print(url.rsplit(".", 1)[-1].lower())
                    if url.rsplit(".", 1)[-1].lower() == "mp3":
                        return True, "Valid mp3 url!"
                    else:
                        return False, "mp3 files only! \n- url must end with .mp3"
                else:
                    return False, "url needs to link to a mp3 file. \n- url must end with .mp3"
            except requests.ConnectionError as exception:
                return False, "url page does not exist"
        else:
            return False, "Invalid url!"

    def url_edited(self):
        valid, result = self.check_url()
        if valid:
            self.result = ("url", self.url_edit_line.text())
            self.buttons_box.button(QDialogButtonBox.Ok).setDisabled(False)
            self.error_label.setText(result)
        else:
            self.error_label.setText(result)
            self.result = False
            self.buttons_box.button(QDialogButtonBox.Ok).setDisabled(True)

    def open_files(self):
        self.hide()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons



        dirname = os.path.dirname(__file__)
        library_path = os.path.join(dirname, 'Audio Library/')
        files, _ = QFileDialog.getOpenFileNames(self, "Select mp3 file(s) to add to " + self.scene_name, library_path,
                                                "Audio mp3 files (*.mp3)", options=options)

        if files:
            self.result = "file_path", files
        else:
            self.result = False


class ConfigView(QWidget):
    pass



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
    adjust_animation = pyqtSignal()
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.channel_docks = []
        self.setupUi(self)
        self.setCorner(QtCore.Qt.TopRightCorner, QtCore.Qt.TopDockWidgetArea)
        corner = self.corner(QtCore.Qt.TopRightCorner)
        self.setMaximumWidth(1500)

        self.show()

    def new_channel_dock(self, channel_view, channel_name="channel_name"):
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


        dockWidgetContents = channel_view
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dockWidgetContents.sizePolicy().hasHeightForWidth())
        dockWidgetContents.setSizePolicy(sizePolicy)
        dockWidgetContents.setMinimumSize(QtCore.QSize(87, 155))
        dockWidgetContents.setMaximumSize(QtCore.QSize(87, 155))
        dockWidgetContents.setObjectName("dockWidgetContents")

        template_dock.setWindowTitle(channel_name)
        temp = template_dock.titleBarWidget()


        #template_dock.barsetStyleSheet("Qborder: 2px solid lightgrey;")
        template_dock.setWidget(dockWidgetContents)
        #dockWidgetContents.mouseMoveEvent = lambda event: print("clicked")

        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, template_dock)
        self.channel_docks.append(template_dock)
        return template_dock



class Switch(QAbstractButton):
    def __init__(self, parent=None, track_radius=10, thumb_radius=8):
        super().__init__(parent=parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._track_radius = track_radius
        self._thumb_radius = thumb_radius

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: self.width() - self._base_offset,
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset

        palette = self.palette()
        if self._thumb_radius > self._track_radius:
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._thumb_color = {
                True: palette.highlight(),
                False: palette.light(),
            }
            self._text_color = {
                True: palette.highlightedText().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '',
                False: '',
            }
            self._track_opacity = 0.5
        else:
            self._thumb_color = {
                True: palette.highlightedText(),
                False: palette.light(),
            }
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._text_color = {
                True: palette.highlight().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '',
                False: '',
            }
            self._track_opacity = 1

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def sizeHint(self):  # pylint: disable=invalid-name
        return QSize(
            4 * self._track_radius + 2 * self._margin,
            2 * self._track_radius + 2 * self._margin,
        )

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._end_offset[checked]()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.offset = self._end_offset[self.isChecked()]()

    def paintEvent(self, event):  # pylint: disable=invalid-name, unused-argument
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        track_opacity = self._track_opacity
        thumb_opacity = 1.0
        text_opacity = 1.0
        if self.isEnabled():
            track_brush = self._track_color[self.isChecked()]
            thumb_brush = self._thumb_color[self.isChecked()]
            text_color = self._text_color[self.isChecked()]
        else:
            track_opacity *= 0.8
            track_brush = self.palette().shadow()
            thumb_brush = self.palette().mid()
            text_color = self.palette().shadow().color()

        p.setBrush(track_brush)
        p.setOpacity(track_opacity)
        p.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin,
            self.height() - 2 * self._margin,
            self._track_radius,
            self._track_radius,
        )
        p.setBrush(thumb_brush)
        p.setOpacity(thumb_opacity)
        p.drawEllipse(
            self.offset - self._thumb_radius,
            self._base_offset - self._thumb_radius,
            2 * self._thumb_radius,
            2 * self._thumb_radius,
        )
        p.setPen(text_color)
        p.setOpacity(text_opacity)
        font = p.font()
        font.setPixelSize(1.5 * self._thumb_radius)
        p.setFont(font)
        p.drawText(
            QRectF(
                self.offset - self._thumb_radius,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            ),
            Qt.AlignCenter,
            self._thumb_text[self.isChecked()],
        )

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            anim = QPropertyAnimation(self, b'offset', self)
            anim.setDuration(120)
            anim.setStartValue(self.offset)
            anim.setEndValue(self._end_offset[self.isChecked()]())
            anim.start()

    def enterEvent(self, event):  # pylint: disable=invalid-name
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)



  # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.scene_frame.setStyleSheet('background-color: palette(window)')