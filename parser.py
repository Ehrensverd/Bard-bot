from urllib.request import urlopen
from xml.etree import ElementTree

from channel import Channel


# url = urlopen('https://xml.ambient-mixer.com/audio-template?player=html5&id_template=20819 ')


def get_channels(url):
    url = urlopen(url)
    channels = {}
    num = 1
    for item in ElementTree.parse(url).iter():
        if item.tag.startswith('channel'):
            if item.findtext('id_audio') == '0':
                continue
            else:
                audio_id = item.findtext('id_audio')
                audio_name = item.findtext('name_audio')
                link = item.findtext('url_audio')
                mute = item.findtext('mute')
                volume = item.findtext('volume')
                balance = item.findtext('balance')
                random = item.findtext('random')
                random_counter = item.findtext('random_counter')
                random_unit = item.findtext('random_unit')
                cross_fade = item.findtext('crossfade')
                channels['channel' + str(num)] = Channel(audio_name, audio_id, link, mute, volume, balance, random,
                                                         random_counter, random_unit, cross_fade)

            num = num + 1
    return channels
