import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
import youtube_dl
import asyncio
import random

load_dotenv()

DISCORD_TOKEN = 'OTM0MjY2ODM5NzQ2MzU1Mjkw.YetlzA.wDVSV0W0T8d98MCiaG0wfIwSqv8'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents, status=discord.Status.offline)
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
        # return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        return filename


@bot.command(name='join_channel', help='just join')
async def join_channel(ctx, guild_name=None, usr=None):
    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    # find user if not None
    user = None
    if usr is None:
        user = ctx.author
    else:
        for member in guild.members:
            if (member.name == usr or member.nick == usr) and member.id != guild.me.id:
                user = member

    # connect to channel
    channel = user.voice.channel
    await channel.connect()


@bot.command()
async def start_record(ctx, usr, guild_name=None):
    await ctx.author.voice.channel.connect()  # Connect to the voice channel of the author
    ctx.voice_client.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx, usr, guild_name)
    await ctx.respond("Initiating surveillance")


async def finished_callback(sink, ctx, usr, guild_name):
    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    # find user if not None
    user = None
    if usr is None:
        user = ctx.author
    else:
        for member in guild.members:
            if (member.name == usr or member.nick == usr) and member.id != guild.me.id:
                user = member

    # Here you can access the recorded files:
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    for rec in sink.audio_data.items():
        if rec.user_id == user.id:
            await user.voice.channel.connect()
            async with ctx.typing():
                guild.voice_client.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=audio))
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await ctx.channel.send(f"Recorded audio for {', '.join(recorded_users)}.", files=files)


@bot.command()
async def stop_recording(ctx):
    ctx.voice_client.stop_recording()  # Stop the recording, finished_callback will shortly after be called
    await ctx.respond("Terminating surveillance")


@bot.command()
async def get_stream_info(ctx, usr, guild_name=None):
    """get streaming info"""
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    for member in guild.members:
        if (member.name == usr or member.nick == usr) and member.id != guild.me.id:
            user = member

    print(user.voice.self_stream)


@bot.command(name='leave_channel', help='just leave')
async def leave_channel(ctx, guild_name=None):
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y
    try:
        voice_channel = guild.voice_client
        await voice_channel.disconnect()
    except AttributeError:
        await ctx.send("Not connected to voice channel")


@bot.command(name='mp', help='Play missing ping')
async def mp(ctx, guild_name=None, usr=None):
    # guild, user = find_guild_user(ctx, guild_name, usr)
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    # find user if not None
    user = None
    if usr is None:
        user = ctx.author
    else:
        for member in guild.members:
            if member.name == usr or member.nick == usr and member.id != guild.me.id:
                user = member
    await safety_disconnect(ctx, guild)
    channel = user.voice.channel
    await channel.connect()
    voice_channel = guild.voice_client
    try:

        async with ctx.typing():
            filename = await YTDLSource.from_url('https://www.youtube.com/watch?v=T6dvKYZ7enU', loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await asyncio.sleep(1)
        await voice_channel.disconnect()
    except:
        await ctx.send("The bot is not connected to a voice channel.")


async def safety_disconnect(ctx, guild_name):
    """disconnect bot if it is in a channel"""

    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    try:
        voice_client = guild.me.voice.channel
        await voice_client.disconnect()
    except:
        pass


@bot.command()
async def gb(ctx, usr, guild_name=None):
    """impersonate someone in a guild"""

    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y
                print("found guild", guild_y)
    print("end conditional")

    # find and impersonate usr
    for user in guild.members:
        if (user.name == usr or user.nick == usr) and user.id != guild.me.id:
            await guild.me.edit(nick=user.nick)
            await guild.me.edit(name=user.name)
            await guild.me.edit(color=user.color)
            ret_img = user.avatar_url_as()
            mod_img = await ret_img.read()
            if user.activity is None:
                await bot.change_presence(activity=None)
            else:
                await bot.change_presence(activity=discord.Activity(type=user.activity.type, name=user.activity.name))
            await bot.user.edit(avatar=mod_img)
            await ctx.send("impersonation initiated")


@bot.command()
async def gpp(ctx, usr, guild_name=None):
    """gets avatar of member in a guild"""

    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y
    # get avatar of user
    for user in guild.members:
        if (user.name == usr or user.nick == usr) and user.id != guild.me.id:
            await ctx.send(user.avatar_url_as())


@bot.command()
async def go_offline(ctx):
    """set status to offline/invisible"""
    await bot.change_presence(status=discord.Status.offline)
    await ctx.send("going dark")


@bot.command()
async def go_online(ctx):
    """set status to online"""
    await bot.change_presence(status=discord.Status.online)
    await ctx.send("going light")


@bot.event
async def on_message(msg):
    msg_flag = random.randint(1, 100)
    if isinstance(msg.channel, discord.channel.DMChannel) and msg.author != bot.user:
        if msg_flag % 6 == 0:
            await msg.channel.send("Hello")
        elif msg_flag % 5 == 0:
            await msg.channel.send("Hi")
        elif msg_flag % 4 == 0:
            await msg.channel.send("Hey")
        elif msg_flag % 3 == 0:
            await msg.channel.send("ⒽⒺⓁⓁⓄ")
        elif msg_flag % 2 == 0:
            await msg.channel.send("ⒼⓄⓄⒹ ⓃⒾⒼⒽⓉ")
        elif msg_flag % 1 == 0:
            await msg.channel.send("ⒽⓄⓌⒹⓎ ⓉⒽⒺⒺ")
        else:
            await msg.channel.send("a;lsjdflka;jsdlkfsa")
    await bot.process_commands(msg)


async def find_guild_user(ctx, guild_name=None, usr=None):
    """finds user and guild to operate in"""
    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    # find user if not None
    user = None
    if usr is None:
        user = ctx.author
    else:
        for member in guild.members:
            if member.name == usr or member.nick == usr and member.id != guild.me.id:
                user = member

    return guild, user


@bot.command(name='play_audio_rem', help='a')
async def play_audio_rem(ctx, dur, guild_name=None, usr=None):
    await safety_disconnect(ctx, guild_name)
    # establish which guild to operate in
    guild = None
    if guild_name is None:
        guild = ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                guild = guild_y

    # find user if not None
    user = None
    if usr is None:
        user = ctx.author
    else:
        for member in guild.members:
            if member.name == usr or member.nick == usr and member.id != guild.me.id:
                user = member

    # must hard code url in for now
    channel = user.voice.channel
    await channel.connect()
    try:
        voice_channel = guild.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url("https://www.youtube.com/watch?v=G-ogxxcSZhM", loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await asyncio.sleep(int(dur))
        await voice_channel.disconnect()
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.event
async def on_ready():
    print("bot ready")


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
