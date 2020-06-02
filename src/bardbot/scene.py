import random
from urllib.request import urlopen
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from .channel import Channel
from pydub import AudioSegment


class Scene:
    """
        A class to represent an audio scene.

        ...

        Attributes
        ----------
        channels : dict { channel# : channel instance}
            collection of all channels in the scene mix

        looped_segments : list [channel#]
            list of channels that are continuously looping

        random_segments : list [channel#]
            list of channels that are continuously looping

        is_active : dict { channel# : boolean}
            dictionary indicating wheter segment is being sent to main stream

        scheduler = dict{channel# : generator }
            dictionary with generators providing next random play time

        next_play_time = dict {channel# : int}
            dictionary with next scheduled play time for random type segment

        ms, sec, min = int
            Providing time mapping for main generator.

        Methods
        -------

        """

    def __init__(self, url):
        self.channels = self.get_channels(url)
        self.ms = self.sec = self.min = self.hour = 0
        self.gen = self.main_generator()

    def main_generator(self):
        """Generates 20ms worth of opus encoded raw bytes
        Checks if scheduled segments, and sets to active when needed

        Overlays all active segments
        """

        while True:
            self.ms += 20
            if self.ms >= 1000:
                self.ms = 0
                self.sec += 1
                if self.sec >= 60:
                    self.sec = 0
                    self.min += 1
                    if self.min >= 60:
                        self.min = 0
            if self.ms == 0:
                print('new empty')
            segment = AudioSegment.silent(duration=20)
            for channel in self.channels.values():
                if not channel.is_active:
                    if channel.next_play_time <= self.sec + self.min * 60:
                        print('channel ', channel.name , ' is now active')
                        channel.is_active = True
                        channel.seg_gen = channel.segment_generator()
                if channel.is_active:
                    if self.ms == 0:
                        print('Adding: ', channel.name)

                    try:
                        seg = next(channel.seg_gen)
                        segment = segment.overlay(seg)
                    except StopIteration:
                        continue
            if self.ms == 0:
                print('yielding 20ms merged')

            yield segment



    def get_channels(self, url):
        """Parses channels from XML file

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
                    audio_id = item.findtext('id_audio')
                    audio_name = item.findtext('name_audio')
                    link = item.findtext('url_audio')
                    mute = item.findtext('mute')
                    volume = item.findtext('volume')
                    balance = item.findtext('balance')
                    is_random = (item.findtext('random') == 'true')

                    random_counter = item.findtext('random_counter')
                    random_unit = item.findtext('random_unit')
                    cross_fade = item.findtext('crossfade')
                    channels['channel' + str(num)] = Channel(audio_name, audio_id, link, mute, volume, balance,
                                                             is_random,
                                                             random_counter, random_unit, cross_fade)

                num = num + 1
        return channels
