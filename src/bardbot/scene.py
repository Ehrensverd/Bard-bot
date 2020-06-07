from urllib.request import urlopen
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from pydub import AudioSegment
import requests

from .channel import Channel


class Scene:
    """
        A class to represent an audio scene.

        ...

        Attributes
        ----------
        channels : dict { channel# : channel instance}
            collection of all channels in the scene mix


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
                    print(self.sec)
                    self.sec = 0
                    self.min += 1
                    for channel in self.channels.values():
                        if channel.depleted and channel.random_unit == 1:
                            channel.depleted = False
                        if min == 10 and channel.random_unit == 10:
                            channel.depleted = False
                    if self.min >= 60:
                        for channel in self.channels.values():
                            if channel.depleted and channel.random_unit == 3600:
                                channel.depleted = False
                        self.min = 0

            segment = AudioSegment.silent(duration=20)
            for channel in self.channels.values():
                if not channel.is_active:
                    if channel.next_play_time <= self.sec + (self.min * 60) and not channel.depleted:
                        print('channel ', channel.name, ' is now active at time ', self.sec + (self.min * 60))
                        channel.is_active = True
                        channel.seg_gen = channel.segment_generator()
                if channel.is_active:
                    try:
                        seg = next(channel.seg_gen)
                        segment = segment.overlay(seg)
                    except StopIteration:
                        print("Exception: ", channel.name, "is random:", channel.is_random, "| Is active:",
                              channel.is_active)

                        continue
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

                    channels['channel' + str(num)] = Channel(audio_name, audio_id, mp3_url, mute, volume, balance,
                                                             is_random,
                                                             random_counter, random_unit, cross_fade)
                num += 1
        return channels
