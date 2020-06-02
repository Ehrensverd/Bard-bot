import os
import urllib
from urllib.request import urlopen
from urllib.request import urlretrieve
import cgi
from io import BufferedIOBase
import sys
import io
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
from os.path import basename
from mix import Mix
from urllib.request import urlopen
from xml.etree import ElementTree

from channel import Channel


def not_random(channels):
    return {k: v for k, v in channels.items() if v is not None and not v.is_random}


def longest(channels):
    return max(channels, key=lambda channel: channels[channel].segment.duration_seconds)


def loops(times, seg, crossfade=100):
    if times == 1:
        return seg
    return seg.append(loops(times - 1, seg), crossfade=crossfade)


# add to base segment, find and update cutoff point
def add_to_base_seg(channel, base_seg):
    # corner case, both segments are equal length.
    if len(channel.segment) == len(base_seg):
        return base_seg.overlay(channel.segment)
    else:
        seg = channel.segment
        length_base = len(base_seg)
        length_seg = len(seg)

        # first loop needs to be cutoff
        first = channel.segment[channel.cutoff:]
        remaining = length_base - len(first)

        # How many whole segments fits on base segment including cut segment
        looped_amount = int(remaining / length_seg)
        looped_seg = loops(looped_amount + 1, seg)
        length_looped = len(seg) * looped_amount + len(first)
        if (length_looped == len(seg)):
            channel.cutoff = 0
        else:
            channel.cutoff = length_base - length_looped
        return base_seg.overlay(first.append(looped_seg))

def get_mix_from_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    temnplate_id = soup.select_one("a[href*=vote]")['href'].rpartition('/')[2]
    template_url = 'https://xml.ambient-mixer.com/audio-template?player=html5&id_template='+str(temnplate_id)
    print(template_url)
    return Mix(template_url)

    #
    # # Find longest non random channel as base.
    # base = longest(not_random(channels))
    # segment = channels[base].segment + AudioSegment.empty()
    #
    # # All non randoms exept base, loop and find cut off point
    # none_randoms = not_random(channels)
    # del none_randoms[base]
    #
    # for v in none_randoms.values():
    #     print('Adding ' + v.name)
    #     if (v ==None):
    #         continue
    #     segment = add_to_base_seg(v, segment)
    #
    # # for channel in none_randoms.values():
    # #     channel.
    # file = '/home/eskil/PycharmProjects/Discord/AmbientBot/' + url.rpartition('/')[2] + '.mp3'
    # print(file)
    # segment.export(file)
    # print(len(segment))
    # return file


# mix = sound2.overlay(sound1s)
# mix.export('test.mp3')


def make_mp3():
    sound1 = AudioSegment.from_mp3('/home/eskil/PycharmProjects/Discord/AmbientBot/flute.mp3')
    sound2 = AudioSegment.from_mp3('/home/eskil/PycharmProjects/Discord/AmbientBot/insects.mp3')

    sound3 = sound1 + sound1 + sound1 + sound1 + sound1 + sound1 + sound1 + sound1 + sound1
    print('start')
    sound3.export('/home/eskil/PycharmProjects/Discord/AmbientBot/10min.mp3')

    print('sst')
    # mix sound2 with sound1, starting at 5000ms into sound1)
    output = sound1.overlay(sound2, position=1000)
    output = output.set_frame_rate(48000)
    print(output.frame_rate)
    print(type(output.raw_data))

    # save the result
    stream = output.export()
    print(stream.__fspath__())
    print(type(stream))
    print(type(stream.read()))
