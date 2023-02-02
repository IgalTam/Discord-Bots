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


@bot.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
