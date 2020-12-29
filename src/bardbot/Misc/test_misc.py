import string

from pydub.playback import play
from bardbot.Misc.scene import Scene

import io

from pydub import AudioSegment

# /html/body/div[4]/div/div[2]/div[4]/div[1]/div/div[2]/section[1]/div[4]/section/ol/div[4]/div/li/div[2]/div/div[1]
# https://open.spotify.com/playlist/0IyMP3izyM2jbYgJLydB00
url = "https://open.spotify.com/playlist/0bWUBjlr7O4troJKyyMVbD"

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

def parse_soundtrack(album, soundtrack):

    for spotify_song in [item for item in album if item.url is not None]:
        for song in soundtrack.songs:
            if song.namu == spotify_song.name:
                print("SONG FOUND: ", song.namu, " and ", spotify_song.name)
                spotify_song.url = song.url
                songs[song.namu] = spotify_song

    if any(True for item in album if item.url is None):
        # not done yet
        return False
    else:
        return True

def parse_search(search, album, searched_set):

    for soundtrack in search:
        if soundtrack in searched_set:
            continue
        searched_set.add(soundtrack)
        print("searching soundtrack:", soundtrack)
        print()
        all_found = parse_soundtrack(album, soundtrack)
        if all_found:
            return True
    return False

def parse_search_with_sort(search, album, searched_set):
    sort_dictionary = {}
    for word in album_search_query.split():
        word = word.lower()
        for soundtrack in search:
            if soundtrack in searched_set:
                continue
            soundtrack_name = soundtrack.id.replace("-", " ")

            if word in soundtrack_name:
                if soundtrack not in sort_dictionary:
                    sort_dictionary[soundtrack] = 1
                else:
                    sort_dictionary[soundtrack] += 1

    sorted_dictionary = {}
    for soundtrack in sort_dictionary:
        if sort_dictionary[soundtrack] not in sorted_dictionary:
            sorted_dictionary[sort_dictionary[soundtrack]] = [soundtrack]
        else:
            sorted_dictionary[sort_dictionary[soundtrack]].append(soundtrack)
    print("sorted")
    pprint(sorted_dictionary)
    for elem in sorted(sorted_dictionary.items(), reverse=True):
        for soundtrack in elem[1]:
            searched_set.add(soundtrack)
            print("searching soundtrack:", soundtrack)
            print()
            for song in soundtrack.songs:

                for spotify_song in albums[album]:

                    if song.namu == spotify_song.name:
                        print("SONG FOUND!: ", song.namu, " and ", spotify_song.name)
                        spotify_song.url = song.url
                        songs[song.namu] = spotify_song
                        album_found = True

            if album_found:
                break

class Song:
    def __init__(self, name, artists, duration, album):
        self.name = name
        self.artists = artists
        self.duration = duration
        self.album = album
        self.found = False
        self.album_found = False
        self.url = "None"

    def __str__(self):
        return 'Song(name=' + self.name + ', artists' + str(self.artists) + self.album + str(self.duration) + ')'

    def __repr__(self):
        return "{name=:" + self.name + " , url:" + self.url + " , artists:" + str(
            self.artists) + ", album:" + self.album + ", duration:" + str(self.duration) + "}"


albums = {}
for track_items in data["tracks"]["items"]:
    item = track_items["track"]
    song = Song(item["name"], [artist["name"] for artist in item["artists"]], item["duration_ms"],
                item["album"]["name"])
    if song.album not in albums:
        albums[song.album] = []
    albums[song.album].append(song)





# for item in albums.items():
#     print(item[0], ":")
#     for song in item[1]:
#         print("    -", song)

from script_modules import khinsider

pprint(albums)
bad_characters = list(string.punctuation + "1234567890")
bad_characters.remove("'")
bad_words = ["Motion", "Picture", "Television", "Movie"]
bad_dict = {bad_char: "" for bad_char in bad_characters}
bad_table = str.maketrans(bad_dict)
songs = {}
print(len(albums))
count = 0
for album in albums:
    count += 1
    album_found = False
    songs_found = False

    print(count, " searching album:", album)
    album_search_query = album
    print(album_search_query)
    album_search_query = album_search_query.translate(bad_table)
    if any(word in bad_words for word in album_search_query.split(" ")):
        print("Skipping non khinsider")
        continue
    searched_set = set()


    apostof =  "'" in album_search_query

    backup_query = album_search_query

    first = True
    while not album_found:

        print("Searching: ", album_search_query, "word amount: ", len(list(album_search_query.split(" "))))
        search = khinsider.search(album_search_query)
        if isinstance(search, khinsider.Soundtrack):
            searched_set.add(search)
            all_found = parse_soundtrack(albums[album],search)
        elif search and len(search) <= 25:
            print("searching soundtracks", search)
            all_found = parse_search(search,albums[album],searched_set)

        else:
            all_found = False

        if all_found:
            print("found all songs")
            break

            #
        if len(list(album_search_query.split())) < 2:
            print("not found")
            break
        if apostof and first:
            first = False
            backup_query = album_search_query
            album_search_query = album_search_query
            # Remove apostophe
            continue
        elif not first:
            first = True

            pass

        album_search_query = album_search_query.rsplit(maxsplit=1)[0]
        first = True

print("found ", len(songs))
for song in songs:
    print(song, "from", songs[song].album, "url:", songs[song].url)

for song in songs:
    print(type(song))
    break


# {"distict album": [song1 , song2, son3],
#
#
#  }

# for all songs in album
# step 1 find next album
# if album name contains movie or "motion picture" or "television" "tv"
#   go youtube
# else go khinsider
# remove bad characters
# search with full string
# if soundtrack
#       check if songs exist album found.
# add url to songs in album
# else
#       iter soundtrack list till found.
#   if not found remove word from end
# repeat.
# if string empty
# maybe searcb for song names? or go yt
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
        seg = seg + seg1

    seg = seg + 5
    print('done')
    play(seg)

# https://rpg.ambient-mixer.com/d-d-fantasy-inn-pub-tavern
# https://countryside.ambient-mixer.com/scottish-rain
# https://relaxing.ambient-mixer.com/deep-space-explorer--sleep-


# https://harry-potter-sounds.ambient-mixer.com/storm-on-the-hogwarts-express
