import concurrent
import io
from pprint import pprint
from sys import platform
from collections import defaultdict
import hashlib
import os
import sys
from urllib.request import urlopen
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
from shutil import copyfile

from bardbot.bards import Channel, Scene


class FileHandler:
    def __init__(self):
        #check what file system'
        self.system_os = platform

        dirname = os.path.dirname(__file__)
        self.library_path = os.path.join(dirname, 'Audio Library/')
        if not os.path.exists(self.library_path):
            os.makedirs(self.library_path)

        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "darwin":
            pass
        elif platform == "win32":
            pass

    def make_channel_from_url(self, url):


        try:
            mp3 = requests.get(url).content
            mp3_name = str(url).rsplit("/", 1)[-1]

            file_path = os.path.join(self.library_path + mp3_name)

            with open(file_path, 'wb') as f:
                f.write(mp3)

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)


        return [Channel(name=mp3_name.rsplit(".",1)[0], audio_source=io.BytesIO(mp3))]
        # Save to temp location



    def make_channels_from_files(self, files):
        channels = []
        for mp3 in files:

            mp3_name = str(mp3).rsplit("/",1)[-1]
            # print("mp3 dir",os.path.dirname(mp3) )
            # print("lib dir",os.path.dirname(self.library_path) )
            # print("lib path", self.library_path)
            if not os.path.dirname(mp3) == os.path.dirname(self.library_path): # if not in library then add
                copyfile(mp3, os.path.join(self.library_path + mp3_name))
                mp3 = os.path.join(self.library_path + mp3_name)

            channels.append(Channel(name=mp3_name.rsplit(".",1)[0], audio_source=mp3))
        return channels

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
                    cross_fade = False # (item.findtext('crossfade') == 'true')

                    if cross_fade:
                        loop_gap = -0.3
                    else:
                        loop_gap = 0

                    try:

                        dirname = os.path.dirname(__file__)
                        library_path = os.path.join(dirname, 'Audio Library/')

                        mp3 = requests.get(mp3_url).content
                        mp3_name = str(url).rsplit("/", 1)[-1]

                        file_path = os.path.join(library_path + audio_name + ".mp3")

                        with open(file_path, 'wb') as f:
                            f.write(mp3)

                    except requests.exceptions.HTTPError as errh:
                        print("Http Error:", errh)
                    except requests.exceptions.ConnectionError as errc:
                        print("Error Connecting:", errc)
                    except requests.exceptions.Timeout as errt:
                        print("Timeout Error:", errt)
                    except requests.exceptions.RequestException as err:
                        print("OOps: Something Else", err)



                    channel = Channel(audio_name, io.BytesIO(mp3), random_counter, random_unit, balance,
                                      volume, mute, not is_random, False, False, loop_gap)
                    return channel



        new_urls = [new_url for new_url in ElementTree.parse(url).iter() if new_url.tag.startswith('channel')]
        # print("new")
        # pprint(new_urls)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            channels = [channel for channel in executor.map(import_channel, new_urls) if
                        channel is not None]


        # channels = [ import_channel(url) for url in new_urls]
        # channels = [channel for channel in channels if channel is not None]

        preset = self.make_scene_preset(channels)


        return Scene(scene_name, channels, preset, scene_name), channels

    def make_scene_preset(self, channels):
        """ """
        # TODO Rename channel.preset to channel.fields or channel.values

        return {channel.name: channel.channel_fields() for channel in channels}

    def audio_file_downloader(self):
        pass

    def segment_processer(self, mp3):
        # Segment
        segment = AudioSegment.from_file(io.BytesIO(mp3), format='mp3', frame_rate=48000,
                                              parameters=["-vol", str(1)])

        fade_in_amount = fade_out_amount = 20

        # chunk larger segments for smaller ffmpeg subprocesses to prevent playback starvation
        if segment.duration_seconds > 45:
            sliced_chunks = segment[::45001]
            segment = None  # AudioSegment.empty()
            current_chunk = next(sliced_chunks, None)
            while True:
                next_chunk = next(sliced_chunks, None)
                if not segment:  # First chunk
                    segment = current_chunk.set_frame_rate(48000).fade_in(fade_in_amount)
                elif next_chunk:  # In between chunks
                    segment += current_chunk.set_frame_rate(48000)
                else:  # Last chunk
                    segment += current_chunk.set_frame_rate(48000).fade_out(fade_out_amount)
                    break
                current_chunk = next_chunk
        else:
            segment.set_frame_rate(48000).fade_in(fade_in_amount).fade_out(fade_out_amount)

        return segment


    def import_ambient(self, url):
        pass

    def import_sndup(self, urls):
        pass

    def export_sndup(self, scene):
        pass

    def save_scene_as(self, scene, path):
        pass

    def save_scene(self, scene):
        pass

    def load_scene(self, path):
        pass

    def save_collection_as(self, scenes, path):
        pass


class AudioSource:
    """
        Basic audio source from url or file.

        Attributes
        ----------
        file_path : str

        mp3 : bytes
            bytes representation of mp3

    """

    def __init__(self, url=None, file=None, name="audio file"):

        # TODO: Assert filetype and do conversion if needed.
        # MP3 only
        self.file_path = file

        if not file:
            try:
                self.mp3 = requests.get(url)
            except requests.exceptions.HTTPError as errh:
                print("Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                print("OOps: Something Else", err)

            # Save to temp location
            self.mp3 = requests.get(url).content
            self.file_path = str(pathlib.Path(__file__).parent.parent.absolute()) + "/temp_files/" + name
            with open(self.file_path, 'wb') as f:
                f.write(self.mp3)
        # TODO: Send mp3 to garbage collector if not needed

    def copy(self, new_path):
        shutil.copy(self.file_path, new_path)

    def save_as(self, new_path, audio_segment: AudioSegment):
        audio_segment.export(new_path, format="mp3")
        # TODO: if in temp_files delete old file

        # if self.file_path in temp_files
        # delete file
        self.file_path = new_path

    def save(self, audio_segment):
        audio_segment.export(self.file_path, format="mp3")


