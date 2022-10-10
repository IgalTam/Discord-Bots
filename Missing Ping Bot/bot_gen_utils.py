"""general use commands used by multiple bots"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

def guild_find(ctx, bot, guild_name):
    """returns guild object associated with guild_name, return None on fail"""
    if guild_name is None:
        return ctx.message.guild
    else:
        for guild_y in bot.guilds:
            if guild_y.name == guild_name:
                return guild_y
        return None