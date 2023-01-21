from config import SKWIM, TENOR_KEY
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
import asyncio
import os
# from keep_alive import keep_alive

load_dotenv()

DISCORD_TOKEN = SKWIM
API_KEY = TENOR_KEY

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix="\o/", intents=intents,\
             status=discord.Status.offline)
    
    async def setup_hook(self) -> None:
        for filename in os.listdir('./SKWIM Bot/cogs'):
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


@bot.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
