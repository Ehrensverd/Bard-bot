import io
import random

import requests
from pydub import AudioSegment


class Channel:
    def __init__(self, name, audio_id, url, mute, volume, balance, is_random, random_count, random_unit, is_crossfade):
        self.crossfade = is_crossfade

        if random_unit[-1] in 'h':
            self.random_unit = 3600
        else:
            self.random_unit = (int(random_unit[:-1]) * 60)

        self.random_count = int(random_count)
        self.is_random = is_random
        self.is_active = not is_random
        self.balance = balance
        self.volume = volume
        self.mute = mute
        self.url = url
        self.audio_id = audio_id
        self.name = name
        print('Getting segment: ', self.name)
        mp3 = requests.get(url)
        self.segment = AudioSegment.from_file(io.BytesIO(mp3.content), format='mp3', frame_rate=48000,
                                              parameters=["-vol", str(volume)]).set_frame_rate(48000).pan(balance / 50).fade_in(50).fade_out(20)
        self.depleted = False
        if is_random:
            self.schedule = self.random_seg_scheduler()
            self.next_play_time = next(self.schedule)
        if is_crossfade:
            self.initial, self.crossfaded = self.crossfader()

        self.seg_gen = self.segment_generator()

    def crossfader(self):
        """Generate initial crossfaded segment and loopable crossfaded segment"""
        # end crossfaded
        initial = self.segment.append(self.segment[:300], crossfade=150)

        initial = initial[:len(self.segment)].fade_in(20).fade_out(20)
        print("initial framerate2:",initial.frame_rate)
        # Start and end crossfaded
        crossfaded = self.segment[-300:].append(initial, crossfade=150)

        crossfaded = crossfaded[-len(self.segment):].fade_in(20).fade_out(20)
        print("crossfade framerate", crossfaded.frame_rate)
        return initial[::20], crossfaded

    def segment_generator(self):
        """Generate 20 ms AudioSegments.
        Checks wheter channel is continiously looping or is a random segment

        Once a random segment is depleted its set to not active and
        generator ends
        """

        if self.crossfade and not self.is_random:
            slices = self.crossfaded[::20]
            while True:
                try:
                    yield next(self.initial)
                except StopIteration:
                    break
        else:
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
                    if self.crossfade:
                        slices = self.crossfaded[::20]
                    else:
                        slices = self.segment[::20]
                    continue

    def random_seg_scheduler(self):
        """Generate infinite number random start times.

        Segments will not overlap, ie- next start time will be after current segment is finished playing.
        Last segment will finish before next period starts
        """

        segment_length = int(self.segment.duration_seconds * 1000)
        period = self.random_unit * 1000
        rate = self.random_count
        print("Schedule stats  for: ", self.name, "Segment length: ", segment_length/1000, "random unit: ", period, "random rate: ", rate )

        start_times = ((segment_length - 1000) * i + x for i, x in
                       enumerate(sorted(random.sample(range(period - (segment_length - 1000) * rate), rate))))
        start_times = list(start_times)
        print("Start times: ", start_times, "for channel ", self.name)
        start_times = (time for time in start_times)

        while True:
            try:
                time = next(start_times) // 1000
                yield time
            except StopIteration:
                print('Segment ', self.name, ' schedule depleted')
                print("Schedule stats  for: ", self.name, "Segment length: ", segment_length / 1000, "random unit: ",
                      period, "random rate: ", rate)

                start_times = ((segment_length - 1000) * i + x for i, x in
                               enumerate(sorted(random.sample(range(period - (segment_length - 1000) * rate), rate))))
                start_times = list(start_times)
                print("Start times: ", start_times, "for channel ", self.name)
                start_times = (time for time in start_times)
                self.depleted = True
                continue
