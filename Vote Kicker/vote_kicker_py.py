import bot_gen_utils
from config import VOTEKICK, OP_ID_EXT
import asyncio
import discord
from discord.ext import commands
import warnings
import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = VOTEKICK
OP_ID = OP_ID_EXT # put your discord ID here if you want
                           # to use the maintenance flag
MAINT_FLAG = False # prevents operator from getting votekicked while working on bot

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        super().__init__(command_prefix="!*!", intents=intents,\
             status=discord.Status.offline)
    
    async def setup_hook(self) -> None:
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

bot = Bot()

@bot.hybrid_command(name="votetimeout", with_app_command=True, description="vote on whether to timeout"\
    "someone and for how long")
@commands.has_permissions(moderate_members=True)
async def votetimeout(ctx: commands.Context, kicked: discord.Member, timeout_duration, timer=30.0):
    MAINT_FLAG = False
    kicked_name = bot_gen_utils.get_member_name(kicked)
    if kicked is None:
        return await ctx.send(f"{kicked_name} is not a member of this server.")
    if kicked.id == OP_ID and MAINT_FLAG is True:
        await ctx.send(f"{kicked_name} is attempting to fix me, stop interrupting")
    else:
        await ctx.send(f"Timeout for {kicked_name} is now pending.")
        result = await vote(ctx, timer)
        if result == 1:
            try:
                await kicked.timeout(datetime.timedelta(int(timeout_duration)), reason="The people voted for it.")
                await ctx.send(f"Vote result passed. {kicked_name} is timed out for {timeout_duration} minutes.")
            except:
                await ctx.send("Something went wrong. Vote result terminated.")
        elif result == 0:
            await ctx.send("Vote result is tied. No action taken.")
        else:
            await ctx.send("Vote result not passed.")


@bot.hybrid_command(name='votekick', with_app_command=True, description='vote on whether to '\
    'kick a user from the voice channel they are connected to')
async def votekick(ctx: commands.Context, kicked: discord.Member, timer=30.0):
    kicked_name = bot_gen_utils.get_member_name(kicked)
    if kicked_name is None:
        return await ctx.send(f"{kicked_name} is not a member of this server.")
    elif kicked.id == OP_ID and MAINT_FLAG is True:
        await ctx.send(f"{kicked_name} is attempting to fix me, stop interrupting")
    elif kicked.voice is None:
        print("no voice")
        await ctx.send(f"{kicked_name} is not connected to a voice channel.")
    else:
        await ctx.send(f"VC kick for {kicked_name} is now pending.")
        result = await vote(ctx, timer)
        if result == 1:
            await kicked.move_to(None)
            await ctx.send(f"Vote result passed. {kicked_name} kicked from voice channel.")
        elif result == 0:
            await ctx.send("Vote result is tied. No action taken.")
        else:
            await ctx.send("Vote result not passed.")


@bot.hybrid_command(name='genvote', with_app_command=True, description="create a Y/N vote for input message")
async def genvote(ctx: commands.Context, message, timer=30):
    await ctx.send(message)
    result = await vote(ctx, timer)
    if result == 1:
        await ctx.send("Yes")
    elif result == 0:
        await ctx.send("Tie")
    else:
        await ctx.send("No")


async def vote(ctx, durat):
    """voting-enabling function, uses emojis to represent option weights"""
    message = await ctx.send("React to this message to vote.")
    await asyncio.gather(message.add_reaction('👍'), message.add_reaction('👎'))

    def check(m):
        return m.content == 'cancel' and m.channel == ctx.message.channel

    try:
        await bot.wait_for('message', timeout=durat, check=check)
        cache_msg = discord.utils.get(bot.cached_messages, id=message.id)
        if cache_msg.reactions[0].count == cache_msg.reactions[1].count:
            return 0 # tie
        elif cache_msg.reactions[0].count > cache_msg.reactions[1].count:
            return 1 # yes
        else:
            return 2 # no
    except asyncio.TimeoutError:
        cache_msg = discord.utils.get(bot.cached_messages, id=message.id)
        if cache_msg.reactions[0].count == cache_msg.reactions[1].count:
            return 0 # tie
        elif cache_msg.reactions[0].count > cache_msg.reactions[1].count:
            return 1 # yes
        else:
            return 2 # no


@bot.hybrid_command(name='genmultvote', with_app_command=True, description='create a poll for up to 10 messages')
async def genmultvote(ctx: commands.Context, msg1: str, msg2: str, msg3=None, msg4=None, msg5=None, msg6=None,\
        msg7=None, msg8=None, msg9=None, msg10=None, timer=30):
    if msg1 is None or msg2 is None:
        return await ctx.send("Insufficient poll options.")
    msg_arr = [msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8, msg9, msg10]
    opts = 0
    await ctx.send("Multivote options:")
    for msg in msg_arr:
        if msg is None:
            break
        opts += 1
    await ctx.send(bot_gen_utils.inputs_in_numbered_str(msg_arr, '\n'))
    result = await vote_multi(ctx, opts, timer)
    await ctx.send(f"Winning option: {msg_arr[result]}")


async def vote_multi(ctx: commands.Context, opt_count, durat):
    """voting-enabling function, uses number emojis to represent option weights"""
    num_emoj_table = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', \
        '7️⃣', '8️⃣', '9️⃣', '🔟']
    message = await ctx.send("React to this message to vote.")
    for i in range(opt_count):
        await asyncio.gather(message.add_reaction(num_emoj_table[i]))

    def check(m):
        return m.content == 'cancel' and m.channel == ctx.message.channel

    try:
        await bot.wait_for('message', timeout=durat, check=check)
        cache_msg = discord.utils.get(bot.cached_messages, id=message.id)
        max_val = max(cache_msg.reactions[i].count for i in range(len(cache_msg.reactions)))
        for msg in cache_msg.reactions:
            if msg.count == max_val:
                return cache_msg.reactions.index(msg)
    except asyncio.TimeoutError:
        cache_msg = discord.utils.get(bot.cached_messages, id=message.id)
        max_val = max(cache_msg.reactions[i].count for i in range(len(cache_msg.reactions)))
        for msg in cache_msg.reactions:
            if msg.count == max_val:
                return cache_msg.reactions.index(msg)


@bot.event
async def on_ready():
    print("bot ready")


@bot.hybrid_command(name='ping', with_app_command=True, description='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
