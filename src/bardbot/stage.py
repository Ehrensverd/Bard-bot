"""
A stage is a collection of Scenes that share  at least 1 channel.
A channel can only be handled by 1 scene at a time.
A stage can have multiple scenes.

Reason for stage is so one can easily find related soundscapes and
be able to seemlessly transition between them.
Tavern - Busy.
becomes
Tavern - Brawl
With a scene change, channels are gradually shifted towards their new values.

When a stage is loaded into a group its scenes are also loaded and readied
Stage yields from active scene to main_mix

Stage has all channels in two collection, active and non active
on scene change channel collections are updated.

"""
import io
import random
from urllib.request import urlopen
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment

from bardbot.AudioMixer.audio_source import AudioSource



# Utility

def load_stage_scene(self, file_path):
    pass

# TODO: make possible to only import subset of channels
def import_stage(self, url):
    """Parse channels from XML file

    Returns a dicitionary {channel# : channel instance }

    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    temnplate_id = soup.select_one("a[href*=vote]")['href'].rpartition('/')[2]
    url = 'https://xml.ambient-mixer.com/audio-template?player=html5&id_template=' + str(temnplate_id)

    url = urlopen(url)
    channels = {}
    num = 1
    for item in ElementTree.parse(url).iter():

        if item.tag.startswith('channel'):
            if item.findtext('id_audio') == '0':
                continue
            else:
                audio_id = int(item.findtext('id_audio'))
                audio_name = item.findtext('name_audio')
                mp3_url = item.findtext('url_audio')
                mute = (item.findtext('mute') == 'true')
                volume = int(item.findtext('volume'))
                balance = int(item.findtext('balance'))
                is_random = (item.findtext('random') == 'true')
                random_counter = int(item.findtext('random_counter'))
                random_unit = item.findtext('random_unit')
                cross_fade = (item.findtext('crossfade') == 'true')
                audio_source = AudioSource(url=mp3_url)

                # TODO: check if is_active can be deactivated in ambient-mixer while not random, and if it creates issues.
                channels['channel' + str(num)] = Channel(audio_name, audio_source, random_counter, random_unit, balance,
                                                         volume, mute, cross_fade, is_random, not is_random)

    return channels


class Stage:
    """Base audio template for soundscapes

    Attributes
    ----------
    stage_volume : int
        main volume for stage

    scenes : dict { scene_name : scene_presets{}}
        collection of loaded scenes.
        each scene is a different preset for the stage.
     channel_presets : dict { channel instance : channel_preset{} }
        collection of scene channels and corresponding presets
    channel_preset : dict { volume : int,
                            balance : int,
                            is_random : bool,
                                indicate randomly triggered segment
                            random_rate : int,
                            random_unit : int,
                            is_crossfade : boolean,
                                - only non randomly triggered segments are cross faded
                            crossfade_amount : int
                            }
        channel preset

    channels : dict { channel_name : channel instance }
        collection of channels.
        channel behavior depends on the active scene

    active_scene : scene preset
        scene from which stage segmenter get channel settings

    new_actve_scene

    stage_segmenter()
        Yields 20ms of mixed audio from all active channels

    ms, sec, min : int
        Providing time mapping for scene generator.

    Methods
    -------

        """

    def __init__(self, channels, scenes, active_scene):

        self.channels = channels
        self.paused_channels = {}
        self.scenes = scenes
        self.active_scene = active_scene


        self.ms = self.sec = self.min = self.hour = 0
        self.segmenter = self.scene_generator()
        self.scene_volume = 50
        self.stage_playing = True

    def pause_channel(self, channel):
        self.paused_channels[channel] = self.channels.pop(channel)

    def unpause_channel(self, channel):
        self.channels[channel] = self.paused_channels.pop(channel)

    def scene_generator(self):
        """Generates 20ms worth of opus encoded raw bytes
        Checks if scheduled segments, and sets to active when needed

        Overlays all active segments
        """

        while True:
            # time schedule
            self.ms += 20
            if self.ms >= 1000:
                self.ms = 0
                self.sec += 1
                if self.sec >= 60:
                    self.sec = 0
                    self.min += 1
                    # Resets depleted random channels  at corresponding 1 min, 10 min and 1 hour mark
                    for channel in self.channels.values():
                        if channel.depleted and channel.random_unit == 1:
                            channel.depleted = False
                        if self.min == 10 and channel.random_unit == 10:
                            channel.depleted = False
                    if self.min >= 60:
                        for channel in self.channels.values():
                            if channel.depleted and channel.random_unit == 3600:
                                channel.depleted = False
                        self.min = 0
            #empty base
            segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

            #
            if self.stage_playing:
                for channel in self.channels.values():
                    if not channel.is_active:
                        if channel.next_play_time <= self.sec + (self.min * 60) and not channel.depleted:
                            print(channel.name, "now playing. Time:", self.sec + (self.min * 60))
                            channel.is_active = True
                            channel.seg_gen = channel.segment_generator()
                    if channel.is_active:
                        try:
                            segment = segment.overlay(next(channel.seg_gen))
                        except StopIteration:
                            print(channel.name, "finished playing")
                            continue
            yield segment


    def change_scene(self, new_scene):
        pass

    def add_scene(self):
        pass

    def remove_scene(self):
        pass


    def defualt_preset(self):
        preset = {"is_channel_active": False,
                  "volume": 50,
                  "balance": 0,
                  "is_random": False,
                  "random_rate": 0,
                  "random_unit": 1,
                  "is_crossfade": False,
                  "crossfade_amount": 100
                  }
        return preset




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
            self.initial, self.crossfaded = self.crossfader()

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

        if self.crossfade and not self.is_random:
            slices = self.crossfaded[::20]
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
    def __init__(self, name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                 is_crossfaded=False, is_random=False, is_active=False, is_global_distinct=False):
        super().__init__(name, audio_source, random_amount, time_unit, balance=0, volume=50, is_muted=False,
                         is_crossfaded=False, is_random=False, is_active=False, is_gloabl_distinct=False)

        # dict { "name" : (pydub.AudioSegment, AudioSource) }
        self.playlist = {}

    def shuffle(self):
        pass

    def add_song(self, song):
        pass

    def remove_song(self, song):
        pass
