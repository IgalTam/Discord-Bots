import discord
from discord.ext import commands
import asyncio
import random
from bot_gen_utils import *
import botaudioutils
from config import DEF_PFP_PATH

FFMPEG_PATH = "C:/FFmpeg/bin/ffmpeg.exe" # set this to wherever your ffmpeg.exe is stored

class Impersonator(commands.Cog):
    """main set of commands for Impersonator Bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Impersonator Bot Cog loaded.")


    @commands.hybrid_command(name='mp', with_app_command=True, description='Play missing ping')
    async def mp(self, ctx: commands.Context, guild_name=None, usr=None):
        """plays missing ping in the channel usr is currently in"""

        # credit for missing pings: https://www.youtube.com/watch?v=T6dvKYZ7enU

        guild = guild_find(ctx, self.bot, guild_name)
        if guild is None:
            await ctx.send("Could not find server.")
            return

        # find user if not None
        user = user_find(ctx, guild, usr)

        # internal function definition
        async def safety_disconnect(ctx, guild_name):
            """disconnect bot if it is in a channel"""

            # establish which guild to operate in
            guild = guild_find(ctx, self.bot, guild_name)
            if guild is None:
                await ctx.send("Could not find server.")
                return

            # disconnect from channel, if possible
            try:
                voice_client = guild.me.voice.channel
                await voice_client.disconnect()
            except:
                pass

        if guild.me.voice:
            await safety_disconnect(ctx, guild)
        try:
            await user.voice.channel.connect()
            voice_channel = guild.voice_client
            async with ctx.typing():
                filename = await botaudioutils.YTDLSource.from_url('https://www.youtube.com/watch?v=T6dvKYZ7enU', loop=self.bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=filename))
            await asyncio.sleep(1)
            await voice_channel.disconnect()
            await ctx.send("Operation successful.")
        except AttributeError:
            await ctx.send("Guild or user not found.")


    @commands.hybrid_command(name="gb", with_app_command=True, description="impersonate someone in a guild")
    async def gb(self, ctx: commands.Context, usr, guild_name=None):
        """impersonate someone in a guild"""

        # establish which guild to operate in
        guild = guild_find(ctx, self.bot, guild_name)
        if guild is None:
            await ctx.send("Could not find server.")
            return

        # find and impersonate usr
        user = user_find(ctx, guild, usr)
        if user.nick:
            await guild.me.edit(nick=user.nick)
        else:
            await guild.me.edit(nick=user.name)
        ret_img = user.avatar
        mod_img = await ret_img.read()
        if user.activity is None:
            await self.bot.change_presence(activity=None, status=guild.me.status)
        else:
            await self.bot.change_presence(activity=discord.Activity(type=user.activity.type, name=user.activity.name))
        await self.bot.user.edit(avatar=mod_img)
        await ctx.send("impersonation initiated")


    @commands.hybrid_command(name="sd", with_app_command=True, description="reset bot to default appearance")
    async def sd(self, ctx: commands.Context, guild_name=None):
        """resets bot appearance attributes to defaults"""

        # establish which guild to operate in
        guild = guild_find(ctx, self.bot, guild_name)
        if guild is None:
            await ctx.send("Could not find server.")
            return
        
        # reset bot to original nickname, and activity
        await guild.me.edit(nick=None)
        await self.bot.change_presence(activity=None, status=guild.me.status)

        # convert image into bytes, then store as avatar
        with open(DEF_PFP_PATH, 'rb') as image:
            print("opened file")
            await self.bot.user.edit(avatar=bytearray(image.read()))
            await ctx.send("reverted to default")


    @commands.hybrid_command(name="gpp", with_app_command=True, desc="get a guild member's icon")
    async def gpp(self, ctx: commands.Context, usr,  guild_name=None):
        """gets avatar of member in a guild"""

        # establish which guild to operate in
        guild = guild_find(ctx, self.bot, guild_name)
        if guild is None:
            await ctx.send("Could not find server.")
            return
        
        # get avatar of user
        try:
            await ctx.send(user_find(ctx, guild, usr).avatar)
        except AttributeError:
            await ctx.send(f"Could not find a user named {usr}.")


    @commands.hybrid_command(name="gsp", with_app_command=True, desc="get a guild's icon")
    async def gsp(self, ctx: commands.Context, guild: discord.Guild):
        """gets guild icon"""
        await ctx.send(guild.icon)


    @commands.hybrid_command(name="go_offline", with_app_command=True,\
        description="set status to offline/invisible")
    async def go_offline(self, ctx: commands.Context):
        """set status to offline/invisible"""
        await self.bot.change_presence(status=discord.Status.offline)
        await ctx.send("going dark")


    @commands.hybrid_command(name="go_online", with_app_command=True,\
        description="set status to online")
    async def go_online(self, ctx: commands.Context):
        """set status to online"""
        await self.bot.change_presence(status=discord.Status.online)
        await ctx.send("going light")


    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        msg_flag = random.randint(1, 100)
        if isinstance(msg.channel, discord.channel.DMChannel) and msg.author != self.bot.user:
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
        await self.bot.process_commands(msg)
    

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
    await bot.add_cog(Impersonator(bot))
