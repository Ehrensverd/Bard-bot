import sys
import threading
from asyncio import get_event_loop
from collections import deque
from contextlib import suppress
import os
from multiprocessing.context import Process

from bardbot import GUI
from bardbot.AudioMixer import main_mixer
from bardbot.AudioMixer.main_mixer import MainMixer, Monitor
from bardbot.AudioMixer.scene import Scene
from bardbot.Controller.controller import Controller
from bardbot.GUI.gui import init_ui

from dotenv import load_dotenv
import discord
from discord import opus
from discord.ext import commands, tasks
from discord.utils import get
from pydub import AudioSegment as As



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


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(719204954514128938)
    await channel.send('bot online')
    print('opusloaded: ', discord.opus.is_loaded())


@bot.event
async def on_disconnect():
    print(f'{bot.user} has disconnected from Discord!')
    channel = bot.get_channel(689397500863578122)
    await channel.send('bot offline')


class Bard(discord.AudioSource):
    def __init__(self, size=15):
        self.source = None
        self.deque = None
        self.size = size

    def add_source(self, source: As):
        self.source = source
        self.deque = deque(maxlen=self.size)
        self.deque.append(next(self.source.segmenter))

    def add_new_source(self, source: As):
        self.new_source = source
        self.temp_deque = deque(maxlen=self.size)
        self.temp_deque.append(next(self.new_source))

    @tasks.loop(seconds=0.01)
    async def fill(self):
        if self.source is None:
            print("NOPE")
            return

        if len(self.deque) < self.size:
            try:
                segment = next(self.source.segmenter)
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




@bot.command()
async def mp3(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)

    voice.stop()  # ensures current playback is stopped before continuing
    voice.play(discord.FFmpegOpusAudio('/home/eskil/PycharmProjects/Bard-bot/src/bardbot/BARD_LOOP_1.mp3'))

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
async def scene(ctx, url):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)

    print("Get Scene")
    source = Scene(url)
    print("Scene done?")

    if voice.is_playing():
        print("Set new source")
        bard.source = source
    else:
        bard.add_source(source)


    try:
        bard.fill.start()  # denne restartes ikke
    except RuntimeError:
        print("Restart task")
        bard.fill.restart()

    if not voice.is_playing(): # change source
        voice.play(bard)

@bot.command()
async def play(ctx, url):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        voice = await channel.connect()
        await voice.move_to(channel)
    else:
        await voice.move_to(channel)

    if url in scenes:
        url = scenes[url]

    print("Get Scene")
    source = Scene(url)
    print("Scene done?")

    if voice.is_playing():
        print("Set new source")
        bard.source = source
    else:
        bard.add_source(source)


    try:
        bard.fill.start()  # denne restartes ikke
    except RuntimeError:
        print("Restart task")
        bard.fill.restart()

    if not voice.is_playing(): # change source
        voice.play(bard)


@bot.command()
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
    elif voice.is_paused():
        voice.resume()

@bot.command()
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        pass
    elif voice.is_paused():
        voice.resume()

@bot.command()
async def mute_channel(ctx, channel):

    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source.source.pause_channel(channel)

@bot.command()
async def unmute_channel(ctx, channel):

    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source.source.unpause_channel(channel)

@bot.command()
async def resume_music(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source.source.music_playing = True

@bot.command()
async def pause_music(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source.source.music_playing = False


@bot.command()
async def resume_scene(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source.source.scene_playing = True


@bot.command()
async def pause_scene(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source.source.scene_playing = False

# load_opus_lib()

# check config file
# set discord and monitor true false
discord_playback = False
monitor_playback = True



def main():
    print("tresfsdf")
    #sys.setswitchinterval()
    # Start machinery
    main_mix = MainMixer()

    # Read config files and set discord_playback local_playback

    playback = None
    # Setup playback
    if discord_playback:
        async def bot_final_start():
            await bot.start(BOT_TOKEN)

        def bot_loop_start(event_loop):
            event_loop.run_forever()

        loop = get_event_loop()
        loop.create_task(bot_final_start())
        bot_thread = threading.Thread(target=bot_loop_start, args=(loop,))
        bot_thread.start()

        playback = Bard(main_mix)

        # old start call: bot.run(BOT_TOKEN)

    if monitor_playback and not discord_playback:
        playback = Monitor(main_mix)
        # Setup controller / businiss logic

    controller = Controller(main_mix, playback)
    #dummy_scene = controller.import_scene("https://movies-other.ambient-mixer.com/mr--tumnus--house")
    # Setup business logic- called by gui
    # Load Gui
    # ui_thread = threading.Thread(target=init_ui, args=(controller,))
    # ui_thread.start()
    GUI.gui.init_ui(controller)

    print("discord actually done")

