"""
takes all collections streams and gives to discord bot buffer

"""
import threading
import time
from collections import deque
from multiprocessing.context import Process
from pprint import pprint

import pyaudio
from pydub import AudioSegment


class MainMixer:
    def __init__(self, sources=None):

        self.sources = sources
        if sources is None:
            self.sources = []

        if self.sources is None:
            self.playing = True
        else:
            self.playing = True

        self.source_added = False
        self.main_segmenter = self.segment_generator()
        print()
    def segment_generator(self):

        while True:
            segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

            if self.playing:


                for source in self.sources:
                    # only active channels are yielded from
                    if source.scene_playing:
                        try:

                            segment = segment.overlay(next(source.segmenter))
                        except StopIteration:
                            print(source.name, "finished playing")
                            continue
                #print("yielding to queue")
            yield segment

    def add_source(self, source):
        self.source_added = True
        print("adding source to mixer")
        sources = []
        if source not in self.sources:
            for s in self.sources:
                sources.append(s)
            sources.append(source)

        self.sources = sources
        self.source_added = False


class Monitor:
    def __init__(self, main_mix=None, size=50):

        self.main_mix = main_mix
        self.source = main_mix.main_segmenter
        self.size = size
        self.deque = deque(maxlen=self.size)
        self.silent_segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

        self.x = threading.Thread(target=self.fill)

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
                    self.deque.appendleft(self.silent_segment)



            else:
                time.sleep(0.01)
                pass

            if not self.deque:
                print("fill done?")
                return

    def read(self):
        if self.source is None:
            print("NOPE")
            return b""

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(self.silent_segment.sample_width),
                        frames_per_buffer=int(self.silent_segment.frame_count()),
                        channels=self.silent_segment.channels,
                        rate=self.silent_segment.frame_rate,
                        output=True)

        while True:
            if len(self.deque) == 0:
                print("empty queu")
                data = self.silent_segment
            else:
                data = self.deque.pop()
            #next(self.source)
            stream.write(data.raw_data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        print("read done")





