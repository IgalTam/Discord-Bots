import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
import youtube_dl
import random
import asyncio
# from keep_alive import keep_alive

load_dotenv()

DISCORD_TOKEN = 'ODU0MTAwMTA0ODc3MTc4OTAw.YMfAtQ.59nNdL-OiILFKBwhz0LRayrgeRs'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!$!', intents=intents, status=discord.Status.offline)
bot.delay = True  # global boolean for auto mode

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
    delay = False
    channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='play_scream', help='To play hunter scream')
async def play_scream(ctx):
    print(type(ctx))

    # credit for hunter scream: https://www.youtube.com/watch?v=G-ogxxcSZhM

    await safety_disconnect(ctx)
    delay = False
    channel = ctx.message.author.voice.channel
    await channel.connect()
    voice_client = ctx.message.guild.voice_client
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url('https://www.youtube.com/watch?v=G-ogxxcSZhM', loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await asyncio.sleep(4)
        await voice_client.disconnect()
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='en_auto', help='enables auto mode, see !$!help_auto for more info')
async def en_auto(ctx, delay_time):
    print('enabling auto mode')
    bot.delay = True
    while bot.delay is True:
        if float(delay_time) > 0:
            time.sleep(int(60*float(delay_time)))
            await play_scream(ctx)
        else:
            await ctx.send('invalid input')
            break


@bot.command(name='en_auto_rand', help='enables auto mode at random, see !$!help_auto for more info')
async def en_auto_rand(ctx):
    print('enabling auto random mode')
    bot.delay = True
    while bot.delay is True:
        time.sleep(int(60 * float(random.randint(1, 5))))
        await play_scream(ctx)


@bot.command(name='dis_auto', help='disables auto mode')
async def dis_auto(ctx):
    print('disabling auto mode')
    bot.delay = False


@bot.command(name='help_auto', help='explains auto mode')
async def dis_auto(ctx):
    await ctx.send('en_auto usage: !$!en_auto [input]. Valid [input] is any decimal or integer greater than 0 or '
                   'r. Every [input] minutes Hunter Bot will play_scream in the voice channel that the user '
                   'called en_auto from. If !$!en_auto_rand is used, play_scream will run every 1-5 minutes.')


@bot.event
async def on_message(message):
    if "zHunter Bot MkII" in message.content:
        await message.delete()
    for member in message.mentions:
        print(member)
        if member.name == "zHunter Bot MkII":
            await message.delete()
    await bot.process_commands(message)


async def safety_disconnect(ctx):
    """disconnect bot if it is in a channel"""
    voice_client = ctx.message.guild.voice_client
    try:
        await voice_client.disconnect()
    except:
        pass


@bot.command()
async def get_system_flags(ctx):
    """gets system channel flags of guild"""
    await ctx.send(ctx.message.guild.system_channel_flags)
    await ctx.send(ctx.message.guild.system_channel_flags.join_notifications)


@bot.command()
async def dw(ctx, dur=10, guild_name=None):
    """disables welcome message on guild join for dur seconds"""
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y
    old_flags = guild.system_channel_flags
    new_flags = old_flags
    new_flags.join_notifications = False
    await guild.edit(system_channel_flags=new_flags)
    await ctx.send("welcome messages disabled, use https://discord.com/api/oauth2/authorize?client"
                   "_id=869147082429194270&permissions=8&scope=bot for mk II")
    await asyncio.sleep(int(dur))
    new_flags_2 = new_flags
    new_flags_2.join_notifications = True
    await guild.edit(system_channel_flags=new_flags_2)
    await ctx.send("welcome messages re-enabled")


@bot.event
async def on_ready():
    print("bot ready")


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
