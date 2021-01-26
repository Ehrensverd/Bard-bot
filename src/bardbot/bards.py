import io
import os
import pathlib
import pickle
import random
import shutil
from os import path

import requests
from pydub import AudioSegment
from pydub.utils import ratio_to_db



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




def save_scene_as(scene, directory_path):
    # if file_path exist confirm overwrite
    if path.exists(directory_path):
        print("scene  exists, overwrite")
        # qt dialog
        return

    # save channels to file
    for channel in scene.channels:
        channel.audio_source.save_as(directory_path
                                     + scene.scene_name + channel.name + ".mp3", channel.segment)

    # save scene preset
    with open(directory_path + scene.scene_name + "presets.txt", 'wb') as f:
        pickle.dump(scene.presets, f, pickle.HIGHEST_PROTOCOL)


def load_scene(directory_path, active_preset):
    # TODO remove from stage class, make utility.
    print("Loading scene from path:", directory_path)
    with open(directory_path + "presets.txt", 'rb') as f:
        scenes = pickle.load(f)

    scene_name = os.path.basename(os.path.normpath(directory_path))
    print("Scene name:", scene_name)
    return Scene(scene_name, load_channels(directory_path + "/channels/", scenes[active_preset]), scenes, active_preset)


# TODO: make possible to only import subset of channels
def load_channels(directory_path, active_preset):
    """
    Returns dict { "channel_name" : channel_instance }


     """
    return {channel_name: Channel(channel_name, AudioSource(file=directory_path + channel_name),
                                  **active_preset[channel_name]) for channel_name in os.listdir(directory_path)}


def align_presets(channel, new_channel_preset, preset):
    changed = False
    if channel[preset] < new_channel_preset[preset]:
        channel[preset] += 1
        changed = True
    elif channel[preset] > new_channel_preset[preset]:
        new_channel_preset[preset] -= 1
        changed = True
    return changed


