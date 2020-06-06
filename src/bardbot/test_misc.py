import random
import urllib
from io import BytesIO

from pydub import AudioSegment
from pydub.playback import play

from bardbot.scene import Scene

import requests
import io
from pydub import AudioSegment



def test_download_AudioSeg():
    external_audio = requests.get("https://xml.ambient-mixer.com/audio/1/3/0/130739e1e14f93b44daf7cfaa462b52a.mp3")
    au = io.BytesIO(external_audio.content)
    audio_segment = AudioSegment.from_file(au, format='mp3')
    play(audio_segment)

def test_mixer(input):
    mix = Scene(input)
    seg = AudioSegment.empty()

    for _ in range(0, 3000):
        seg1 = next(mix.gen)
        seg = seg+seg1

    seg = seg +5
    print('done')
    play(seg)


test_mixer(input("Ambient mixer url: "))

# https://rpg.ambient-mixer.com/d-d-fantasy-inn-pub-tavern
# https://countryside.ambient-mixer.com/scottish-rain
# https://relaxing.ambient-mixer.com/deep-space-explorer--sleep-


# https://harry-potter-sounds.ambient-mixer.com/storm-on-the-hogwarts-express
#