import concurrent.futures
import time
from pprint import pprint
from urllib.request import urlopen
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from bardbot.bards import AudioSource, Channel, Scene
from bardbot.AudioMixer.channels import Channel
from bardbot.AudioMixer.scene import Scene


class Controller:
    def __init__(self, main_mix, playback):
        self.main_mix = main_mix
        self.playback = playback

    # Scene
    # Import
    def import_scene(self, url):
        """Parse channels from XML file

        Returns a dicitionary {channel# : channel instance }

        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        scene_name = url.rsplit('/', 1)[-1]

        temnplate_id = soup.select_one("a[href*=vote]")['href'].rpartition('/')[2]
        url = 'https://xml.ambient-mixer.com/audio-template?player=html5&id_template=' + str(temnplate_id)

        url = urlopen(url)
        channels = {}
        num = 1

        def import_channel(item):
            print("importing channel")
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
                    if cross_fade:
                        loop_gap = -0.3
                    else:
                        loop_gap = 0
                    print("making channels")
                    channel = Channel(audio_name, audio_source, random_counter, random_unit, balance,
                                      volume, mute, not is_random, False, False, loop_gap)
                    return channel

        print("making threads finished")

        new_urls = [new_url for new_url in ElementTree.parse(url).iter() if new_url.tag.startswith('channel')]
        # print("new")
        # pprint(new_urls)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            channels = [channel for channel in executor.map(import_channel, new_urls) if
                        channel is not None]
        # channels = self.get_channels(new_urls)
        pprint(channels)
        preset = self.make_scene_preset(channels)
        pprint(preset)
        print("making scene finished")
        return Scene(scene_name, channels, preset, scene_name)

    def make_scene_preset(self, channels):
        """ """
        # TODO Rename channel.preset to channel.fields or channel.values
        print("making scene presets")
        return {channel.name: channel.channel_fields() for channel in channels}

    def get_channels(self, url):
        """Parses channels from XML file
        Returns a dicitionary {channel# : channel instance }
        """

        channels = []
        num = 1
        for item in url:

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
                    print("problems?")
                    time.sleep(1)
                    channels.append(Channel(audio_name, audio_source, random_counter, random_unit, balance,
                                            volume, mute, cross_fade, is_random, not is_random))
                num += 1
        return channels

    def add_scene(self, scene):
        self.main_mix.add_source(scene)
