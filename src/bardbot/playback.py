import threading
import time
from collections import deque

import discord
import pyaudio
from discord.ext import tasks
from pydub import AudioSegment


class DiscordPlayback(discord.AudioSource):

    def __init__(self,  main_mix, size=200,):

        self.source = main_mix.main_segmenter
        self.is_active = False
        self.deque = None
        self.size = size
        self.silent_slice = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)
        self.deque = deque(maxlen=self.size)
        self.deque.append(next(self.source))





    @tasks.loop(seconds=0.01)
    async def fill(self):
        if self.source is None:
            print("NOPE")
            return

        if len(self.deque) < self.size:
            try:
                if self.is_active:
                    segment = next(self.source)
                    self.deque.append(segment)
                else:
                    self.deque.append( self.silent_slice)
            except StopIteration:
                print(self)
                print("source depleted")

    def read(self):
        if self.source is None:
            print("source is None")
            return  self.silent_slice.raw_data
        try:
            if self.is_active:
                return self.deque.pop().raw_data
            else:
                return self.silent_slice.raw_data
        except IndexError:
            print("discord Playback index error ")
            return  self.silent_slice.raw_data

    def cleanup(self):
        print("Stopping deque filling")
        self.fill.stop()


class Monitor:

    def __init__(self, main_mix=None, size=4):
        self.is_active = True
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
                    if self.is_active:
                        self.deque.appendleft(next(self.source))
                    else:
                        self.deque.appendleft(self.silent_segment_fill)
                except StopIteration:
                    self.deque.appendleft(self.silent_segment_fill)
                    print("stop itration")


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

                    data = self.silent_segment_read
                except StopIteration:
                    print("read stop itration")
                    data = self.silent_segment_read
            else:
                if self.is_active:
                    data = self.deque.pop()
                else:
                    data = self.silent_segment_read

            #next(self.source)
            stream.write(data.raw_data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        print("read done")





