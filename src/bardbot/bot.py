import asyncio
import os
from io import BufferedIOBase

from bringbuf.bringbuf import bRingBuf
from discord import opus
import discord
import io
import requests
from bs4 import BeautifulSoup
from discord import Client
from discord.ext import commands, tasks
import ffmpeg
from pydub import AudioSegment as AS, effects

from contextlib import suppress


from discord.utils import get

from .scene import Scene

from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv('GUILD_ID')



OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


# noinspection PyDefaultArgument
def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded(): return True
    for opus_lib in opus_libs:
        with suppress(OSError):
            opus.load_opus(opus_lib)
            return
        raise RuntimeError(f"Could not load an opus lib ({opus_lib}). Tried {', '.join(opus_libs)}")


def ptype(obj):
    print(type(obj))


bot = commands.Bot(command_prefix='!')


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

    input4 = AS.from_mp3(mp3).set_frame_rate(48000)
    export = input4.export(format='opus', codec='libopus')
    voice.stop()
    voice.play(discord.FFmpegOpusAudio(export.raw, pipe=True, codec='libopus'))


@bot.command()
async def test3(ctx, mp3):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)
    print('test')
    voice.stop()
    voice.play(discord.PCMAudio(Gen_Wrapper(mp3)))
    print('sgsgs')


@bot.command()
async def test2(ctx, mp3):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)

    else:
        await voice.move_to(channel)

    # input1 = ffmpeg.input()
    # input1 = ffmpeg.input()
    # input1 = ffmpeg.input()
    # input1 = ffmpeg.input()
    # input1 = ffmpeg.input()

    out = AS.from_mp3(mp3).set_frame_rate(48000).set_sample_width(2)
    out = io.BytesIO(out.raw_data)
    ptype(out)

    voice.stop()
    voice.play(discord.PCMAudio(out))


@bot.command()
async def test1(ctx, mp3):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)

    else:
        await voice.move_to(channel)

    out, _ = (ffmpeg
              .input(mp3)
              .output('-', format='opus', acodec='libopus', ab='12800', ar='48k')
              .overwrite_output()
              .run(capture_stdout=True)
              )
    print(type(out))
    out = io.BytesIO(out)
    ptype(out)

    voice.stop()
    voice.play(discord.PCMAudio(out), after=my_after)


def my_after(error):
    # voice = get(bot.voice_clients)
    # coro = voice.play(discord.PCMAudio(next(gen)), after=my_after)
    #
    # fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    # ptype(fut)
    # try:
    #     fut.result()
    # except:
    #     # an error happened sending the message
    #     pass
    print('player play done')


class Gen_Wrapper(discord.AudioSource):
    def __init__(self, mp3):
        self.seg = AS.from_mp3(mp3).set_frame_rate(48000)[::20]

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

    print('playing')
    voice.play(discord.PCMAudio(Mix_Wrapper(buf)), after=my_after)


def get_set(url):
    scene = Scene(url)
    buff = bRingBuf(3840000)
    while buff.len < 384000:
        buff.enqueue(next(scene.gen).raw_data)

    print('ready set go')
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



@bot.command()
async def play(ctx, url):
    pass

    file = ambient.get_mix_from_url(url)

    channel = ctx.message.author.voice.channel
    print('channel', channel)
    print(type(channel))
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return

    # voice er none her feil

    source = discord.FFmpegOpusAudio(file)

    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)

    else:
        await voice.move_to(channel)

    print(voice, 'voivoiv')

    voice.stop()
    voice.play(source)
    print('kakaka')

    # await songs.put(player)


# print('source ', type(source))
# if voice.is_playing():
#     voice.stop()
# voice.play(source)
# # , after=lambda _: bot.loop.call_soon_threadsafe(play_next(voice))
# channel = ctx.author.voice.channel
# vc = await channel.connect()
# vc.play(discord.FFmpegPCMAudio('tette.mp3'), after=lambda e: print('done', e))

# for channel in mix.channels.values():

# await ctx.send(channel.__dict__)

# load_opus_lib()
def main():
    bot.run(BOT_TOKEN)
