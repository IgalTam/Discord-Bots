from config import HUNTER
from bot_gen_utils import guild_find
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
import asyncio
import botaudioutils
import bot_gen_utils
import os
# from keep_alive import keep_alive

load_dotenv()

DISCORD_TOKEN = HUNTER
MK2_LINK = 'https://discord.com/api/oauth2/authorize?client_id=869147082429194270&permissions=8&scope=bot'

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix="!$!", intents=intents,\
             status=discord.Status.offline)
    
    async def setup_hook(self) -> None:
        for filename in os.listdir('./Hunter Bot/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

bot = Bot()

@bot.hybrid_command(name="rle", with_app_command=True,\
    description="reload extension")
async def rle(ctx, filename):
    await bot.reload_extension(f'cogs.{filename[:-3]}')

@bot.hybrid_command(name="play_scrm", with_app_command=True, description="play hunter scream")
# @bot.command(name='play_scream', help='To play hunter scream')
async def play_scream(ctx: commands.Context, guildn=None, usern=None):

    # credit for hunter scream: https://www.youtube.com/watch?v=G-ogxxcSZhM

    guild = bot_gen_utils.guild_find(ctx, bot, guildn)
    user = bot_gen_utils.user_find(ctx, guild, usern)

    await safety_disconnect(ctx)
    try:
        channel = user.voice.channel
        await channel.connect()
        voice_client = guild.voice_client
        server = guild
        voice_channel = server.voice_client
        async with ctx.typing():
            print("async with typing")
            filename = await botaudioutils.YTDLSource.from_url('https://www.youtube.com/watch?v=G-ogxxcSZhM', loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/bin/ffmpeg.exe", source=filename))
        await asyncio.sleep(4)
        await voice_client.disconnect()
        await ctx.send("Operation successful")
    except AttributeError:
        await ctx.send("Guild or user not found.")


@bot.hybrid_command(name='en_auto', with_app_command=True, description="delays play_scrm for [input] minutes")
# @bot.command(name='en_auto', help='enables auto mode, see !$!help_auto for more info')
async def en_auto(ctx: commands.Context, delay_time):
    print('enabling auto mode')
    if float(delay_time) > 0:
        await asyncio.sleep(int(60*float(delay_time)))
        await play_scream(ctx)
    else:
        await ctx.send('invalid input')


@bot.hybrid_command(name='en_auto_rand', with_app_command=True, description="elays play_scrm" \
     " between 1 and 5 minutes at random")
# @bot.command(name='en_auto_rand', help='delays play_scrm between 1 and 5 minutes at random')
async def en_auto_rand(ctx: commands.Context):
    print('enabling auto random mode')
    bot.delay = True
    while bot.delay is True:
        await asyncio.sleep(int(60 * float(random.randint(1, 5))))
        await play_scream(ctx)


@bot.event
async def on_message(message):
    if "zHunter Bot MkII" in message.content:
        await message.delete()
    for member in message.mentions:
        if member.name == "zHunter Bot MkII":
            await message.delete()
    await bot.process_commands(message)


async def safety_disconnect(ctx: commands.Context):
    """disconnect bot if it is in a channel"""
    voice_client = ctx.message.guild.voice_client
    try:
        await voice_client.disconnect()
    except:
        await ctx.send("Safety disconnect failed.")


@bot.command()
async def get_system_flags(ctx: commands.Context):
    """gets system channel flags of guild"""
    await ctx.send(ctx.message.guild.system_channel_flags)
    await ctx.send(ctx.message.guild.system_channel_flags.join_notifications)


@bot.hybrid_command(name='dw', with_app_command=True, description='secret')
@commands.has_permissions(administrator=True)
async def dw(ctx: commands.Context, dur=10, guild_name=None):
    """disables welcome message on guild join for dur seconds"""
    guild = guild_find(ctx, bot, guild_name)
    sys_flags = guild.system_channel_flags # get current system flags of guild
    sys_flags.join_notifications = False 
    await guild.edit(system_channel_flags=sys_flags) # set guild notif. flag to false
    await ctx.send(f"welcome messages in guild {guild.name} disabled, "\
        f" use {MK2_LINK} for mk II")
    await asyncio.sleep(int(dur))
    sys_flags.join_notifications = True
    await guild.edit(system_channel_flags=sys_flags) # restore guild notif. flag
    await ctx.send(f"welcome messages in guild {guild.name} re-enabled")


@bot.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
