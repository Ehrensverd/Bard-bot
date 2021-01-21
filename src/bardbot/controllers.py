import os
import sys
import threading
from asyncio import get_event_loop

from PyQt5 import Qt
from PyQt5.QtCore import QTimer, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from discord.ext.commands import bot
from dotenv import load_dotenv

from bardbot.AudioMixer.scene import Scene
from bardbot.AudioMixer.main_mixer import MainMixer, Monitor
from bardbot.views import MainView, SceneView

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')


class DiscordPlayback(object):
    def __init__(self, slices):
        self.slices = slices
    pass


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
            self.scene_controller = SceneController(new_scene_name=text)
            self.scene_controller.scene_view

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
        self.scene_view = SceneView()


    def change_balance(self, value):
        self.scene.balance = value

    def change_volume(self, value):
        self.scene.scene_volume = value

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