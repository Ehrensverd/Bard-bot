import os
import random
from urllib.request import urlretrieve

from pydub import AudioSegment


class Channel:
    def __init__(self, name, audio_id, url, mute, volume, balance, random, random_count, random_unit, crossfade):
        self.crossfade = crossfade

        if random_unit[-1] in 'h':
            self.random_unit = 60*60
        else:
            self.random_unit = (int(random_unit[:-1])*60)

        self.random_count = int(random_count)
        self.is_random = random
        self.is_active = not random
        self.balance = balance
        self.volume = volume
        self.mute = mute
        self.url = url
        self.audio_id = audio_id
        self.name = name
        self.filename = '/home/eskil/PycharmProjects/Discord/AmbientBot/mp3/' + url.rpartition('/')[2]
        if not os.path.isfile(self.filename):
            urlretrieve(self.url, self.filename)

        print('Getting segment ', self.name)
        self.segment = AudioSegment.from_file(self.filename, frame_rate=48000, sample_width=1).export('-', format='ogg', codec='libopus')
        #'/home/eskil/PycharmProjects/Discord/AmbientBot/mp3/temp.ogg
        self.segment = AudioSegment.from_file(self.segment.raw, format='ogg', codec='libopus')

        #,  frame_rate=48000, sample_width=2 ,codec='libopus
        self.cutoff = 0
        self.schedule = self.random_seg_scheduler()
        self.next_play_time = next(self.schedule)
        self.seg_gen = self.segment_generator()
        # for field in self.__dict__.items():
        #     print(field[0], ' = ' , field[1])
        #
        # print('segment length = ',     self.segment.duration_seconds)
        # print()

    def segment_generator(self):
        """Generate 20 ms AudioSegments.
        Checks wheter channel is continiously looping or is a random segment

        Once a random segment is depleted its set to not active and
        generator ends
        """
        slices = self.segment[::20]
        while True:
            try:
                yield next(slices)
            except StopIteration:
                if self.is_random:
                    self.is_active = False
                    self.next_play_time = next(self.schedule)
                    return
                else:
                    slices = self.segment[::20]
                    continue

    def random_seg_scheduler(self):
        """Generate infinite number random start times.

        Segments will not overlap, ie- next start time will be after current segment is finished playing.
        Last segment will finish before next period starts
        """

        segment_length = int(self.segment.duration_seconds*1000)
        period = self.random_unit*1000
        rate = self.random_count
        print(self.name)
        print('Rate:', rate)
        print('period:', period//1000)
        print('seglength:', segment_length/1000)

        start_times = ((segment_length - 1000) * i + x for i, x in
                       enumerate(sorted(random.sample(range(period - (segment_length - 1000) * rate), rate))))
        while True:
            try:
                time = next(start_times)//1000
                print('VERY IMPORTANT TIM: ',time)
                print()
                yield time
            except StopIteration:
                print('Segment ', self.name, ' schedule depleted')
                start_times = ((segment_length - 1000) * i + x for i, x in
                               enumerate(sorted(random.sample(range(period - (segment_length - 1000) * rate), rate))))
                continue

