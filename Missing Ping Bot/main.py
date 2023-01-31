import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import MISSPING
from bot_gen_utils import *
import os

load_dotenv()

DISCORD_TOKEN = MISSPING

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


@bot.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)