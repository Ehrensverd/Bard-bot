import os
import os
import sys
import threading
from asyncio import get_event_loop

import discord
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QPropertyAnimation, QSize
from PyQt5.QtWidgets import QApplication, QInputDialog
from discord.utils import get
from dotenv import load_dotenv
from validator_collection import checkers

from bardbot.bards import Channel, Scene, MainMixer
from bardbot.filehandler import FileHandler
from bardbot.playback import DiscordPlayback, Monitor
from bardbot.views import MainView, SceneView, ChannelView, AddChannelDialog

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')





class MainController(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Read config files and set discord_playback local_playback
        playback = None
        # Setup playback



        self.sources = []
        self.main_mix = MainMixer(self.sources)
        self.local_playback = Monitor(self.main_mix)
        self.discord_playback = None
        self.discord_client = None
        self.main_window = MainView()
        self.playing_discord = False
        self.main_window.join_button.setDisabled(True)
        self.discord_channel_id = self.main_window.channel_id_lineedit.text()
        self.setup_callbacks()


    def setup_callbacks(self):
        self.main_window.new_scene_button.clicked.connect(self.new_scene)
        self.main_window.import_button.clicked.connect(self.import_scene)
        self.main_window.discord_playback.connect(self.change_playback)
        self.main_window.channel_id_lineedit.textChanged.connect(self.channel_id_changed)
        self.main_window.join_button.clicked.connect(self.start_discord)

    def channel_id_changed(self, text):
        self.main_window.join_button.setDisabled(text=="")


    def start_discord(self):
        load_dotenv()
        BOT_TOKEN = os.getenv('TOKEN')
        GUILD_ID = os.getenv('GUILD_ID')
        channel_id = int(self.main_window.channel_id_lineedit.text())
        self.discord_playback = DiscordPlayback(self.main_mix)
        self.discord_client = DiscordClient(self.discord_playback,  channel_id, GUILD_ID)

        async def bot_final_start():
            await self.discord_client.start(BOT_TOKEN)

        def bot_loop_start(event_loop):
            event_loop.run_forever()

        loop = get_event_loop()
        loop.create_task(bot_final_start())
        bot_thread = threading.Thread(target=bot_loop_start, args=(loop,))

        bot_thread.start()


        self.main_window.discord_switch.setDisabled(False)

    def change_playback(self, discord):
        if discord:

            self.local_playback.is_active = False
            self.discord_playback.is_active = True
        else:
            self.discord_playback.is_active = False
            self.local_playback.is_active = True


    def import_scene(self):
        url, ok = QInputDialog.getText(self.main_window, 'Text Input Dialog', "Scene name", text="test test")
        if ok and checkers.is_url(url):
            temp_control = FileHandler()
            scene, channels = temp_control.import_scene(url)

            scene_controller = SceneController(new_scene_name=scene.scene_name, scene=scene)
            for channel in channels:
                channel_controller = ChannelController(parent=self, channel=channel)
                channel_controller.channel_view.play_button.click()

                scene_controller.channel_sources.append((channel_controller, channel))

                scene_controller.scene_view.channel_dock.new_channel_dock(channel_controller.channel_view, channel_name=channel.name)


            self.sources.append((scene_controller, scene_controller.scene))

    def new_scene(self):
        text, ok = QInputDialog.getText(self.main_window, 'Text Input Dialog', "Scene name", text="test test")
        if ok:
            scene_controller =SceneController(new_scene_name=text)
            self.sources.append((scene_controller,scene_controller.scene))




    def setup_scene(self, scene, scene_widget):
        self.main_mix.append(scene)
        self.main_window.add(scene_widget)
        scene_widget.play_button.clicked.connect(self.scene.play)


class SceneController(QObject):

    def __init__(self, new_scene_name=None, scene: Scene=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if new_scene_name:
            self.scene = Scene(scene_name=new_scene_name, channels=[])
            self.channel_sources = self.scene.channels
        else:
            self.scene = scene
            self.channel_sources = [ChannelController(parent=self, channel=channel) for channel in self.scene.channels]


        self.scene_view = SceneView(self.scene.scene_name)
        #self.scene_view.timed_button.setText(self.scene.scene_name)
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

    def add_channel(self):
        dialog = AddChannelDialog(scene_name=self.scene.scene_name)
        while not dialog.result:
            dialog.exec()



        if dialog.result[0] == "canceled":
            return
        elif dialog.result[0] == "file_path":
            channels = FileHandler().make_channels_from_files(dialog.result[1])

        elif dialog.result[0] == "url":
            channels = FileHandler().make_channel_from_url(dialog.result[1])

        for channel in channels:
            channel_controller = ChannelController(parent=self,channel=channel)
            self.channel_sources.append((channel_controller, channel))

            self.scene_view.channel_dock.new_channel_dock(channel_controller.channel_view, channel_name=channel.name)



    # Signals
    def setup_signals(self):
        # parent interface
        # child interface
        # self
        self.scene_view.add_channel.connect(self.add_channel)
        self.scene_view.scene_button_checked.connect(self.expander)
        # volume

        # Balance
        self.scene_view.balance_changed.connect(self.change_balance)

        # Play
        self.scene_view.play_pause.connect(self.play_pause_scene)



    def change_balance(self, value):
        self.scene.balance = value

    def play_pause_scene(self, is_playing):

        self.scene.scene_playing = is_playing


class ChannelController:
    def __init__(self, parent=None, channel_name=None, audio_file_path=None, audio_url=None, channel: Channel = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        if audio_file_path:

            self.channel = Channel(name=channel_name, audio_source=audio_file_path)
        else:
            self.channel = channel

        self.channel_view = ChannelView(None, channel_name=self.channel.name)
        self.previous_volume = self.channel.volume

        self.setup_volume()
        self.setup_signals()

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

    def setup_signals(self):
        self.channel_view.play_pause.connect(self.pause_channel)
        self.channel_view.balance_changed.connect(self.set_scene_balance)
        self.channel_view.triggered.connect(self.trigger_clicked)
        self.channel_view.crossfaded.connect(self.change_crossfade)
        self.channel_view.combo_changed.connect(self.set_channel_mode)
        self.channel_view.amount_edit.valueChanged.connect(self.amount_edited)

    def amount_edited(self, value):
        mode = self.channel_view.channel_mode_box.currentIndex()
        if mode >= 4:

            if mode == 5:
                self.channel.loops = float("inf")
            else:
                self.channel.loops = value
        else:
            self.channel.random_amount = value

    def set_channel_mode(self, mode):
        # TODO: Check if random ratio is possibe
        scene_offset = self.parent.scene.ms + self.parent.scene.sec + self.parent.scene.min
        self.channel.is_looped = mode >= 4

        if mode >= 4:
            self.channel.schedule = self.channel.loop_scheduler(scene_offset)
            if mode == 5:
                self.channel.loops = float("inf")
            else:
                self.channel.loops = self.channel_view.amount_edit.text()
        else:
            self.channel.schedule = self.channel.random_seg_scheduler(scene_offset)
            if mode == 0:
                self.channel.random_time_unit = 60
            elif mode == 1:
                self.channel.random_time_unit = 600
            else:
                self.channel.random_time_unit = 3600

    def change_crossfade(self, is_crosfaded):
        if is_crosfaded:

            self.channel.loop_gap = -0.3

        else:
            self.channel.loop_gap = 0

    def trigger_clicked(self):
        # TODO: Check next playtime takeover

        self.channel.is_triggered = True



    def set_scene_balance(self, value):
        self.channel.balance = value

    def pause_channel(self, is_playing):

        self.channel.is_paused = not is_playing
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

class DiscordClient(discord.Client):


    def __init__(self, playback, channel_id, guild_id,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playback = playback
        self.playback.fill.start()
        self.channel_id = channel_id
        self.guild_id = guild_id

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        channel = self.get_channel(self.channel_id)
        voice = get(self.voice_clients, guild=self.guild_id)
        if not voice or not voice.is_connected():
            voice = await channel.connect()
            await voice.move_to(channel)
        else:
            await voice.move_to(channel)


        if not voice.is_playing():  # change source
            voice.play(self.playback)




def main():
    sys.setswitchinterval(0.001)
    qApp = QApplication(sys.argv)
    qApp.setStyle("Fusion")

    mdi = MainController()
    mdi.main_window.show()
    # timer = QTimer()
    # timer.timeout.connect(lambda: None)
    # timer.start(100)
    qApp.exec_()

main()