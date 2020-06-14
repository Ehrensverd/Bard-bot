# queue songs from spotify, youtube, url.mp3

#
import itertools
from collections import deque


class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = []
        self.playlist = deque(len(self.songs))
        for song in self.songs:
            self.playlist.append(song)
        self.segmenter = self.playlist_generator()
        self.is_active = False
        self.next = False

    def import_from_url(self, url):
        pass

    def import_from_file(self, path):
        pass

    def remove_song(self, song):
        if song in self.songs:
            self.songs.remove(song)

    def next_song(self):
        self.next = True


    def playlist_generator(self):
        for song in itertools.cycle(self.songs):
            song_gen = song[::20]
            while True:
                if self.next:
                    self.next = False
                    break

                try:

                    yield next(song_gen)
                except StopIteration:
                    break
