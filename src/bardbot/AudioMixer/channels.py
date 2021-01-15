import io
import random
import time

from pydub import AudioSegment


class Channel:
    """
    Base Audio channel.
    Handles yielding to stage.
    Instructed by active scene.
    Segmenter can smoothly transition between scenes, keeping track of segment postion.

    make segmenter that takes next 20 ms slice from scene_segment[::20] but
    keeps track of position.

    Attributes
    ----------
    name : string
        channel name / filename

    audio_source : AudioSource
        from file or url
        file_path   : string
        mp3         : bytes

    audio_segment : pydub.AudioSegment

    volume : int
        range: 0-100

    balance : int
        range: -50 - 50

    is_muted : bool
        volume = 0

    is_playing : bool
        is being currently played.
        Either between random plays or if paused.

    is_random : bool
        indicates channel is played at a random interval
        thus needs random_rate ratio amount / time_unit
        randomed channels cannot be crossfaded

    random_traits : dict {    amount : int
                           time_unit : int seconds
                                amount / time_unit
                                5 times over 10 minutes period

                           depleted : bool
                                this indicates that channel has
                                no more play events for current
                                time unit iteration and therefore waits
                            }

    is_looped : bool
        activates crossfader()
        adds a smooth volume curve to start and end of segment
        that also contains overlayed audio from opposite end.
        creates a smooth loop feel

    is_global_distinct : bool
        if this channel is playing, then no other
        global_distinct channel is playing.
        For playlists channels and other channels that
        shouldn not be mixed.
        e.g. Tavern band playlist and battle playlist
        TODO make into groups of distinct channels

    channel_segmenter()
        uses presets in scene channel_preset
        makes 20ms slices and yield to stage generator
        updates channel position
        changing scene, smoothly change volume to fit destination scene
        make and sync new 20ms generator
        once match in volume and position. Swap

    """

    def __init__(self, name, audio_source, random_amount, random_time_unit, balance=0, volume=50, is_muted=False,
                 is_looped=False, is_random=False, is_playing=False, is_global_distinct=False, space=0, loops=0):
        # TODO: is name needed? Since Channels are dict { channel_name : channel_instance }

        self.name = name
        self.audio_source = audio_source
        self.volume = volume
        self.balance = balance
        self.is_muted = is_muted
        # TODO check if vol needs to be set vol 0 if muted, here or if scene generator handels

        self.segment = AudioSegment.from_file(io.BytesIO(self.audio_source.mp3), format='mp3', frame_rate=48000,
                                              parameters=["-vol", str(volume + 6)])
        self.fade_in_amount = 60
        self.fade_out_amount = self.fade_in_amount
        self.pause_offset = 0
        self.separation_space = space
        self.loops = loops
        print(self.name, "\nDuration:", self.segment.duration_seconds)
        print()

        if self.segment.duration_seconds > 15:
            sliced_chunks = self.segment[::15001]
            self.segment = None  # AudioSegment.empty()
            current_chunk = next(sliced_chunks, None)
            print(self.name, "\nDuration:", current_chunk.duration_seconds)
            while True:

                next_chunk = next(sliced_chunks, None)
                if not self.segment:
                    # First chunk
                    # print(self.name, "\nFirst Duration:", current_chunk.duration_seconds)
                    self.segment = current_chunk.set_frame_rate(48000).fade_in(self.fade_in_amount)
                elif next_chunk:
                    # print(self.name, "\n betweenDuration:", current_chunk.duration_seconds)
                    # In between
                    self.segment += current_chunk.set_frame_rate(48000)
                else:
                    # Last
                    # print(self.name, "\n Last Duration:", current_chunk.duration_seconds)
                    self.segment += current_chunk.set_frame_rate(48000).fade_out(self.fade_out_amount)
                    break
                current_chunk = next_chunk

        else:

            self.segment.set_frame_rate(48000).fade_in(self.fade_in_amount).fade_out(self.fade_out_amount)

        self.is_playing = is_playing
        self.is_random = is_random
        if random_time_unit[-1] in 'h':
            self.random_time_unit = 3600
        else:
            self.random_time_unit = (int(random_time_unit[:-1]) * 60)

        self.random_amount = random_amount

        if self.is_random:
            # TODO: What happens if next time is immediate
            self.is_playing = not is_random
            # Make schedule generator
            self.schedule = self.random_seg_scheduler()
            self.next_play_time = next(self.schedule)
        else:
            self.is_playing = True

        self.is_triggered = False
        self.is_looped = is_looped
        if self.is_looped:
            self.initial, self.crossfaded_segment = self.crossfader()

        self.is_global_distinct = is_global_distinct
        self.seg_gen = self.segment_generator()
        # Might ber redundant, but might be useful for changed channels
        self.preset_fields = self.channel_fields()

    def channel_fields(self):
        fields = {"channel_name": self.name,
                  "volume": self.volume,
                  "balance": self.balance,
                  "is_muted": self.is_muted,
                  "is_playing": self.is_playing,
                  "is_random": self.is_random,
                  "random_time_unit": self.random_time_unit,
                  "random_amount": self.random_amount,
                  "is_looped": self.is_looped,
                  "is_global_distinct": self.is_global_distinct
                  }
        return fields

    def crossfader(self):
        """Generate initial crossfaded segment and loopable crossfaded segment"""
        # end crossfaded
        initial = self.segment.append(self.segment[:300], crossfade=150)
        initial = initial[:len(self.segment)].fade_in(20).fade_out(20)

        # Start and end crossfaded
        crossfaded = self.segment[-300:].append(initial, crossfade=150)
        crossfaded = crossfaded[-len(self.segment):].fade_in(20).fade_out(20)
        return initial[::20], crossfaded

    def segment_generator(self):
        """Generate 20 ms AudioSegments.
        Checks wheter channel is continiously looping or is a random segment

        Once a random segment is depleted its set to not active and
        generator ends
        """
        if self.is_looped:
            schedule = self.loop_scheduler()
            if self.separation_space < 0:
                yield from self.initial
        else:
            schedule = self.random_seg_scheduler()

        while True:
            if self.is_looped and self.separation_space < 0:
                slices = self.crossfaded_segment[::20]
            else:
                slices = self.segment[::20]

            if not self.is_triggered:
                self.next_play_time = next(schedule)
            else:
                self.is_triggered = False
            yield from slices




    def loop_scheduler(self, scene_time_offset=0):
        # initial loop setup
        loop_duration = self.segment.duration_seconds + self.separation_space
        remaining_loops = self.loops
        self.pause_offset = 0
        self.next_play_time = scene_time_offset
        remaining_loops -= 1
        yield self.next_play_time

        while remaining_loops > 0:
            self.next_play_time = loop_duration + self.next_play_time
            remaining_loops -= 1
            yield self.next_play_time + self.pause_offset

        if remaining_loops == 0:
            self.next_play_time = float("inf")

    def random_seg_scheduler(self, scene_time_offset=0):
        """Generate infinite number random start times.

        Segments will not overlap, ie- next start time will be after current segment is finished playing.
        Last segment will finish before next period starts
        """
        iterations = 0
        segment_length = int(self.segment.duration_seconds * 1000)
        time_period = self.random_time_unit * 1000

        while True:
            # Generate randomly spaced play times
            regulated_intervals = enumerate(
                sorted(random.sample(range(time_period - segment_length * self.random_amount), self.random_amount)))
            start_times = (segment_length * playtime + interval for playtime, interval in regulated_intervals)
            while True:
                try:
                    next_play_time = next(start_times) / 1000
                    yield next_play_time + (iterations * self.random_time_unit) + scene_time_offset + self.pause_offset
                except StopIteration:
                    print('Segment ', self.name, ' schedule depleted')
                    break
            iterations += 1

    def transition_segmenter(self):
        pass


class Playlist(Channel):
    """A channel that can have multiple audio files control """

    def __init__(self, name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                 is_looped=False, is_random=False, is_playing=False, is_global_distinct=False):
        super().__init__(name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                         is_looped=False, is_random=False, is_playing=False, is_gloabl_distinct=False)

        # dict { "name" : (pydub.AudioSegment, AudioSource) }
        self.playlist = {}

    def shuffle(self):
        pass

    def next_song(self):
        pass

    def previous_song(self):
        pass

    def add_song(self, song):
        pass

    def remove_song(self, song):
        pass
