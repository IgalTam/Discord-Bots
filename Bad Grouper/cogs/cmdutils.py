import discord
from discord.ext import commands

class Cmdutils(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cmdutils Cog loaded.")
    
    @commands.hybrid_command(name="ping", with_app_command=True,\
        description="pingpong")
    async def ping(self, ctx: commands.Context):
        await ctx.send('Pong! {0}'.format(round(self.bot.latency, 1)))

async def setup(bot: commands.Bot):
    await bot.add_cog(Cmdutils(bot))