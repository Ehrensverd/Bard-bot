import threading
import time
from collections import deque

import pyaudio
from pydub import AudioSegment


class DiscordPlayback(object):
    def __init__(self, slices):
        self.slices = slices
    pass




class Monitor:

    def __init__(self, main_mix=None, size=4):

        self.main_mix = main_mix
        self.source = main_mix.main_segmenter
        self.size = size
        self.deque = deque(maxlen=self.size)
        self.silent_segment_read = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)
        self.silent_segment_fill = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

        self.x = threading.Thread(target=self.fill)
        time.sleep(0.3)
        self.y = threading.Thread(target=self.read)
        self.x.start()
        time.sleep(0.5)
        self.y.start()

        print("M O N I TO R INIT")

    def add_source(self, source):
        self.source = source.main_segmenter
        self.deque.appendleft(next(self.source))



    def fill(self):

        while True:

            if len(self.deque) < self.size:

                try:

                    self.deque.appendleft(next(self.source))

                except StopIteration:
                    self.deque.appendleft(self.silent_segment_fill)



            else:
                time.sleep(0.005)
                pass

            if not self.deque:
                print("fill done?")


    def read(self):
        if self.source is None:
            print("NOPE")
            return b""

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(self.silent_segment_fill.sample_width),
                        frames_per_buffer=int(self.silent_segment_fill.frame_count()),
                        channels=self.silent_segment_fill.channels,
                        rate=self.silent_segment_fill.frame_rate,
                        output=True)

        while True:

            if len(self.deque) == 0:

                try:

                    data = next(self.main_mix.main_segmenter)
                except StopIteration:
                    data = self.silent_segment_read
            else:
                data = self.deque.pop()
            #next(self.source)
            stream.write(data.raw_data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        print("read done")





