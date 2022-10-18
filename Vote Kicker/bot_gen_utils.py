"""general use commands used by multiple bots"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

def guild_find(ctx: commands.Context, bot, guild_name):
    """returns guild object associated with guild_name, return None on fail"""
    if guild_name is None:
        return ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                return guild_y
        return None

def user_find(ctx: commands.Context, guild: discord.Guild, usr):
    """returns member object from guild"""
    user = None
    if usr is None:
        user = ctx.author
    else:
        for member in guild.members:
            if (member.name == usr or member.nick == usr) and member.id != guild.me.id:
                user = member
    return user

def get_member_name(target: discord.Member):
    """get member name output"""
    if target is None:
        return None
    elif target.nick is None:
        return target.name
    return target.nick

def inputs_in_numbered_str(arr, delimiter=""):
    """put variable length array inputs into a string, separated by delimiter and preceded by order number"""
    out_str = ""
    for i in range(len(arr)):
        if arr[i] is not None:
            out_str += f"{str(i+1)}. " + str(arr[i]) + delimiter
    return out_str