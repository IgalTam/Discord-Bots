import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='b!', intents=intents)

DISCORD_TOKEN = 'OTQwODU2ODAxMzk2NjcwNDk0.YgNfLQ.Q5498pYclWbhNb-Y9AmvAoxiEZI'


@client.event
async def on_ready():
    print("bot ready")


@client.event
async def on_member_update(before, after):
    # await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status)))
    print("status updated")
    if after.activity is not None:
        # if after.nick is not None:
        print(after.nick)
        if len(after.activities) > 1:
            # if len(after.nick) > 1:
            print(after.nick)
            if str(after.activities[1].name).lower() == "league of legends":
                # if str(after.nick).lower() == "lol":
                print("naming")
                try:
                    nick = "Filthy League Player 0"
                    i = 0
                    while True:
                        if after.guild.get_member_named(nick) is None:
                            await after.edit(nick=nick)
                            break
                        else:
                            nick = nick[:len(nick)-1]
                            print(nick)
                            nick += str(i)
                            i += 1
                except discord.errors.Forbidden:
                    print("Not valid permissions")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
