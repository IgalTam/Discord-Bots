import discord
from discord.ext import commands

class Cmdutils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("bot ready")
    
    @commands.hybrid_command(name="ping", with_app_command=True,\
        description="pingpong")
    async def ping(self, ctx: commands.Context):
        await ctx.send('Pong! {0}'.format(round(self.bot.latency, 1)))
    
    @commands.hybrid_command(name="jchl", with_app_command=True,\
        description="joins message author's voice channel")
    async def jchl(self, ctx: commands.Context):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    
    @commands.hybrid_command(name="lchl", with_app_command=True,\
        description="leaves voice channel in message author's guild")
    async def jchl(self, ctx: commands.Context):
        try:
            guildn = ctx.message.guild
            for vc in self.bot.voice_clients:
                if vc.guild == guildn:
                    await vc.disconnect()
        except:
            await ctx.send("Not connected to a channel.")

async def setup(bot):
    await bot.add_cog(Cmdutils(bot))