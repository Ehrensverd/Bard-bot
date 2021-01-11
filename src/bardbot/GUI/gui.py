import re
import time

from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit, QWidget, QLineEdit, \
    QInputDialog, QPushButton, QTabWidget, QBoxLayout, QVBoxLayout, QHBoxLayout, QScrollArea
import sys

from bardbot.GUI.channel_widget import Ui_channel_widget

from bardbot.GUI.scene_widget import Ui_scene_widget
from bardbot.AudioMixer.scene import Scene


class SceneWindow(QWidget, Ui_scene_widget):
    def __init__(self, scene=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = scene
        self.tabs = []


        # Setup
        self.scene_ui_setup()
        self.setup_ui_tab(self.scene.active_preset)
        self.setFixedWidth(111)
        self.setFixedHeight(220)

        # self.resize(92, self.height())
        self.preset_list.view().setDragDropMode(Qt.QAbstractItemView.DragDrop)


        self.open = False
        self.show()
        print("stop")
        print("stop")


    def scene_ui_setup(self):
        self.setupUi(self)
        self.scene_label.setText(self.scene.scene_name + self.scene.active_preset)

        # Icons
        self.pause_icon = QtGui.QIcon("src/bardbot/GUI/icons/icons8-pause-30.png")
        self.play_icon = QtGui.QIcon("src/bardbot/GUI/icons/icons8-play-30.png")

        # Buttons and Sliders
        self.expand_button.clicked.connect(self.scene_expander)
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.click_play_button)
        self.settings_button.clicked.connect(self.settings_button_clicked)
        self.volume_slide.setRange(0, 100)
        self.volume_slide.setValue(self.scene.scene_volume)
        self.volume_slide.valueChanged.connect(self.volume_slider_changed)

        self.balance_pot.setRange(-100, 100)
        self.balance_pot.setValue(self.scene.scene_balance)
        self.balance_pot.valueChanged.connect(self.balance_pot_changed)

        #Tabs And channels


    def settings_button_clicked(self):
        self.scene.low_pass = not self.scene.low_pass


    def setup_ui_tab(self, preset):
        preset_object_name = re.sub(r"\W+|^(?=\d)", "_", preset)
        # Make new preset tab
        outer_tab = QWidget()
        outer_tab.tab = QWidget()
        tab = outer_tab.tab

        tab.setObjectName(preset_object_name)

        # make Layout and scroll
        tab_layout = QHBoxLayout()
        #tab.setLayout(tab_layout)

        # Fetch Channels
        # call ChannelWidget(channel)  for in
        for name, channel in self.scene.channels.items():
            channel_widget = ChannelWindow(channel)
            tab_layout.addWidget(channel_widget)
            pass
        tab_layout.addStretch()
        tab.setLayout(tab_layout)
        # Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        # Scroll Area Layer add
        vLayout = QHBoxLayout(outer_tab)
        # vLayout.addWidget(self.settings_button)
        vLayout.addWidget(scroll)
        outer_tab.setLayout(vLayout)

        outer_tab.show()

        tab.show()

        # Put in tabs [] and add to preset tabs
        self.tabs.append(outer_tab)
        self.preset_tabs.addTab(outer_tab, preset)
        #tab_scroll_area = QScrollArea(tab)


    def add_new_channel(self, channel):
        # Needs to be fixed
        label = Qt.QLabel("new")
        layout = self.widget.layout()
        layout.insertWidget(layout.count() - 1, label)

    def balance_pot_changed(self, value):
        self.scene.scene_balance = value

    def volume_slider_changed(self, value):
        self.scene.scene_volume = value


    def click_play_button(self):
        self.scene.scene_playing = not self.scene.scene_playing
        if self.play_button.isChecked():
            self.play_button.setIcon(self.pause_icon)
        else:
            self.play_button.setIcon(self.play_icon)

    def scene_expander(self):
        print("click")
        if self.open:
            # self.resize(950, self.height())
            self.setFixedWidth(111)
            self.open = False
        else:
            self.setFixedWidth(944)
            # self.resize(92, self.height())
            self.open = True
        self.show()

    def populate_channels(self, channels):
        pass


class ChannelWindow(QWidget, Ui_channel_widget):
    def __init__(self, channel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel

        # Setup
        self.channel_ui_setup()
        self.setFixedWidth(94)


        self.show()

    def channel_ui_setup(self):
        self.setupUi(self)
        # Buttons
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.click_play_button)
        # Icons
        self.pause_icon = QtGui.QIcon("src/bardbot/GUI/icons/icons8-pause-30.png")
        self.play_icon = QtGui.QIcon("src/bardbot/GUI/icons/icons8-play-30.png")


        # Label
        print("Gui Channel:", self.channel.name)
        self.channel_label.setText(self.channel.name)
        print("Gui Channel label:", self.channel_label.text())
        # Buttons


        # Volume
        self.volume_slide.setRange(0, 100)
        self.volume_slide.setValue(self.channel.volume)
        self.volume_slide.valueChanged.connect(self.volume_slider_changed)
        # Balance
        self.balance_pot.setValue(self.channel.balance)
        self.balance_pot.setRange(-100, 100)
        self.balance_pot.valueChanged.connect(self.balance_pot_changed)

    # Events
    def volume_slider_changed(self, value):
        self.channel.volume = value

    def balance_pot_changed(self, value):

        self.channel.balance = value


    def click_play_button(self):
        if self.channel.is_random:
            self.channel.is_triggered = True

        self.channel.is_playing = not self.channel.is_playing
        if self.play_button.isChecked():
            self.play_button.setIcon(self.pause_icon)
        else:
            self.play_button.setIcon(self.play_icon)

    def channel_expander(self):
        if self.width() == 94:
            self.setFixedWidth(950)
        else:
            self.setFixedWidth(94)


class External(QThread):
    """
    Runs a observer thread.
    for updating GUI elements, when the machinery changes
    """
    countChanged = pyqtSignal(int)

    def run(self):

        while  True:

            time.sleep(1)
            self.countChanged.emit(count)

class MDIWindow(QMainWindow):
    count = 0

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # multi document interface area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        bar = self.menuBar()
        self.scene_widgets = []
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
                imported_scene = self.controller.import_scene(text)

                self.controller.add_scene(imported_scene)
                print(text)
                self.scene_widgets.append(SceneWindow(imported_scene))
                self.controller.main_mix.playing = True



                # sub.setWindowTitle("Sub Window" + str(MDIWindow.count))
                # sub.setWindowFlags(sub.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint )

                # print(bin(sub.windowFlags()) + " " + bin(QtCore.Qt.MSWindowsFixedSizeDialogHint) + " " + bin(sub.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint))

                # sub.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
                # sub.setStyleSheet('background-color: grey; border: 3px solid black')



        if p.text() == "Open":
            scene_gui = Ui_scene_widget()
            self.scene_widget = QWidget()
            scene_gui.setupUi(self.scene_widget)
            self.scene_widget.show()
            tab_widget = QWidget()
            tab_widget.setObjectName("Testing")
            scene_gui.preset_tabs.addTab(tab_widget, "")
            tab_widget.show()

            layout = QHBoxLayout()

            scene_gui.brawl_tab.setLayout(layout)
            scene_gui.morning_tab.setLayout(layout)
            scene_gui.scrollAreaWidgetContents.setLayout(layout)
            # tab clicked -> set layout
            # match new preset fields

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
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)
    app.exec_()
