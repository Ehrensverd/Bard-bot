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
import os
import pickle
import random
from os import path
from urllib.request import urlopen
from xml.etree import ElementTree
import concurrent.futures

import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment

from bardbot.AudioMixer.audio_source import AudioSource

# Utility
from bardbot.AudioMixer.channels import Channel


# File management


def save_scene_as(scene, directory_path):
    # if file_path exist confirm overwrite
    if path.exists(directory_path):
        print("scene  exists, overwrite")
        # qt dialog
        return

    # save channels to file
    for channel in scene.channels:
        channel.audio_source.save_as(directory_path
                                     + scene.scene_name + channel.name + ".mp3", channel.segment)

    # save scene preset
    with open(directory_path + scene.scene_name + "presets.txt", 'wb') as f:
        pickle.dump(scene.presets, f, pickle.HIGHEST_PROTOCOL)


def load_scene(directory_path, active_preset):
    # TODO remove from stage class, make utility.
    print("Loading scene from path:", directory_path)
    with open(directory_path + "presets.txt", 'rb') as f:
        scenes = pickle.load(f)

    scene_name = os.path.basename(os.path.normpath(directory_path))
    print("Scene name:", scene_name)
    return Scene(scene_name, load_channels(directory_path + "/channels/", scenes[active_preset]), scenes, active_preset)


# TODO: make possible to only import subset of channels
def load_channels(directory_path, active_preset):
    """
    Returns dict { "channel_name" : channel_instance }


     """
    return {channel_name: Channel(channel_name, AudioSource(file=directory_path + channel_name),
                                  **active_preset[channel_name]) for channel_name in os.listdir(directory_path)}


def import_scene(url):
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

    def import_channel(item):

        if item.tag.startswith('channel'):
            if item.findtext('id_audio') == '0':
                return None
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
                return ('channel' + str(num), Channel(audio_name, audio_source, random_counter, random_unit, balance,
                                                      volume, mute, cross_fade, is_random, not is_random))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        channels = executor.map(import_channel, ElementTree.parse(url).iter())

    scene_name = url.rsplit('/', 1)[-1]
    preset = make_scene_preset(channels)
    return scene_name, channels, preset, preset


def make_scene_preset(channels):
    """ """
    # TODO Rename channel.preset to channel.fields or channel.values
    return {channel.name: channel.preset for channel in channels}


def align_presets(channel, new_channel_preset, preset):
    changed = False
    if channel[preset] < new_channel_preset[preset]:
        channel[preset] += 1
        changed = True
    elif channel[preset] > new_channel_preset[preset]:
        new_channel_preset[preset] -= 1
        changed = True
    return changed


class Scene:
    """Base audio template for soundscapes

    Attributes
    ----------
    scene_volume : int
        main volume for stage

    presets : dict { preset_name : channel_presets{}}
        collection of loaded scenes.
        each scene is a different preset for the stage.
     channel_presets : dict { channel_name : channel_preset{} }
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

    active_preset : scene preset
        scene from which stage segmenter get channel settings

    new_actve_scene

    stage_segmenter()
        Yields 20ms of mixed audio from all active channels

    ms, sec, min : int
        Providing time mapping for scene generator.

    Methods
    -------

        """

    def __init__(self, scene_name, channels, presets, active_preset):
        self.scene_name = scene_name
        self.channels = channels
        self.paused_channels = {}

        if presets is None:
            self.presets = self.default_presets()
        else:
            self.presets = presets

        self.active_preset = active_preset
        self.changing_preset = False
        self.next_preset = None

        self.ms = self.sec = self.min = self.hour = 0
        self.segmenter = self.scene_generator()
        self.scene_volume = 50
        self.scene_playing = True

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
            # empty base
            segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

            #
            if self.scene_playing:
                if self.changing_preset:
                    self.preset_changer()
                for channel in self.channels.values():
                    # only active channels are yielded from
                    if not channel.is_playing:
                        if channel.next_play_time <= self.sec + (self.min * 60) and not channel.depleted:
                            print(channel.name, "now playing. Time:", self.sec + (self.min * 60))
                            channel.is_playing = True
                            channel.seg_gen = channel.segment_generator()
                    if channel.is_playing:
                        try:
                            segment = segment.overlay(next(channel.seg_gen))
                        except StopIteration:
                            print(channel.name, "finished playing")
                            continue
            yield segment

    def preset_changer(self):
        """
        method called within stage generator
            shfiting values towards new scene
        """

        # 2 start shifting towards new values
        # if active in old and nonactive in new -> 0
        # else shift til matches new value
        changed = False
        # activated scenes
        for channel in self.channels:
            # if (preset["volume"]) == self.active_scene[channel]["volume"]:
            #     self.active_scene[channel]["volume"] -= (self.active_scene[channel]["volume"] - preset["volume"])/abs( self.active_scene[channel]["volume"] - preset["volume"])
            changed = align_presets(channel, "volume") or align_presets(channel, "balance")

        if not changed:
            # 3 when done, set old active to non active if non active in new.
            for channel in self.channels:
                channel.__dict__.update(**self.next_preset[channel.name])
                # channel.is_active = self.new_scene[channel.name]["is_active"]
                # channel.volume = self.new_scene[channel.name]["volume"]
                # channel.balance = self.new_scene[channel.name]["balance"]
                # channel.random_unit = self.new_scene[channel.name][""]
                # channel. = self.new_scene[channel.name][""]
                # channel. = self.new_scene[channel.name][""]
                # channel. = self.new_scene[channel.name][""]
            # if not self.new_scene.channel.is_active and channel.is_active:
            #         channel.is_active = False

            self.changing_preset = False

    def change_preset(self, next_preset=None):
        """initial scene change method. sets"""
        # 1 find active scenes that are non active in current
        # make active and set volume = 0
        if next_preset:
            self.next_preset = next_preset

        for channel, preset in self.next_preset.items():
            if (preset["is_active"]) and not self.active_preset[channel]["is_active"]:
                preset["volume"] = 0
                self.active_preset[channel]["is_active"] = True

        self.changing_preset = True

    def add_preset(self, preset, preset_name):
        # TODO: Assert scene is valid

        if preset not in self.presets:
            self.presets[preset_name] = preset

    def remove_preset(self, preset_name):
        if preset_name in self.presets:
            self.presets[preset_name].remove(preset_name)

    def default_presets(self):
        presets = {"default_preset": self.get_channel_presets()}
        return presets

    def get_channel_presets(self):
        channel_presets = {channel.name: channel.preset_fields() for channel in self.channels}
        return channel_presets
