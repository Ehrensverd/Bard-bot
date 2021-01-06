"""
takes all collections streams and gives to discord bot buffer

"""
import threading
import time
from collections import deque

import pyaudio
from pydub import AudioSegment


class MainMixer:
    def __init__(self, sources=None):
        self.sources = sources
        if self.sources is None:
            self.playing = False
        else:
            self.playing = True

        self.main_segmenter = self.segment_generator()



    def segment_generator(self):
        segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

        #
        if self.playing:

            for source in self.sources:
                # only active channels are yielded from

                if source.is_playing:
                    try:
                        segment = segment.overlay(next(source.segmenter))
                    except StopIteration:
                        print(source.name, "finished playing")
                        continue
        yield segment

    def add_source(self, source):
        if source not in self.sources:
            self.sources.append(source)


class Monitor:
    def __init__(self, main_mix=None, size=15):

        self.source = main_mix
        self.size = size
        self.deque = deque(maxlen=self.size)

        self.x = threading.Thread(target=self.fill)
        self.y = threading.Thread(target=self.read)
        self.x.start()
        self.y.start()

    def add_source(self, source):
        self.source = source
        self.deque.appendleft(next(self.source))

    def fill(self):
        silent_segment = AudioSegment.silent(20, 48000)
        while True:

            if len(self.deque) < 15:
                try:
                    deque.appendleft(next(self.source))
                except StopIteration:
                    deque.appendleft(silent_segment.raw_data)
                    time.sleep(0.01)

            else:
                time.sleep(0.01)
            if not deque:
                print("fill done?")
                return

    def read(self):
        if self.source is None:
            print("NOPE")
            return b""

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.source.sample_width),
                        channels=self.source.channels,
                        rate=self.source.frame_rate,
                        output=True)
        try:
            while deque:

                data = deque.pop()
                stream.write(data)

            stream.stop_stream()
            stream.close()
            p.terminate()
            print("read done")
        except IndexError:
            print("Playback done")




