import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random
from bot_gen_utils import *
import botaudioutils
import os

load_dotenv()

DISCORD_TOKEN = 'OTM0MjY2ODM5NzQ2MzU1Mjkw.YetlzA.wDVSV0W0T8d98MCiaG0wfIwSqv8'
FFMPEG_PATH = "C:/FFmpeg/bin/ffmpeg.exe" # set this to wherever your ffmpeg.exe is stored

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents,\
             status=discord.Status.offline)
    
    async def setup_hook(self) -> None:
        for filename in os.listdir('./Missing Ping Bot/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

bot = Bot()


@bot.hybrid_command(name='mp', with_app_command=True, description='Play missing ping')
async def mp(ctx: commands.Context, guild_name=None, usr=None):
    """plays missing ping in the channel usr is currently in"""

    # credit for missing pings: https://www.youtube.com/watch?v=T6dvKYZ7enU

    guild = guild_find(ctx, bot, guild_name)
    if guild is None:
        await ctx.send("Could not find server.")
        return

    # find user if not None
    user = user_find(ctx, guild, usr)

    if guild.me.voice:
        await safety_disconnect(ctx, guild)
    try:
        await user.voice.channel.connect()
        voice_channel = guild.voice_client
        async with ctx.typing():
            filename = await botaudioutils.YTDLSource.from_url('https://www.youtube.com/watch?v=T6dvKYZ7enU', loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=filename))
        await asyncio.sleep(1)
        await voice_channel.disconnect()
        await ctx.send("Operation successful.")
    except AttributeError:
        await ctx.send("Guild or user not found.")


async def safety_disconnect(ctx, guild_name):
    """disconnect bot if it is in a channel"""

    # establish which guild to operate in
    guild = guild_find(ctx, bot, guild_name)
    if guild is None:
        await ctx.send("Could not find server.")
        return

    # disconnect from channel, if possible
    try:
        voice_client = guild.me.voice.channel
        await voice_client.disconnect()
    except:
        pass


@bot.hybrid_command(name="gb", with_app_command=True, description="impersonate someone in a guild")
async def gb(ctx: commands.Context, usr, guild_name=None):
    """impersonate someone in a guild"""

    # establish which guild to operate in
    guild = guild_find(ctx, bot, guild_name)
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
        await bot.change_presence(activity=None, status=guild.me.status)
    else:
        await bot.change_presence(activity=discord.Activity(type=user.activity.type, name=user.activity.name))
    await bot.user.edit(avatar=mod_img)
    await ctx.send("impersonation initiated")


@bot.hybrid_command(name="gpp", with_app_command=True, desc="get a guild member's icon")
async def gpp(ctx: commands.Context, usr,  guild_name=None):
    """gets avatar of member in a guild"""

    # establish which guild to operate in
    guild = guild_find(ctx, bot, guild_name)
    if guild is None:
        await ctx.send("Could not find server.")
        return
    
    # get avatar of user
    try:
        await ctx.send(user_find(ctx, guild, usr).avatar)
    except AttributeError:
        await ctx.send(f"Could not find a user named {usr}.")

@bot.hybrid_command(name="gsp", with_app_command=True, desc="get a guild's icon")
async def gsp(ctx: commands.Context, guild: discord.Guild):
    """gets guild icon"""
    await ctx.send(guild.icon)


@bot.hybrid_command(name="go_offline", with_app_command=True,\
     description="set status to offline/invisible")
async def go_offline(ctx: commands.Context):
    """set status to offline/invisible"""
    await bot.change_presence(status=discord.Status.offline)
    await ctx.send("going dark")


@bot.hybrid_command(name="go_online", with_app_command=True,\
     description="set status to online")
async def go_online(ctx: commands.Context):
    """set status to online"""
    await bot.change_presence(status=discord.Status.online)
    await ctx.send("going light")


@bot.event
async def on_message(msg: discord.Message):
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


@bot.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
