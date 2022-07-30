import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv
import time
import youtube_dl

load_dotenv()

DISCORD_TOKEN = 'ODY5ODE4MTY4ODQ2MjE3MjQ2.YQDvSw.rKIh2xobWN0UiVMhRfnsBEqSaHQ'

client = discord.Client()
bot = Bot(command_prefix='|3')
guild = discord.Guild
url = None
delay = 0

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
    print("channel requested")
    channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='play_welcome', help='plays welcome message')
async def play_welcome(ctx):
    global url, delay
    print(url, delay)
    channel = ctx.message.author.voice.channel
    await channel.connect()
    voice_client = ctx.message.guild.voice_client
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        time.sleep(delay)
        await voice_client.disconnect()
    except:
        await ctx.send("ooga booga no operato")


@bot.event
async def on_voice_state_update(member, pre_chan, tar_chan):
    print("voice_state_update active")
    channel = bot.get_channel(528651756201050115)
    await channel.send("|3play_welcome")


@bot.command(name='set_url', help='set welcome media')
async def set_url(url_in):
    global url
    url = url_in


@bot.command(name='set_delay', help='set welcome duration')
async def set_delay(delay_in):
    global delay
    delay = delay_in


@bot.event
async def on_ready():
    print("greedo online-o")
    global delay, url
    delay = 3
    url = 'https://www.youtube.com/watch?v=X42fU3ZINME'
    print("greedo setupo")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
