import io
import os

from pydub import utils, AudioSegment
import requests
import shutil

"""
This class handles audio importing from url or disk.
If AudioSource from url then its stored temporarily such it can be Saved later.


"""
class BasicAudioSource:

    def __init__(self, volume=50, balance=50, url=None, file=None):

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


            self.mp3 = requests.get(url).content
            #TODO: Make to pydub.AudioSegment and export.
            self.file_path = "/home/eskil/PycharmProjects/Bard-bot/src/bardbot/temp_files/" + url.rsplit('/', 1)[-1]
            with open(self.file_path, 'wb') as f:
                f.write(self.mp3)

        #make segment
        self.pydub_segment = AudioSegment.from_file(self.file_path, format='mp3', frame_rate=48000,
                                                  parameters=["-vol", str(volume)]).set_frame_rate(48000).pan(
                balance / 50).fade_in(50).fade_out(20)
        print(self.pydub_segment)


    def copy(self, new_path):
        new_path = shutil.copy(self.file_path, new_path)

    def save_as(self, new_path):
        #TODO: change to pydub.Audiosegment export()
        # TODO: if in temp_files delete old file
        with open(new_path, 'wb') as f:
            f.write(self.mp3)

    def save(self):
        # TODO: change to pydub.Audiosegment export()
        with open(self.file_path, 'wb') as f:
            f.write(self.mp3)

    def load(self, path):
        pass





test = BasicAudioSource(url="https://xml.ambient-mixer.com/audio/9/a/8/9a83a6a96fd76692cc1556ee13e01b04.mp3")