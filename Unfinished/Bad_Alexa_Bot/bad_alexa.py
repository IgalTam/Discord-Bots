import discord
from discord.ext import commands
from dotenv import load_dotenv
from linked_list import Node
from queues import QueueLinked
import youtube_dl
import asyncio
import queue
from config import BAD_ALEXA

load_dotenv()

DISCORD_TOKEN = BAD_ALEXA

bot = commands.Bot(command_prefix='!')
music_queue = None

youtube_dl.utils.bugs_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join_channel', help='just join')
async def join_channel(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='play', help='plays next item in queue')
async def play(ctx):
    await safety_disconnect(ctx)
    await join_channel(ctx)
    url = None
    try:
        url = music_queue.dequeue()
    except IndexError:
        await ctx.send("No items queued.")
        return
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await play(ctx)
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='q_add', help='q+ <url>, adds to queue')
async def q_add(url):
    """adds item to queue"""
    if music_queue.is_full:
        music_queue.capacity += 1
    music_queue.enqueue(url)


@bot.command(name='q_skip', help='skips the current song')
async def q_skip(ctx):
    """skips current item"""
    await safety_disconnect(ctx)
    await join_channel(ctx)
    await play(ctx)


@bot.command(name='dc', help='leaves channel')
async def dc(ctx):
    """disconnect bot if it is in a channel"""
    voice_client = ctx.message.guild.voice_client
    try:
        await voice_client.disconnect()
    except:
        pass


async def safety_disconnect(ctx):
    """disconnect bot if it is in a channel"""
    voice_client = ctx.message.guild.voice_client
    try:
        await voice_client.disconnect()
    except:
        pass


@bot.event
async def on_ready():
    global music_queue
    music_queue = QueueLinked(20)
    print("bot ready")


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
