import io
import pathlib

from pydub import utils, AudioSegment
import requests
import shutil

"""
This class handles audio importing from url or disk.
If AudioSource from url then its stored temporarily such it can be Saved later.
"""


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

