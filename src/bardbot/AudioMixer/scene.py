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
from pprint import pprint
from urllib.request import urlopen
from xml.etree import ElementTree
import concurrent.futures

import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
from pydub.utils import ratio_to_db

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
        self.scene_balance = 0
        self.scene_playing = True
        self.low_pass = False

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
                    # This prevents a ratio of x times per 10 minutes, in cases where the last
                    # of the x plays ends before the 10 minute mark, to start a new x times per 10 min
                    # before the original 10 minutes have passed.
                    for channel in self.channels.values():
                        if channel.depleted and channel.random_time_unit == 1:
                            channel.depleted = False
                        if self.min == 10 and channel.random_time__unit == 10:
                            channel.depleted = False
                    if self.min >= 60:
                        for channel in self.channels.values():
                            if channel.depleted and channel.random_time__unit == 3600:
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
                    if not channel.is_playing and channel.is_random:
                        # Check if its time to start playing random segments
                        if channel.next_play_time <= self.sec + (self.min * 60) and not channel.depleted:
                            print(channel.name, "now playing. Time:", self.sec + (self.min * 60))
                            channel.is_playing = True
                            channel.seg_gen = channel.segment_generator()
                    if channel.is_playing:
                        try:
                            channel_segment = next(channel.seg_gen).apply_gain(ratio_to_db(channel.volume / 25))
                            segment = segment.overlay(channel_segment.pan(self.balance_panning(channel.balance)))
                        except StopIteration:
                            print(channel.name, "finished playing")
                            continue

            yield segment.apply_gain(ratio_to_db(self.scene_volume / 25))

    def balance_panning(self, channel_balance):
        # Scale range for channel balance, based on
        # scene balance

        channel_min_range = (50 - self.scene_balance) * -2 if self.scene_balance > 0 else -100
        channel_max_range = (50 + self.scene_balance) * 2 if self.scene_balance < 0 else 100

        # def rescale(val, in_min, in_max, out_min, out_max):
        #     return out_min + (val - in_min) * ((out_max - out_min) / (in_max - in_min))
        pan = channel_min_range + (channel_balance - -100) * ((channel_max_range - channel_min_range) / (100 - -100))

        return int(pan) / 100

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
        for channel in self.channels.values():
            # if (preset["volume"]) == self.active_scene[channel]["volume"]:
            #     self.active_scene[channel]["volume"] -= (self.active_scene[channel]["volume"] - preset["volume"])/abs( self.active_scene[channel]["volume"] - preset["volume"])
            changed = align_presets(channel, "volume") or align_presets(channel, "balance")

        if not changed:
            # 3 when done, set old active to non active if non active in new.
            for channel in self.channels.values():
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
