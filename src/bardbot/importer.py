import json
import re
from pprint import pprint
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from script_modules.khinsider import Soundtrack, SearchError


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



def webscrape_spotify(url):
    """Create playlist from openspotify url"""

    r = requests.get(url)
    p = re.compile(r'Spotify\.Entity = (.*?);')
    # parse to json from javascript object.
    # this bypass need for manual scroll to access all songs
    data = json.loads(p.findall(r.text)[0])
    pprint(data, indent=4)
    albums = {}
    for track_items in data["tracks"]["items"]:
        item = track_items["track"]
        song = Song(item["name"], [artist["name"] for artist in item["artists"]], item["duration_ms"],
                    item["album"]["name"])
        if song.album not in albums:
            albums[song.album] = []
        albums[song.album].append(song)
    pprint(albums, indent=4)
    return albums

def khinsider_search(query):
    """Return a list of Soundtrack objects for the search term `term`."""
    if len(query) <3:
        return []

    r = requests.get(urljoin("https://downloads.khinsider.com/", "search"), params={"search": query})
    print(r.url)
    re_pattern =  re.compile(br"^</td>\s*$", re.MULTILINE)
    soup = BeautifulSoup(re.sub(re_pattern, b'', r.content), "html.parser")

    if soup.find("title").text != "Search - \n":
        # this is a soundtrack
        print("this is a soundtrack")
        url = soup.find('table', id='songlist').find("a")["href"]
        return Soundtrack(url.split('/')[-2])
    try:
        anchors = soup('p')[1]('a')
    except IndexError:
        raise SearchError(soup.find('p').get_text(strip=True))
    soundtrackIds = [a['href'].split('/')[-1] for a in anchors]
    return [Soundtrack(id) for id in soundtrackIds]


def khinsider_soundtrack():
    # parse songs from a soundtrack
    pass



khinsider_search("ssassins Creed")
#webscrape_spotify('https://open.spotify.com/playlist/0bWUBjlr7O4troJKyyMVbD')


# mp3 from file, url, youtube,  ambient-mixer channel

# scene from ambient-mixer, generic and user presets

# playlist from spotify, youtube, generic and user presets

