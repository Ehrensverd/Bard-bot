import os
import sys
from pprint import pprint

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, QPropertyAnimation, QSize
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QGraphicsOpacityEffect
from dotenv import load_dotenv

from bardbot.bards import AudioSource, Channel, Scene, MainMixer
from bardbot.playback import DiscordPlayback, Monitor
from bardbot.views import MainView, SceneView, ChannelView

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')





class MainController(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Read config files and set discord_playback local_playback
        playback = None
        # Setup playback
        discord_playback = False
        local_playback = True

        self.sources = []
        self.main_mix = MainMixer(self.sources)

        self.playback = None
        if discord_playback:
            self.playback = DiscordPlayback(self.main_mix.segment_generator())
        if local_playback and not discord_playback:
            self.playback = Monitor(self.main_mix)

        self.main_window = MainView()

        self.setup_callbacks()


    def setup_callbacks(self):
        self.main_window.new_scene_button.clicked.connect(self.new_scene)
        print("kakfka")

        #self.main_window.import_selcted.clicked.connect(self.import_scene)


    def new_scene(self):
        text, ok = QInputDialog.getText(self.main_window, 'Text Input Dialog', "Scene name", text="test test")
        if ok:
            self.sources.append(SceneController(new_scene_name=text))


    def setup_scene(self, scene, scene_widget):
        self.main_mix.append(scene)
        self.main_window.add(scene_widget)
        scene_widget.play_button.clicked.connect(self.scene.play)


class SceneController(QObject):

    def __init__(self, new_scene_name=None, scene: Scene=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if new_scene_name:
            self.scene = Scene(scene_name=new_scene_name, channels=[])
            self.channel_sources = []
        else:
            self.scene = scene
            self.channel_sources = [ChannelController(channel=channel) for channel in self.scene.channels]


        self.scene_view = SceneView(self.scene.scene_name)

        self.setup_animations()
        self.setup_signals()
        # Sync Scene and View
        # Volume
        self.muted_value_holder = 0

        self.setup_volume()

    #Animations
    def setup_animations(self):
        start_width =0
        end_width = 0
        for index in range(len(self.scene_view.channel_dock.channel_docks)):
            end_width += 87

        self.animation = QPropertyAnimation(self.scene_view.preset_tab, b'size')
        self.animation.setDuration(250)
        self.animation.setStartValue(QSize(start_width, self.scene_view.preset_tab.height()))
        self.animation.setEndValue(QSize(end_width, self.scene_view.preset_tab.height()))

    def expander(self, checked):
        direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
        end_width = 0
        for index in range(len(self.scene_view.channel_dock.channel_docks)):
            end_width += 87
        end_width = end_width + 80
        self.scene_view.preset_tab.setMaximumWidth(end_width)
        self.animation.setEndValue(QSize( end_width, self.scene_view.preset_tab.height()))
        self.animation.setDirection(direction)
        self.animation.start()

    # Volume
    def setup_volume(self):
        self.previous_volume = self.scene.scene_volume
        self.set_view_volume(self.scene.scene_volume)

        self.scene_view.mute_unmute.connect(self.mute_view_clicked)
        self.scene_view.volume_changed.connect(self.slider_view_changed)

    def set_view_volume(self, value):
        self.scene_view.volume_slide.setValue(value)

    def set_scene_volume(self, value):
        self.previous_volume = self.scene.scene_volume
        self.scene.scene_volume = value

    def mute_view_clicked(self, muting):  # Volume Slots
        if muting:
            self.set_view_volume(0)
        else:
            self.set_view_volume(self.previous_volume)

    def slider_view_changed(self, value):
        # self.scene_view.volume_slide.blockSignals(True)
        # self.scene_view.mute_button.blockSignals(True)
        if value == 0 or self.previous_volume == 0:
            self.scene_view.change_mute_icons(value == 0)
            self.scene_view.mute_button.setChecked(value == 0)
        self.set_scene_volume(value)
        # self.scene_view.volume_slide.blockSignals(False)
        # self.scene_view.mute_button.blockSignals(False)

    # Signals
    def setup_signals(self):
        # parent interface
        # child interface
        # self

        self.scene_view.scene_button_checked.connect(self.expander)
        # volume

        # Balance
        self.scene_view.balance_changed.connect(self.change_balance)




    def change_balance(self, value):
        self.scene.balance = value

    def play_pause_scene(self):
        self.scene.scene_playing = not self.scene.scene_playing


class ChannelController:
    def __init__(self, channel_name=None, audio_file_path=None, audio_url=None, channel: Channel = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if audio_file_path:

            self.channel = Channel(name=channel_name, audio_source=audio_file_path)
        else:
            self.channel= channel

        self.channel_view = ChannelView(self.channel.name)
        self.previous_volume = self.channel.volume

        self.setup_volume()

    # Volume
    def setup_volume(self):
        self.set_view_volume(self.channel.volume)

        self.channel_view.mute_unmute.connect(self.mute_view_clicked)
        self.channel_view.volume_changed.connect(self.slider_view_changed)

    def set_view_volume(self, value):
        self.channel_view.volume_slide.setValue(value)

    def set_scene_volume(self, value):
        self.previous_volume = self.channel.volume
        self.channel.volume = value

    def mute_view_clicked(self, muting):  # Volume Slots
        if muting:
            self.set_view_volume(0)
        else:
            self.set_view_volume(self.previous_volume)

    def slider_view_changed(self, value):
        # self.scene_view.volume_slide.blockSignals(True)
        # self.scene_view.mute_button.blockSignals(True)
        if value == 0 or self.previous_volume == 0:
            self.channel_view.change_mute_icons(value == 0)
            self.channel_view.mute_button.setChecked(value == 0)
        self.set_scene_volume(value)
        # self.scene_view.volume_slide.blockSignals(False)
        # self.scene_view.mute_button.blockSignals(False)

    def pause_channel(self):
        pass

    def change_volume(self, volume):
        pass

    def change_balance(self, balance):
        pass

    def mute(self):
        pass

    def trigger(self):
        pass

    def set_mode(self, mode):
        pass

    def set_random_time_unit(self, value):
        pass

    def set_random_amount(self, value):
        pass

    def loop_type(self):
        pass

    def set_loops(self, value):
        pass

    def set_loop_gap(self, value):
        pass


def main():
    app = QApplication(sys.argv)

    mdi = MainController()

    mdi.main_window.show()
    # timer = QTimer()
    # timer.timeout.connect(lambda: None)
    # timer.start(100)
    app.exec_()

main()