from urllib.request import urlopen
from xml.etree import ElementTree


from bs4 import BeautifulSoup
from pydub import AudioSegment
import requests

from .channel import Channel


class Scene:
    """
        Represents an audio soundscape, like a dark moist cave, battlefield or tavern.
        ...
        Attributes
        ----------
        channels : dict { channel# : channel instance}
            collection of all channels in the scene mix

        pause_channels : dict { channel# : channel instance}
            collection of all paused channels in the scene mix

        ms, sec, min : int
            Providing time mapping for scene generator.

        segmenter : generator
            Yields 20ms of mixed audio from all active channels

        scene_volume : int
            Scene master volume

            
        Methods
        -------

        """

    def __init__(self, url):
        self.channels = self.get_channels(url)
        self.paused_channels = {}
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
            self.ms += 20
            if self.ms >= 1000:
                self.ms = 0
                self.sec += 1
                if self.sec >= 60:
                    self.sec = 0
                    self.min += 1
                    # Reseting depleted channels 1 min, 10 min and 1 hour
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

            segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)
            if self.scene_playing:
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



