import discord
from discord.ext import commands
from asyncio import sleep
import youtube_dl

DISCORD_TOKEN = 'ODY5ODE4MTY4ODQ2MjE3MjQ2.YQDvSw.rKIh2xobWN0UiVMhRfnsBEqSaHQ'


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


class Music(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Music cog successfully loaded.')

    @commands.Cog.event
    async def on_voice_state_update(self, member, before, after):
        # replace this with the path to your audio file
        url = 'https://www.youtube.com/watch?v=X42fU3ZINME'

        vc_before = before.channel
        vc_after = after.channel

        if not vc_before and vc_after.id == YOUR VOICE CHANNEL ID:
            vc = await vc_after.connect()
            vc.play(discord.FFmpegPCMAudio(path))
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            vc_after.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
                # Start Playing
                sleep(f.duration)
            await vc.disconnect()


def setup(bot):
    bot.add_cog(Music(bot))