"""general use commands used by multiple bots"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

def guild_find(ctx: commands.Context, bot, guild_name) -> discord.Guild:
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