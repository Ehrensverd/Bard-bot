"""
A stage is a collection of Scenes that share  at least 1 channel.
A channel can only be handled by 1 scene at a time.
A stage can have multiple scenes.

Reason for stage is so one can easily find related soundscapes and
be able to seemlessly transition between them.
Tavern - Busy.
becomes
Tavern - Brawl
With a scene change, channels are gradually shifted towards their new values.

When a stage is loaded into a group its scenes are also loaded and readied
Stage yields from active scene to main_mix

Stage has all channels in two collection, active and non active
on scene change channel collections are updated.

"""
import io
import pickle
import random
from os import path
from urllib.request import urlopen
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment

from bardbot.AudioMixer.audio_source import AudioSource



# Utility
from bardbot.AudioMixer.channels import Channel


def load_stage_scene(self, file_path):
    pass

# TODO: make possible to only import subset of channels
def import_stage(self, url):
    """Parse channels from XML file

    Returns a dicitionary {channel# : channel instance }

    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    temnplate_id = soup.select_one("a[href*=vote]")['href'].rpartition('/')[2]
    url = 'https://xml.ambient-mixer.com/audio-template?player=html5&id_template=' + str(temnplate_id)

    url = urlopen(url)
    channels = {}
    num = 1
    for item in ElementTree.parse(url).iter():

        if item.tag.startswith('channel'):
            if item.findtext('id_audio') == '0':
                continue
            else:
                audio_id = int(item.findtext('id_audio'))
                audio_name = item.findtext('name_audio')
                mp3_url = item.findtext('url_audio')
                mute = (item.findtext('mute') == 'true')
                volume = int(item.findtext('volume'))
                balance = int(item.findtext('balance'))
                is_random = (item.findtext('random') == 'true')
                random_counter = int(item.findtext('random_counter'))
                random_unit = item.findtext('random_unit')
                cross_fade = (item.findtext('crossfade') == 'true')
                audio_source = AudioSource(url=mp3_url)

                # TODO: check if is_active can be deactivated in ambient-mixer while not random, and if it creates issues.
                channels['channel' + str(num)] = Channel(audio_name, audio_source, random_counter, random_unit, balance,
                                                         volume, mute, cross_fade, is_random, not is_random)

    return channels


class Stage:
    """Base audio template for soundscapes

    Attributes
    ----------
    stage_volume : int
        main volume for stage

    scenes : dict { scene_name : scene_presets{}}
        collection of loaded scenes.
        each scene is a different preset for the stage.
     channel_presets : dict { channel instance : channel_preset{} }
        collection of scene channels and corresponding presets
    channel_preset : dict { volume : int,
                            balance : int,
                            is_random : bool,
                                indicate randomly triggered segment
                            random_rate : int,
                            random_unit : int,
                            is_crossfade : boolean,
                                - only non randomly triggered segments are cross faded
                            crossfade_amount : int
                            }
        channel preset

    channels : dict { channel_name : channel instance }
        collection of channels.
        channel behavior depends on the active scene

    active_scene : scene preset
        scene from which stage segmenter get channel settings

    new_actve_scene

    stage_segmenter()
        Yields 20ms of mixed audio from all active channels

    ms, sec, min : int
        Providing time mapping for scene generator.

    Methods
    -------

        """

    def __init__(self, channels, scenes, active_scene):

        self.channels = channels
        self.paused_channels = {}
        self.scenes = scenes
        self.active_scene = active_scene


        self.ms = self.sec = self.min = self.hour = 0
        self.segmenter = self.scene_generator()
        self.scene_volume = 50
        self.stage_playing = True

    def pause_channel(self, channel):
        self.paused_channels[channel] = self.channels.pop(channel)

    def unpause_channel(self, channel):
        self.channels[channel] = self.paused_channels.pop(channel)

    def scene_generator(self):
        """Generates 20ms worth of opus encoded raw bytes
        Checks if scheduled segments, and sets to active when needed

        Overlays all active segments
        """

        while True:
            # time schedule
            self.ms += 20
            if self.ms >= 1000:
                self.ms = 0
                self.sec += 1
                if self.sec >= 60:
                    self.sec = 0
                    self.min += 1
                    # Resets depleted random channels  at corresponding 1 min, 10 min and 1 hour mark
                    for channel in self.channels.values():
                        if channel.depleted and channel.random_unit == 1:
                            channel.depleted = False
                        if self.min == 10 and channel.random_unit == 10:
                            channel.depleted = False
                    if self.min >= 60:
                        for channel in self.channels.values():
                            if channel.depleted and channel.random_unit == 3600:
                                channel.depleted = False
                        self.min = 0
            #empty base
            segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

            #
            if self.stage_playing:
                for channel in self.channels.values():
                    if not channel.is_active:
                        if channel.next_play_time <= self.sec + (self.min * 60) and not channel.depleted:
                            print(channel.name, "now playing. Time:", self.sec + (self.min * 60))
                            channel.is_active = True
                            channel.seg_gen = channel.segment_generator()
                    if channel.is_active:
                        try:
                            segment = segment.overlay(next(channel.seg_gen))
                        except StopIteration:
                            print(channel.name, "finished playing")
                            continue
            yield segment

    def change_scene(self, new_scene):
        pass

    def save_scene(self, scene):
        # TODO: channel needs altered flag
        pass

    def save_scene_as(self, scene, directory_path):
        # if file_path exist confirm overwrite
        if path.exists(directory_path):
            print("scene  exists, overwrite")
            # qt dialog
        for channel in self.channels:
            channel.audio_source.save_as("/home/eskil/PycharmProjects/Bard-bot/src/bardbot/temp_files/" + scene["name"] + "/" + channel.name, channel.segment)
        "/home/eskil/PycharmProjects/Bard-bot/src/bardbot/temp_files/" + scene["name"] + "/"

        with open(scene["name"] + ".txt", 'wb') as f:
            pickle.dump(scene, f, pickle.HIGHEST_PROTOCOL)

    def add_scene(self, scene, scene_name):
        # TODO: Assert scene is valid

        if scene not in self.scenes:
            self.scenes[scene_name] = scene


    def remove_scene(self):
        pass


    def defualt_preset(self):
        preset = {"is_channel_active": False,
                  "volume": 50,
                  "balance": 0,
                  "is_random": False,
                  "random_rate": 0,
                  "random_unit": 1,
                  "is_crossfade": False,
                  "crossfade_amount": 100
                  }
        return preset



