import os
import sys
from pprint import pprint

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, QPropertyAnimation, QSize
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QGraphicsOpacityEffect
from dotenv import load_dotenv

from bardbot.AudioMixer.main_mixer import MainMixer, Monitor
from bardbot.AudioMixer.scene import Scene
from bardbot.playback import DiscordPlayback
from bardbot.views import MainView, SceneView

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
        else:
            self.scene = scene

        self.scene_view = SceneView(self.scene.scene_name)

        self.scene_view.play_pause.connect(self.trigger_scene_play)
        self.setup_animations()
        self.setup_signals()
        # Volume
        self.muted_value_holder = 0
        print(self.scene.scene_volume)
        self.setup_volume()

    def setup_animations(self):
        start_width =0
        sum = 0

        for index in range(len(self.scene_view.channel_dock.channel_docks)):
            sum += 87

        end_width = sum


        self.animation = QPropertyAnimation(self.scene_view.preset_tab, b'size')
        self.animation.setDuration(300)
        self.animation.setStartValue(QSize(start_width, self.scene_view.preset_tab.height()))
        self.animation.setEndValue(QSize(end_width,self.scene_view.preset_tab.height()))



    def setup_volume(self):
        self.previous_volume = self.scene.scene_volume
        self.set_view_volume(self.scene.scene_volume)

        self.scene_view.mute_unmute.connect(self.mute_view_clicked)
        self.scene_view.volume_changed.connect(self.slider_view_changed)

    def mute_view_clicked(self, muting):
        if muting:
            self.set_view_volume(0)
        else:
            self.set_view_volume(self.previous_volume)

    def slider_view_changed(self, value):
        self.scene_view.volume_slide.blockSignals(True)
        self.scene_view.mute_button.blockSignals(True)

        if value == 0 or self.previous_volume == 0:
            self.scene_view.change_mute_icons(value == 0)
            self.scene_view.mute_button.setChecked(value == 0)

        self.set_scene_volume(value)

        self.scene_view.volume_slide.blockSignals(False)
        self.scene_view.mute_button.blockSignals(False)

    def set_view_volume(self, value):
        self.scene_view.volume_slide.setValue(value)

    def set_scene_volume(self, value):
        self.previous_volume = self.scene.scene_volume
        self.scene.scene_volume = value


    def setup_signals(self):
        # parent interface


        # child interfave

        # self

        self.scene_view.scene_button_checked.connect(self.expander)
        # volume

        # Balance
        self.scene_view.balance_changed.connect(self.change_balance)

    # def adjust_size(self, checked):
    #     if checked:
    #         self.scene_view.setFixedWidth(902)

    def expander(self, checked):
        #TODO calc size based on channels and adjust

        sum = 0

        for index in range(len(self.scene_view.channel_dock.channel_docks)):
            sum += 87

        sum = sum +87
        self.scene_view.preset_tab.setMaximumWidth(sum)
        self.animation.setEndValue(QSize( sum, self.scene_view.preset_tab.height()))

        direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
        # self.animation.setStartValue(0)
        self.animation.setDirection(direction)
        self.animation.start()


    def trigger_scene_play(self, checked):
        print(checked)


    def change_balance(self, value):
        print(value)
        self.scene.balance = value


    def play_pause_scene(self):
        self.scene.scene_playing = not self.scene.scene_playing

class ChannelController:
    def __init__(self, channel):
        self.channel = channel

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