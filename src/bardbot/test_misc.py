import json
from pydub.playback import play
from bardbot.scene import Scene

import io

from pydub import AudioSegment
import requests

#/html/body/div[4]/div/div[2]/div[4]/div[1]/div/div[2]/section[1]/div[4]/section/ol/div[4]/div/li/div[2]/div/div[1]
# https://open.spotify.com/playlist/0IyMP3izyM2jbYgJLydB00
url = "https://open.spotify.com/playlist/0bWUBjlr7O4troJKyyMVbD"
from bs4 import BeautifulSoup
from urllib.request import urlopen

import requests, re, json

r = requests.get('https://open.spotify.com/playlist/0bWUBjlr7O4troJKyyMVbD')
p = re.compile(r'Spotify\.Entity = (.*?);')
data = json.loads(p.findall(r.text)[0])


from pprint import pprint

# #pprint(dict(data))
# for item in [track_items["track"] for track_items in data["tracks"]["items"] ]:
#     print(item["name"])
#     print(item["album"]["name"])
#     for artist in item["artists"]:
#         print(artist["name"])
#     print(item["duration_ms"])
#     print()


class Song:
    def __init__(self, name, artists, duration, album):
        self.name = name
        self.artists = artists
        self.duration = duration
        self.album = album
        self.found = False
        self.album_found = False
        self.url = None

    def __str__(self):
        return 'Song(name=' + self.name + ', artists' + str(self.artists) + self.album + str(self.duration) + ')'

    def __repr__(self):
        return "{name=:" + self.name+" , artists:"+ str(self.artists) + ", album:" + self.album+ ", duration:"+ str(self.duration)+"}"


albums = {}
for track_items in data["tracks"]["items"] :
    item = track_items["track"]
    song = Song(item["name"], [artist["name"] for artist in item["artists"]], item["duration_ms"],item["album"]["name"])
    if song.album not in albums:
        albums[song.album] = []
    albums[song.album].append(song)


# for item in albums.items():
#     print(item[0], ":")
#     for song in item[1]:
#         print("    -", song)
#     print()
album_found = True
from script_modules import khinsider

for album in albums:
    album_search_query = album


    while not album_found:
        if not album_found:
            search = khinsider.search(album)
            if len(search)==0:
                pass


    pass



search = khinsider.search("The Sims - House Party Mix")
for item in search:
    print(item)
print(search)
# {"distict album": [song1 , song2, son3],
#
#
#  }

# for all songs in album
#step 1 find album if album name contains game and not movie or "motion picture" or "television
# Assassin's Creed 4: Black Flag (Freedom Cry) [Original Game Soundtrack]
# Assassin's Creed Black Flag Freedom Cry
# Assassin's+Creed+Black+Flag+Freedom+Cry
# https://downloads.khinsider.com/search?search=Assassin%27s+Creed+Black+Flag+Freedom+Cry -direct
# https://downloads.khinsider.com/search?search=Dungeons+%26+Dragons -select from list



# with open("playlists.txt", "a+") as outfile:
#     json.dump(playlist, outfile, indent=4 )


def test_download_AudioSeg():
    external_audio = requests.get("https://xml.ambient-mixer.com/audio/1/3/0/130739e1e14f93b44daf7cfaa462b52a.mp3")
    au = io.BytesIO(external_audio.content)
    audio_segment = AudioSegment.from_file(au, format='mp3')
    play(audio_segment)

def test_mixer(input):
    mix = Scene(input)
    seg = AudioSegment.empty()

    for _ in range(0, 3000):
        seg1 = next(mix.segmenter)
        seg = seg+seg1

    seg = seg +5
    print('done')
    play(seg)



# https://rpg.ambient-mixer.com/d-d-fantasy-inn-pub-tavern
# https://countryside.ambient-mixer.com/scottish-rain
# https://relaxing.ambient-mixer.com/deep-space-explorer--sleep-


# https://harry-potter-sounds.ambient-mixer.com/storm-on-the-hogwarts-express
