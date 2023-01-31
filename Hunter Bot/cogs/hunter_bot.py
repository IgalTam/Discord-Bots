from bot_gen_utils import *
from config import HUNTER2_LNK
import discord
from discord.ext import commands
import random
import asyncio
import botaudioutils
import bot_gen_utils

MK2_LINK = HUNTER2_LNK # set this invite link in your config.py file

class HunterBot(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delay = False

    @commands.Cog.listener()
    async def on_ready(self):
        print("HunterBot Cog loaded.")

    @commands.hybrid_command(name="play_scrm", with_app_command=True, description="play hunter scream")
    async def play_scream(self, ctx: commands.Context, guildn=None, usern=None):

        # credit for hunter scream: https://www.youtube.com/watch?v=G-ogxxcSZhM

        guild = bot_gen_utils.guild_find(ctx, self.bot, guildn)
        user = bot_gen_utils.user_find(ctx, guild, usern)

        if guild.me.voice:
            await self.safety_disconnect(ctx)
        try:
            await user.voice.channel.connect()
            voice_channel = guild.voice_client
            async with ctx.typing():
                filename = await botaudioutils.YTDLSource.from_url('https://www.youtube.com/watch?v=G-ogxxcSZhM', loop=self.bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
            await asyncio.sleep(3.25)
            await voice_channel.disconnect()
            await ctx.send("Operation successful")
        except AttributeError:
            await ctx.send("Guild or user not found.")


    @commands.hybrid_command(name='en_auto', with_app_command=True, description="delays play_scrm for [input] minutes")
    async def en_auto(self, ctx: commands.Context, delay_time):
        print('enabling auto mode')
        if float(delay_time) > 0:
            await asyncio.sleep(int(60*float(delay_time)))
            await self.play_scream(ctx)
        else:
            await ctx.send('invalid input')


    @commands.hybrid_command(name='en_auto_rand', with_app_command=True, description="elays play_scrm" \
        " between 1 and 5 minutes at random")
    async def en_auto_rand(self, ctx: commands.Context):
        print('enabling auto random mode')
        self.delay = True
        while self.delay is True:
            await asyncio.sleep(int(60 * float(random.randint(1, 5))))
            await self.play_scream(ctx)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "zHunter Bot MkII" in message.content:
            await message.delete()
        for member in message.mentions:
            if member.name == "zHunter Bot MkII":
                await message.delete()
        await self.bot.process_commands(message)


    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def get_system_flags(self, ctx: commands.Context):
        """gets system channel flags of guild"""
        await ctx.send(ctx.message.guild.system_channel_flags)
        await ctx.send(ctx.message.guild.system_channel_flags.join_notifications)


    @commands.hybrid_command(name='dw', with_app_command=True, description='secret')
    @commands.has_permissions(administrator=True)
    async def dw(self, ctx: commands.Context, dur=30, guild_name=None):
        """disables welcome message on guild join for dur seconds"""
        guild = guild_find(ctx, self.bot, guild_name)
        sys_flags = guild.system_channel_flags # get current system flags of guild
        sys_flags.join_notifications = False 
        await guild.edit(system_channel_flags=sys_flags) # set guild notif. flag to false
        await ctx.send(f"welcome messages in guild {guild.name} disabled, "\
            f" use {MK2_LINK} for mk II")
        await asyncio.sleep(int(dur))
        sys_flags.join_notifications = True
        await guild.edit(system_channel_flags=sys_flags) # restore guild notif. flag
        await ctx.send(f"welcome messages in guild {guild.name} re-enabled")


    @commands.command(name="safety_disconnect")
    async def safety_disconnect(self, ctx: commands.Context):
        """disconnect bot if it is in a channel"""
        voice_client = ctx.message.guild.voice_client
        try:
            await voice_client.disconnect()
        except:
            await ctx.send("Safety disconnect failed.")


    @commands.hybrid_command(name="jchl_spec", with_app_command=True,\
        description="join channel of specific user in specific guild")
    async def jchl_spec(self, ctx:commands.Context, usr=None, guild_name=None):

        # establish which guild to operate in
        guild = guild_find(ctx, self.bot, guild_name)
        if guild is None:
            await ctx.send("Could not find server.")
            return

        # establish which user to target
        user = user_find(ctx, guild, usr)
        if user is None:
            await ctx.send("Could not find user.")
            return

        await user.voice.channel.connect()
        await ctx.send(f'connected to {usr} in {guild_name}')

async def setup(bot: commands.Bot):
    await bot.add_cog(HunterBot(bot))