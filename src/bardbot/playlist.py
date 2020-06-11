# queue songs from spotify, youtube, url.mp3

#
import itertools









def playlist_generator(self):
    for song in itertools.cycle(self.playlist):
        song_gen = song[::20]
        while True:
            try:
                yield next(song_gen)
            except StopIteration:
                break
