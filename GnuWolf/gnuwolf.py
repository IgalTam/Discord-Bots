import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import gnuwolfutil
from gnuwolfutil import math

load_dotenv()

DISCORD_TOKEN = 'MTAyOTEwNzQyOTg4NTEwMDE0Mg.G3104U.yGWrRNAnIVnlmjMHZqecE_45tLL-2prZnbe-sg'
# test server id: 528651756201050113

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="~@", intents=intents)
    
    async def setup_hook(self) -> None:
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

# WARNING: DO NOT SYNC MORE THAN TWICE PER MINUTE
# ONLY SYNC WHEN MODIFYING A SLASH COMMAND ON THE SERVER END

bot = Bot() # bot initialization

@bot.hybrid_command(name = "test", with_app_command=True, description="Testing")
@commands.has_permissions(administrator=True)
async def test(ctx: commands.Context):
    await ctx.defer(ephemeral=True)
    await ctx.reply("hi!")

@bot.hybrid_command(name = "ping", with_app_command=False, description="pingpong")
@commands.has_permissions(administrator=True)
async def ping(ctx: commands.Context):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))

@bot.hybrid_command(name = "eval_num_size", with_app_command=True, description=" \
    indicates the size of the given input integer, both as unsigned and signed")
async def eval_num_size(ctx: commands.Context, in_num):
    try:
        if not gnuwolfutil.sci_note_conv(in_num):
            await ctx.send('{0} is not a valid number. Use E for scientific notation.'.format(in_num))
        else:
                bit_size = int(math.log(gnuwolfutil.sci_note_conv(in_num), 2)) + 1
                rec_data_type = 0
                if bit_size // 8 == 0:
                    rec_data_type = 8
                elif bit_size // 16 == 0:
                    rec_data_type = 16
                elif bit_size // 32 == 0:
                    rec_data_type = 32
                elif bit_size // 64 == 0:
                    rec_data_type = 64 
                if rec_data_type == 0:
                    await ctx.send('{0} is {1} bits long. Suggestion: look into what data types '\
                        'can handle this data size in your context.'.format(in_num, bit_size))
                else:
                    await ctx.send('{0} is {1} bits long. Suggestion: use a {2} bit data type.'\
                        .format(in_num, bit_size, rec_data_type))
    except OverflowError:
        await ctx.send('This number is too large to fit within a data type. Suggestion: '\
            'use bitwise operations to separate the value into two or more variables.')

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
