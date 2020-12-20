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

    """
        Basic audio source from url or file.


        Attributes
        ----------
        volume : int
            main volume for stage

        scenes : dict { scene_name : scene instance }
            collection of loaded scenes.
            each scene is a different preset for the stage.

        channels : dict { channel_name : channel instance }
            collection of channels.
            channel behavior depends on the active scene
    """
    def __init__(self, url=None, file=None):

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

            self.file_path = "/home/eskil/PycharmProjects/Bard-bot/src/bardbot/temp_files/" + url.rsplit('/', 1)[-1]
            with open(self.file_path, 'wb') as f:
                f.write(self.mp3)




    def copy(self, new_path):
        new_path = shutil.copy(self.file_path, new_path)

    def save_as(self, new_path):

        # TODO: if in temp_files delete old file
        with open(new_path, 'wb') as f:
            f.write(self.mp3)

    def save(self):
        # TODO: change to pydub.Audiosegment export()
        with open(self.file_path, 'wb') as f:
            f.write(self.mp3)







#test = BasicAudioSource(url="https://xml.ambient-mixer.com/audio/9/a/8/9a83a6a96fd76692cc1556ee13e01b04.mp3")