class Scene:
    """Base audio template for soundscapes

    Attributes
    ----------
    scene_volume : int
        main volume for stage

    presets : dict { preset_name : channel_presets{}}
        collection of loaded scenes.
        each scene is a different preset for the stage.
     channel_presets : dict { channel_name : channel_preset{} }
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

    active_preset : scene preset
        scene from which stage segmenter get channel settings

    new_actve_scene

    stage_segmenter()
        Yields 20ms of mixed audio from all active channels

    ms, sec, min : int
        Providing time mapping for scene generator.

    Methods
    -------

        """

    def __init__(self, scene_name, channels, presets=None, active_preset=None):

        self.scene_name = scene_name
        self.channels = channels
        self.paused_channels = {}

        self.active_preset = active_preset
        if presets is None:
            self.presets = self.default_presets()
            self.active_preset = "Preset 1"
        else:
            self.presets = presets


        self.changing_preset = False
        self.next_preset = None

        self.ms = self.sec = self.min = self.hour = 0

        self.segmenter = self.scene_generator()
        self.scene_volume = 50
        self.balance = 0
        self.scene_playing = True
        self.low_pass = False


    def pause_channel(self, channel):
        self.paused_channels[channel] = self.channels.pop(channel)

    def unpause_channel(self, channel):
        self.channels[channel] = self.paused_channels.pop(channel)

    def scene_generator(self):
        """Generates 20ms worth of opus encoded raw bytes and yields to main_mixer

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
                    if self.min >= 60:
                        self.min = 0
            # empty base
            segment = AudioSegment.silent(duration=20, frame_rate=48000).set_channels(2)

            if self.scene_playing:
                if self.changing_preset:
                    self.preset_changer()
                for channel in self.channels:

                    if channel.is_paused:
                        channel.pause_offset += 20

                    elif channel.is_triggered or channel.next_play_time <= self.sec + (self.min * 60):
                        try:

                            channel_segment = next(channel.seg_gen).apply_gain(ratio_to_db(channel.volume / 25))
                            segment = segment.overlay(channel_segment.pan(self.balance_panning(channel.balance)))
                        except StopIteration:
                            print(channel.name, "error yielding")  # consider reinitializing here if issues
                            continue

            yield segment.apply_gain(ratio_to_db(self.scene_volume / 25))

    def balance_panning(self, channel_balance):
        # Scale channel range, based on scene balance
        channel_min_range = (50 - self.balance) * -2 if self.balance > 0 else -100
        channel_max_range = (50 + self.balance) * 2 if self.balance < 0 else 100

        # def rescale(val, in_min, in_max, out_min, out_max):
        #     return out_min + (val - in_min) * ((out_max - out_min) / (in_max - in_min))
        # Apply rescaling, keep relative channel balance and calculate final pan value
        pan = channel_min_range + (channel_balance - -100) * ((channel_max_range - channel_min_range) / (100 - -100))

        return int(pan) / 100

    def preset_changer(self):
        """
        method called within stage generator
            shfiting values towards new scene
        """

        # 2 start shifting towards new values
        # if active in old and nonactive in new -> 0
        # else shift til matches new value
        changed = False
        # activated scenes
        for channel in self.channels.values():
            # if (preset["volume"]) == self.active_scene[channel]["volume"]:
            #     self.active_scene[channel]["volume"] -= (self.active_scene[channel]["volume"] - preset["volume"])/abs( self.active_scene[channel]["volume"] - preset["volume"])
            changed = align_presets(channel, "volume") or align_presets(channel, "balance")

        if not changed:
            # 3 when done, set old active to non active if non active in new.
            for channel in self.channels.values():
                channel.__dict__.update(**self.next_preset[channel.name])
                # channel.is_active = self.new_scene[channel.name]["is_active"]
                # channel.volume = self.new_scene[channel.name]["volume"]
                # channel.balance = self.new_scene[channel.name]["balance"]
                # channel.random_unit = self.new_scene[channel.name][""]
                # channel. = self.new_scene[channel.name][""]
                # channel. = self.new_scene[channel.name][""]
                # channel. = self.new_scene[channel.name][""]
            # if not self.new_scene.channel.is_active and channel.is_active:
            #         channel.is_active = False

            self.changing_preset = False

    def change_preset(self, next_preset=None):
        """initial scene change method. sets"""
        # 1 find active scenes that are non active in current
        # make active and set volume = 0
        if next_preset:
            self.next_preset = next_preset

        for channel, preset in self.next_preset.items():
            if (preset["is_active"]) and not self.active_preset[channel]["is_active"]:
                preset["volume"] = 0
                self.active_preset[channel]["is_active"] = True

        self.changing_preset = True

    def add_preset(self, preset, preset_name):
        # TODO: Assert scene is valid

        if preset not in self.presets:
            self.presets[preset_name] = preset

    def remove_preset(self, preset_name):
        if preset_name in self.presets:
            self.presets[preset_name].remove(preset_name)

    def default_presets(self):
        presets = {"default_preset": self.get_channel_presets()}
        return presets

    def get_channel_presets(self):
        channel_presets = {channel.name: channel.preset_fields() for channel in self.channels}
        return channel_presets


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
                 is_looped=False, is_paused=False, is_global_distinct=False, loop_gap=0,
                 loops=float("inf")):
        # TODO: is name needed? Since Channels are dict { channel_name : channel_instance }

        self.name = name
        self.audio_source = audio_source
        # Controls
        self.volume = volume
        self.balance = balance
        self.is_muted = is_muted
        self.fade_in_amount = 60
        self.fade_out_amount = self.fade_in_amount
        # Segment
        self.segment = AudioSegment.from_file(io.BytesIO(self.audio_source.mp3), format='mp3',
                                              parameters=["-vol", str(1)])

        print(self.name, "\nDuration:", self.segment.duration_seconds)
        print()
        # chunk larger segments for smaller ffmpeg subprocesses to prevent playback starvation
        if self.segment.duration_seconds > 45:
            sliced_chunks = self.segment[::45001]
            self.segment = None  # AudioSegment.empty()
            current_chunk = next(sliced_chunks, None)
            while True:
                next_chunk = next(sliced_chunks, None)
                if not self.segment:  # First chunk
                    self.segment = current_chunk.set_frame_rate(48000).fade_in(self.fade_in_amount)
                elif next_chunk:  # In between chunks
                    self.segment += current_chunk.set_frame_rate(48000)
                else:  # Last chunk
                    self.segment += current_chunk.set_frame_rate(48000).fade_out(self.fade_out_amount)
                    break
                current_chunk = next_chunk
        else:
            self.segment.set_frame_rate(48000).fade_in(self.fade_in_amount).fade_out(self.fade_out_amount)


        self.is_paused = is_paused
        self.pause_offset = 0

        self.is_global_distinct = is_global_distinct
        self.is_triggered = False

        # Loop
        self.loop_gap = loop_gap
        self.loops = loops

        self.is_looped = is_looped
        if self.loop_gap < 0:
            self.initial, self.crossfaded_segment = self.crossfader()

        # Random
        self.random_amount = random_amount

        if random_time_unit[-1] in 'h':
            self.random_time_unit = 3600
        else:
            self.random_time_unit = (int(random_time_unit[:-1]) * 60)

        # Scheduling -- Looped: True / Random: False
        if self.is_looped:
            self.schedule = self.loop_scheduler()
        else:
            self.schedule = self.random_seg_scheduler()

        self.next_play_time = next(self.schedule)
        self.seg_gen = self.segment_generator()


        # Might be redundant, but might be useful for checking changed channel state
        self.preset_fields = self.channel_fields()

    def channel_fields(self):
        fields = {"channel_name": self.name,
                  "volume": self.volume,
                  "balance": self.balance,
                  "is_muted": self.is_muted,
                  "is_paused": self.is_paused,
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
        print(" segment")
        if self.is_looped and self.loop_gap < 0:
            yield from self.initial
            self.next_play_time = next(self.schedule)

        while True:
            print(self.name, " is triggered: ", str(self.is_triggered))
            if self.is_looped and self.loop_gap < 0:
                yield from self.crossfaded_segment[::20]
            else:
                yield from self.segment[::20]

            print("done yielding", self.name)
            if not self.is_triggered:
                print(self.name, " next playtime:", round(self.next_play_time), 2)
                self.next_play_time = next(self.schedule)
            else:
                self.is_triggered = False

    def loop_scheduler(self, scene_time_offset=0):
        # initial loop setup
        loop_duration = self.segment.duration_seconds + self.loop_gap
        remaining_loops = self.loops
        self.pause_offset = 0
        self.next_play_time = scene_time_offset
        remaining_loops -= 1
        yield self.next_play_time

        while remaining_loops > 0:
            self.next_play_time = loop_duration + self.next_play_time
            remaining_loops -= 1
            yield self.next_play_time + self.pause_offset

        if remaining_loops <= 0:
            yield float("inf")

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

    def segment_audio_processer(self):
        pass

    def transition_segmenter(self):
        pass






class AudioSource:
    """
        Basic audio source from url or file.

        Attributes
        ----------
        file_path : str

        mp3 : bytes
            bytes representation of mp3

    """

    def __init__(self, url=None, file=None, name="audio file"):

        # TODO: Assert filetype and do conversion if needed.
        # MP3 only
        self.file_path = file

        if not file:
            try:
                self.mp3 = requests.get(url)
            except requests.exceptions.HTTPError as errh:
                print("Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                print("OOps: Something Else", err)

            # Save to temp location
            self.mp3 = requests.get(url).content
            self.file_path = str(pathlib.Path(__file__).parent.parent.absolute()) + "/temp_files/" + name
            with open(self.file_path, 'wb') as f:
                f.write(self.mp3)
        # TODO: Send mp3 to garbage collector if not needed

    def copy(self, new_path):
        shutil.copy(self.file_path, new_path)

    def save_as(self, new_path, audio_segment: AudioSegment):
        audio_segment.export(new_path, format="mp3")
        # TODO: if in temp_files delete old file

        # if self.file_path in temp_files
        # delete file
        self.file_path = new_path

    def save(self, audio_segment):
        audio_segment.export(self.file_path, format="mp3")

