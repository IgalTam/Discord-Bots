import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import HUNTER2
import youtube_dl
import asyncio

load_dotenv()

DISCORD_TOKEN = HUNTER2

intents = discord.Intents.all()
client = discord.Client(intents=intents)
guild = discord.Guild
bot = commands.Bot(command_prefix=')', intents=intents, status=discord.Status.offline)

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


async def safety_disconnect(ctx):
    """disconnect bot if it is in a channel"""
    voice_client = ctx.message.guild.voice_client
    try:
        await voice_client.disconnect()
    except:
        pass


@bot.command(name='p', help='play scream')
async def p(ctx):
    await safety_disconnect(ctx)
    channel = ctx.message.author.voice.channel
    i = 0
    await channel.connect()
    voice_client = ctx.message.guild.voice_client
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            print("async with typing")
            filename = await YTDLSource.from_url('https://www.youtube.com/watch?v=G-ogxxcSZhM', loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await asyncio.sleep(4)
        await voice_client.disconnect()
        await ctx.guild.leave()
    except:
        await ctx.send("The bot is not connected to a voice channel.")


async def play_scream(guild_in, voice_client):
    # guild_in = find_guild(await bot.fetch_guilds().flatten(), "Music Storage")
    try:
        voice_channel = guild_in.voice_client
        filename = await YTDLSource.from_url('https://www.youtube.com/watch?v=G-ogxxcSZhM', loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await asyncio.sleep(4)
        await voice_client.disconnect()
        await guild_in.leave()
    except:
        print("bot not in vc")
        # await bot.send("The bot is not connected to a voice channel.")


def find_channel(channels, name):
    for channel in channels:
        if channel.name == name and isinstance(channel, discord.VoiceChannel):
            return channel


@bot.command()
async def leave_g(ctx):
    await ctx.message.guild.leave()


@bot.event
async def on_message(message):
    if "zHunter Bot MkII" in message.content:
        await message.delete()
    await bot.process_commands(message)


def fetch_home_base():  # home base
    return 528651756201050113


@bot.event
async def on_guild_join(guild_in):
    try:
        # if guild_in.id != fetch_home_base():
        tar_chan = find_channel(await guild_in.fetch_channels(), "Embassy of Hamsters")
        print("found channel")
        await tar_chan.connect()
        voice_client = guild_in.voice_client
        await play_scream(guild_in, voice_client)
    except AttributeError as err:
        print(err)


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


@bot.event
async def on_ready():
    print("bot is ready")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
