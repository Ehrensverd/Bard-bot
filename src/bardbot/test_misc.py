import random

from pydub import AudioSegment
from pydub.playback import play

from bardbot.scene import Scene

mix = Scene('https://movies-other.ambient-mixer.com/mr--tumnus--house')


seg = AudioSegment.empty()

for _ in range(0, 2000):
    seg1 = next(mix.gen)
    seg = seg+seg1


print('done')

play(seg)
