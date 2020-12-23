import io
import random

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

    is_active : bool
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

    is_crossfaded : bool
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

    def __init__(self, name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                 is_crossfaded=False, is_random=False, is_active=False, is_global_distinct=False):
        self.name = name
        self.audio_source = audio_source
        self.balance = balance
        self.volume = volume
        self.segment = AudioSegment.from_file(io.BytesIO(self.audio_source.mp3), format='mp3', frame_rate=48000,
                                              parameters=["-vol", str(volume)]).set_frame_rate(48000).pan(
            balance / 50).fade_in(50).fade_out(20)

        self.is_active = is_active
        self.is_random = is_random
        self.random_unit = time_unit
        self.random_count = random_amount

        if self.is_random:
            # TODO: What happens if next time is immediate
            self.is_active = not is_random
            # Make schedule generator
            self.schedule = self.random_seg_scheduler()
            self.next_play_time = next(self.schedule)

        if is_crossfaded:
            self.initial, self.crossfaded_segment = self.crossfader()

        self.seg_gen = self.segment_generator()

        self.is_global_distinct = is_global_distinct
        self.is_muted = is_muted

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

        if self.crossfaded_segment and not self.is_random:
            slices = self.crossfaded_segment[::20]
            # initial loop
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
                    if self.crossfaded_segment:
                        slices = self.crossfaded_segment[::20]
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

        start_times = ((segment_length - 1000) * i + x for i, x in
                       enumerate(sorted(random.sample(range(period - (segment_length - 1000) * rate), rate))))

        while True:
            try:
                time = next(start_times) // 1000
                yield time
            except StopIteration:
                print('Segment ', self.name, ' schedule depleted')

                start_times = ((segment_length - 1000) * i + x for i, x in
                               enumerate(sorted(random.sample(range(period - (segment_length - 1000) * rate), rate))))
                self.depleted = True
                continue

    def transition_segmenter(self):
        pass


class Playlist(Channel):
    """A channel that can have multiple audio files control """
    def __init__(self, name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                 is_crossfaded=False, is_random=False, is_active=False, is_global_distinct=False):
        super().__init__(name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                         is_crossfaded=False, is_random=False, is_active=False, is_gloabl_distinct=False)

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
