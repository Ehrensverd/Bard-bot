## stage has all audio clips
## scenes
## neighbor stages
# gloabal stage
# stage main volume

"""
Words:

Stage is the base template of a soundscape.
A stage can have multiple scenes. And have all channels used by its scenes.

When a stage is loaded into a group it scenes are also loaded and readied
changes done to a scene presist during group session. Unless saved or reloaded
Stage handles what channels to yield from, based on active scene

Scene is a configured preset of a soundscape.
Different Scenes can have different presets for the same channels.

Channel is base audio channel and plays and controls an audiosegment.
It can be shared / played from different scenes.
It yields 20ms segments to stage based on active scene

Segmenter is a generator that yields 20ms audio slices

Stage has all channels in two collection, active and non active
on scene change channel collections are updated.

Stage segmenter takes 20ms from each channel segmenter

each channel is told be active scene what configurations it is to use.
scene also tells stage which channels are active or not.

fra load / new
først new, so load

"""
import io

import requests
from pydub import AudioSegment


class Stage:
    """Base audio template for soundscapes

    Attributes
    ----------
    volume : int
        main volume for stage

    scenes : dict { scene_name : scene instance }
        collection of loaded scenes.
        each scene is a different preset for the stage.

    channels : dict { channel_name : channel instance }
        collection of channels.
        channel behavior depends on the active scene

    active_scene : scene instance
        scene from which stage segmenter get channel settings

    stage_segmenter()
        yields from all active channels and overlays segments
        and handles scene transitions
        yields to group mixer

    """

    def __init__(self, connected_stages=None, volume=50, active_channels=None,non_active_channels=None, scenes=None):
        """"""
        if not scenes:
            # New stage
            scene = Scene("initial scene")
            self.scenes[scene.name] = self.scenes["default"] = scene
            self.connected_stages = {}
            self.active_channels = {}
            self.non_active_channels = {}
        else:
            # Load stage
            self.active_scene = scenes["default"]

            self.connected_stages = connected_stages
            self.scenes = scenes
            self.active_channels = active_channels
            self.non_active_channels = non_active_channels
        self.volume = volume




    # Utility
    def segmenter(self):
        # put depleted channels into non_active
        # if past random triggered time unit, reset depleted
        # check if any non active are scheduled

        # take all channels overlay and yield


        pass


    # Stage
    def load_stage(self):
        pass

    def save_stage(self):
        pass
    def start_stage(self):
        pass

    def pause_stage(self):
        pass

    def stop_stage(self):
        pass


    # Scene

    def change_scene(self, scene):
        """"""
        # check what channels are identical in segment stats, volume, balance
        # if same check if crossfade or randomly triggered
        # change segment in channel segmenter

        pass

    def create_scene(self):
        pass

    def copy_scene(self, scene):
        pass

    def delete_scene(self, scene):
        pass

    def save_scene(self, scene):
        pass

    # Channels

    def new_channel(self):


        channel = Channel("url", "name", self)
        # Get url or file and name.
        # make base segment
        # make default preset in all scenes.
        # make default preset for all scenes.
        # active in what scenes?

    def copy_channel(self, channel):
        pass




class Scene:
    """A preset for a stage.
        has a list of active channels and their scene presets
        list of nonactive channels
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

    """

    def __init__(self, name="new scene", playlist=None, channel_presets=None):
        # shared channels - adjust volume, balance, but keep play position when swapping
        # individual channels. starts from beginning
        # playlist channels / stream. play,stop next, prev, repeat shuffle
        #

        if channel_presets:
            # loaded scene
            self.channel_presets = channel_presets
            self.name = name
        else:
            #new sc ene
            self.channel_presets = {}

        self.playlist = playlist

    def add_channel(self, channel):
        self.channel_presets[channel] = self.defualt_preset()

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

    is_random : bool
        indicates channel is played at a random interval
        thus needs random_rate ratio amount / time_unit
        randomed channels cannot be crossfaded

    random_ratio : dict {    amount : int
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

    def __init__(self, name, audio_source, balance=0, volume=50, is_muted=False, is_crossfaded=False, is_random=False ):
        self.name = name
        self.audio_source = audio_source
        self.balance = balance
        self.volume = volume
        self.segment = AudioSegment.from_file(io.BytesIO(self.audio_source.mp3), format='mp3', frame_rate=48000,
                                              parameters=["-vol", str(volume)]).set_frame_rate(48000).pan(
            balance / 50).fade_in(50).fade_out(20)




    def activate(self):
        """Make scene segments, scheduels
        check whats different than default
        """
        if self.is_active:
            return

        preset = self.active_scene.channel_presets(self)

        scene_segment = self.base_segment
        if preset["balance"] != 0:
            scene_segment = scene_segment.pan(self.active_scene.channel_presets(self)["balance"] / 50)

        if preset["is_random"]:
            # check schedule, make scheduler
            pass
        if not preset["is_random"] and preset["is_crossfade"]:
            # Make crossfaded segments
            pass

        self.is_active = True
        return scene_segment

    def segmenter(self):

        pass

    def transition_segmenter(self):
        pass
