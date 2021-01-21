from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMainWindow

from bardbot.GUI.scene_widget import Ui_scene_widget
from bardbot.ui_forms.main_template import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)



class SceneView(QWidget, Ui_scene_widget):
    def __init__(self, scene=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        flags = QtCore.Qt.WindowFlags(
            QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setupUi(self)

        print(str(self.scene_frame.winId()))

        self.setStyleSheet("QFrame#scene_frame { background: default ;  border: 2px solid black; }")
        self.play_button.lower()
        self.mute_button.lower()
        self.show()

    pass

class ChannelView(QWidget):
    pass

class FileFinderView(QWidget):
    pass

class ConfigView(QWidget):
    pass


