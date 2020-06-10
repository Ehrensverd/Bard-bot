from pydub import AudioSegment

# group is a collection of scenes. playlists and soundboard sounds.

class Group:
    def __init__(self):
        self.active_sources = []
        self.puased_sources = []
        self.base_segment = AudioSegment.silent(duration=20, frame_rate=48000)

    def add_source(self, group):
        self.active_sources.append(group)

    def remove_source(self, group):
        if group in self.active_sources:
            self.active_sources.remove(group)

    def mix_generator(self):
        mix_segment = self.base_segment.set_channels(2)
        for group in self.active_sources:
            mix_segment = mix_segment.overlay(next(group.segmenter))
        yield mix_segment


