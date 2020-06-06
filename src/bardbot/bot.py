from collections import deque
from contextlib import suppress
import io
import os

from bringbuf.bringbuf import bRingBuf
from dotenv import load_dotenv
import discord
from discord import opus
from discord.ext import commands, tasks
from discord.utils import get
from pydub import AudioSegment as As

from .scene import Scene

load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']
bot = commands.Bot(command_prefix='!')


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded(): return True
    for opus_lib in opus_libs:
        with suppress(OSError):
            opus.load_opus(opus_lib)
            return
        raise RuntimeError(f"Could not load an opus lib ({opus_lib}). Tried {', '.join(opus_libs)}")

def ptype(obj):
    print(type(obj))





@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(689397500863578122)
    await channel.send('bot online')
    print('opusloaded: ', discord.opus.is_loaded())


@bot.event
async def on_disconnect():
    print(f'{bot.user} has disconnected from Discord!')
    channel = bot.get_channel(689397500863578122)
    await channel.send('bot offline')


@bot.command()
async def test4(ctx, mp3):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)

    input4 = As.from_mp3(mp3).set_frame_rate(48000)
    export = input4.export(format='opus', codec='libopus')
    voice.stop()
    voice.play(discord.FFmpegOpusAudio(export.raw, pipe=True, codec='libopus'))


class Bard(discord.AudioSource):
    def __init__(self, size=10):
        self.source = None
        self.deque = None
        self.size = size

    def add_source(self, source: As):
        self.source = source
        self.deque = deque(maxlen=self.size)
        self.deque.append(next(self.source))

    @tasks.loop(seconds=0.01)
    async def fill(self):
        if self.source is None:
            print("NOPE")
            return

        if len(self.deque) < self.size:
            try:
                segment = next(self.source)
                self.deque.append(segment)
            except StopIteration:
                print(self)
                print("source depleted")

    def read(self):
        if self.source is None:
            print("NOPE")
            return b""
        try:
            return self.deque.pop().raw_data
        except IndexError:
            print("Playback done")
            return b""

    def cleanup(self):
        print("Stopping deque filling")
        self.fill.stop()

bard = Bard()

@bot.command()
async def test_deque(ctx, mp3):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)

    voice.stop()  # ensures current playback is stopped before continuing
    source = As.from_mp3(mp3).set_frame_rate(48000)[:40000:20]
    bard.add_source(source)
    bard.fill.start()  # denne restartes ikke
    voice.play(bard)

@bot.command()
async def test_deque_scene(ctx, url):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)

    voice.stop()  # ensures current playback is stopped before continuing
    source = Scene(url).gen
    bard.add_source(source)
    bard.fill.start()  # denne restartes ikke
    voice.play(bard)


@bot.command()
async def test2(ctx, mp3):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)

    else:
        await voice.move_to(channel)

    out = As.from_mp3(mp3).set_frame_rate(48000).set_sample_width(2)
    out = io.BytesIO(out.raw_data)
    ptype(out)

    voice.stop()
    voice.play(discord.PCMAudio(out))


def my_after(error):
   print('Player ended, empty stream')


class Gen_Wrapper(discord.AudioSource):
    def __init__(self, mp3):
        self.seg = As.from_mp3(mp3).set_frame_rate(48000)[::20]

    def read(self, _):
        return next(self.seg).raw_data

class Mix_Wrapper(discord.PCMAudio):
    def __init__(self, gen):
        self.gen = gen

    def read(self, frames):
        # self.buffer.write(next(self.mix.gen).raw_data)
        # return self.buffer.read(frames)
        print('playing', frames)
        return self.gen.deque(frames)




@bot.command()
async def test(ctx, url):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)

    else:
        await voice.move_to(channel)

    scene, buf = get_set(url)

    # slow_count.start(mix, buf)

    print('Discord player playing from stream')
    voice.play(discord.PCMAudio(Mix_Wrapper(buf)), after=my_after)


def get_set(url):
    print("Setting up scene and buffer.")
    scene = Scene(url)
    buff = bRingBuf(3840000)
    while buff.len < 384000:
        buff.enqueue(next(scene.gen).raw_data)
    print("Buffer ready.")
    return scene, buff


@tasks.loop(seconds=0.1)
async def slow_count(mix, buf):
    if buf.len < 34800:
        for _ in range(0, 10):
            buf.enque(next(mix.gen).raw_data)
        print('loop added')

class StreamRW(io.BufferedRandom):
    def __init__(self, raw):
        super().__init__(raw)
        self.seek(0)

    def read(self, size=1):
        super().seek(self.read_offset)
        data = super().read(size)
        self.read_offset = self.tell()
        return data

    def write(self, data):
        super().seek(self.write_offset)
        written = super().write(data)
        self.write_offset = self.tell()
        return written

    def seek(self, offset, whence=0):
        super().seek(offset)
        self.read_offset = self.write_offset = self.tell()



# load_opus_lib()

def main():
    bot.run(BOT_TOKEN)
