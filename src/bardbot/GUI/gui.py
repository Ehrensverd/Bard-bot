from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit, QWidget, QLineEdit, \
    QInputDialog, QPushButton, QTabWidget, QBoxLayout, QVBoxLayout, QHBoxLayout
import sys

from bardbot.GUI.channel_widget import Ui_channel_widget

from bardbot.GUI.scene_widget import Ui_scene_widget
from bardbot.AudioMixer.scene import Scene


class SceneWindow(QWidget, Ui_scene_widget):
    def __init__(self, scene: Scene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = scene

        # Setup
        self.scene_ui_setup()
        self.setFixedWidth(111)
        self.setFixedHeight(181)
        # self.resize(92, self.height())
        self.preset_list.view().setDragDropMode(Qt.QAbstractItemView.DragOnly)
        button = QPushButton

        self.expand_button.clicked.connect(self.scene_expander)
        self.open = False
        self.show()

    def scene_ui_setup(self):
        self.setupUi(self)
        self.scene_label.setText(self.scene.scene_name + self.scene.active_preset["preset_name"])

    def scene_expander(self):
        print("click")
        if self.open:
            # self.resize(950, self.height())
            self.setFixedWidth(111)
            self.open = False
        else:
            self.setFixedWidth(904)
            # self.resize(92, self.height())
            self.open = True
        self.show()

    def populate_channels(self, channels):
        pass


class ChannelFrame(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_channel_widget()
        self.ui.setupUi(self)
        self.setFixedWidth(94)
        self.ui.channel_play.clicked.connect(self.channel_expander)
        self.show()

    def channel_expander(self):
        if self.width() == 94:
            self.setFixedWidth(950)
        else:
            self.setFixedWidth(94)


class MDIWindow(QMainWindow):
    count = 0

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # multi document interface area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        bar = self.menuBar()

        file = bar.addMenu("Scene")
        file.addAction("Import")
        file.addAction("Open")
        file.addAction("Tiled")
        file.triggered[QAction].connect(self.WindowTrig)
        self.setWindowTitle("MDI Application")

    def WindowTrig(self, p):

        if p.text() == "Import":
            text, ok = QInputDialog.getText(self, 'Text Input Dialog', "Import from url")

            if ok:
                print(text)
                mdi = MDIWindow()
                MDIWindow.count = MDIWindow.count + 1
                sub = QMdiSubWindow()
                play_button = QPushButton("P")

                # sub.setWindowTitle("Sub Window" + str(MDIWindow.count))
                # sub.setWindowFlags(sub.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint )

                # print(bin(sub.windowFlags()) + " " + bin(QtCore.Qt.MSWindowsFixedSizeDialogHint) + " " + bin(sub.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint))

                # sub.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
                # sub.setStyleSheet('background-color: grey; border: 3px solid black')

                sub.setFixedSize(200, 100)
                mdi.mdi_area.addSubWindow(sub)
                mdi.show()
                sub.show()

        if p.text() == "Open":
            scene_gui = Ui_scene_widget()
            self.scene_widget = QWidget()
            scene_gui.setupUi(self.scene_widget)
            self.scene_widget.show()

            layout = QHBoxLayout()
            scene_gui.brawl_tab.setLayout(layout)

            channel_1_gui = Ui_channel_widget()
            self.channel_widget_1 = QWidget()
            channel_1_gui.setupUi(self.channel_widget_1)
            # self.channel_widget_1.setMaximumWidth(94)
            self.channel_widget_1.setFixedWidth(94)
            layout.addWidget(self.channel_widget_1)
            self.channel_widget_1.show()

            channel_2_gui = Ui_channel_widget()
            self.channel_widget_2 = QWidget()
            channel_2_gui.setupUi(self.channel_widget_2)
            # self.channel_widget_2.setMaximumWidth(94)
            self.channel_widget_2.setFixedWidth(94)
            #
            layout.addWidget(self.channel_widget_2)
            self.channel_widget_2.show()
            layout.addStretch()

            # scene_widget.preset_tabs.addTab(self.channel_widget, "test")

        if p.text() == "Tiled":
            self.scene_1 = SceneWindow()

def init_ui(controller):

    app = QApplication(sys.argv)
    mdi = MDIWindow(controller)
    mdi.show()
    app.exec_()
