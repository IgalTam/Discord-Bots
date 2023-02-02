import bot_gen_utils
from discord.ext import commands
from discord.utils import get
from discord import colour as color

class SkwimBot(commands.Cog):
    """main set of commands for SKWIM Bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("SKWIM Bot Cog loaded.")

    @commands.hybrid_command(name = "make", with_app_command=True, description="create x private tc & vc, \
        custom names optional, associated roles optional")
    @commands.has_permissions(administrator=True)
    async def make(self, ctx: commands.Context, count, name, role_make=False):
        await ctx.send("Creating groups...")
        guild = ctx.message.guild
        dr = guild.default_role
        for ind in range(1, int(count)+1):
            cname = name + str(ind)
            # create custom category
            category = await guild.create_category(cname, reason=None, position=None)
            # create tc
            tc = await guild.create_text_channel(cname, category=category, reason=None)
            # create vc
            vc = await guild.create_voice_channel(cname, category=category, reason=None)
            # if applicable, create role and assign permissions
            if role_make is True:
                role = await self.make_role(ctx, cname)
                await tc.set_permissions(dr, read_messages=False, send_messages=False)
                await tc.set_permissions(role, read_messages=True, send_messages=True, manage_channels=True)
                await vc.set_permissions(dr, connect=False, speak=False)
                await vc.set_permissions(role, connect=True, speak=True, manage_channels=True)
        await ctx.send("Created " + str(count) + " groups.")
    
    # coding plan

    # states
    # - start "lobby", query for players
    # - voting for prompt
    # - searching Tenor for gif
    # - voting on best meme
    # - assign points, display scoreboard
    # - return to "lobby"

    # additional requirements
    # - create new text channel for game, then delete after session is stopped
    # - lobby join/leave -> reactions?
    # - lobby start -> command
    # - prompts -> come from a file, prompts can be added by users to this file
    # - if possible, make Tenor searching dynamic like in actual KWIM
    # - make a random player be presenter for meme intros
    # - voting should be secret -> bot dms message to react to?
    # - winning meme should be reposted
    # - point system -> TBD


async def setup(bot: commands.Bot):
    await bot.add_cog(SkwimBot(bot))