import discord
from discord.ext import commands
from config import BAD_GRPR
from discord import client
from discord.utils import get
from dotenv import load_dotenv
from discord import colour as color
import getopt
import os

load_dotenv()

DISCORD_TOKEN = BAD_GRPR

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix="/*/", intents=intents)
    
    async def setup_hook(self) -> None:
        for filename in os.listdir('./Bad Grouper/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

bot = Bot() # bot initialization

@bot.event
async def on_ready():
    print("bot ready")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
