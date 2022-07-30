import asyncio
import discord
from discord.ext import commands
import aiohttp
import warnings
import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = 'OTI4ODU1MDYyMzYzNjM1ODAy.Yde1sA.400Tl6v92AUpxEC2Gl50kheduSk'

warnings.filterwarnings("ignore", category=DeprecationWarning)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!*!', intents=intents)
bot.session = aiohttp.ClientSession()


async def timeout_user(*, user_id: int, guild_id: int, until):
    headers = {"Authorization": f"Bot {bot.http.token}"}
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    print(json)
    async with bot.session.patch(url, json=json, headers=headers) as session:
        print(session.status)
        if session.status in range(200, 299):
            return True
        return False


@bot.command(name='votetimeout', help='votetimeout [name] [duration (minutes)]: hold vote on whether to '
                                      'timeout someone, and for how long (DOES NOT WORK ON ADMINS)')
async def votetimeout(ctx, kicked, durat, timer=30.0):
    maint_flag = False
    kicked_obj = get_member(kicked, ctx.message.guild)
    if kicked_obj is None:
        return await ctx.send(f"{kicked} is not a member of this server.")
    if ctx.message.author.id == 168015898148470784 and kicked.id == 145396599621812226:
        await ctx.send(f"Stop it Pavel that's mean")
    elif ctx.message.author.id == 168015898148470784 and kicked_obj.id == 386648374469722144 and maint_flag is True:
        await ctx.send(f"{kicked} is attempting to fix me, stop interrupting")
    else:
        result = await vote(ctx, timer)
        if result:
            timeout_check = await timeout_user(user_id=kicked_obj.id, guild_id=ctx.message.guild.id, until=int(durat))
            if timeout_check:
                return await ctx.send(f"Vote result passed. Timeout for {durat} minutes.")
            await ctx.send("Something went wrong. Vote result terminated.")
        else:
            await ctx.send("Vote result not passed.")


@bot.command(name='votekick', help='votekick [name]: hold vote on whether to disconnect someone from vc')
async def votekick(ctx, kicked, timer=30.0):
    maint_flag = False
    kicked_obj = get_member(kicked, ctx.message.guild)
    if kicked_obj is None:
        return await ctx.send(f"{kicked} is not a member of this server.")
    elif kicked_obj.id == 386648374469722144 and maint_flag is True:
        await ctx.send(f"{kicked} is attempting to fix me, stop interrupting")
    else:
        result = await vote(ctx, timer)
        if result:
            await kicked_obj.move_to(None)
            await ctx.send(f"Vote result passed. {kicked} kicked from voice channel.")
        else:
            await ctx.send("Vote result not passed.")


def get_member(name, guild):
    """discord.py got changed, need this to find member"""
    print(guild.members)
    for member in guild.members:
        if member.name == name or member.nick == name:
            return member
    return None


@bot.command(name='genvote', help='genvote [message]: vote yes or no to message (put message in "" if '
                                  'it contains spaces)')
async def genvote(ctx, message, timer=30):
    await ctx.send(message)
    result = await vote(ctx, timer)
    if result:
        await ctx.send("Yes")
    else:
        await ctx.send("No")


@bot.command()
async def vote(ctx, durat):
    message = await ctx.send("React to this message to vote.")
    await asyncio.gather(message.add_reaction('👍'), message.add_reaction('👎'))

    def check(m):
        return m.content == 'cancel' and m.channel == ctx.message.channel

    try:
        await bot.wait_for('message', timeout=durat, check=check)
        cache_msg = discord.utils.get(bot.cached_messages, id=message.id)
        if cache_msg.reactions[0].count > cache_msg.reactions[1].count:
            return True
        else:
            return False
    except asyncio.TimeoutError:
        cache_msg = discord.utils.get(bot.cached_messages, id=message.id)
        if cache_msg.reactions[0].count > cache_msg.reactions[1].count:
            return True
        else:
            return False


@bot.event
async def on_ready():
    print("bot ready")


"""@bot.event
async def on_reaction_add(reaction, user):
    print("someone reacted")
    print(reaction.message.reactions)"""


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
