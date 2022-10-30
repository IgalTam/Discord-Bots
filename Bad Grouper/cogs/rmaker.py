from http.client import HTTPException
from io import TextIOWrapper
from turtle import position
import discord
from discord.ext import commands
import asyncio
import os

class Rmaker(commands.Cog):
    """commands for creating guild roles from input files
    and creating input files via interactive input or guild captures"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Rmaker Cog loaded.")

    def guild_owner_only():
        """function to check whether command is called by guild owner"""
        async def predicate(ctx: commands.Context):
            return ctx.author == ctx.guild.owner  # checks if author is the guild owner
        return commands.check(predicate)
    
    
    @commands.hybrid_command(name="rmake", with_app_command=True,\
        description="creates roles based on a \"rmake\" input file")
    @commands.has_permissions(administrator=True)
    async def rmake(self, ctx: commands.Context, infile: discord.Attachment):

        # parse file
        await ctx.send("Parsing file...")
        if infile.filename[len(infile.filename)-4:] != ".txt":
            await ctx.send(f"{infile} is invalid, input must be a standard .txt file.")
            return
        
        # process file contents
        await ctx.send("Processing file...")
        try:
            await infile.save(fp=infile.filename) # save attachment as file-like obj for reading
            with open(infile.filename, mode='rb') as fo: # open file as binary in case of non-ascii characters
                rles = fo.read().decode('utf-8').split('\n')
            fo.close()
            succ_rles = 0
            for rle in rles: # process individual role names
                if rle.count(':') < 1:
                    await ctx.send("Skipping invalid channel...")
                else: # create role based on valid data
                    rle_arr = rle.split(':')
                    rle_color = discord.Color.from_str(hex(int(rle_arr[0])))
                    rle_hoist = False
                    if rle_arr[1] == "t":
                        rle_hoist = True
                    rle_mentnble = False
                    if rle_arr[2] == "t":
                        rle_mentnble = True
                    rle_perm = discord.Permissions(permissions=int(rle_arr[4]))
                    # try:
                    await ctx.message.guild.create_role(color=rle_color.value, hoist=rle_hoist,\
                        mentionable=rle_mentnble, name=rle_arr[3], permissions=rle_perm)
                    succ_rles += 1
                    # except:
                    #     await ctx.send("Skipping invalid role...")
            os.unlink(fo.name)
            await ctx.send(f"Operation complete. {succ_rles} roles created.")
        except FileNotFoundError:
            await ctx.send("File not found. Make sure to include the complete path.")
    

    @commands.hybrid_command(name="crmake", with_app_command=True,\
        description="clears all channels in guild, then creates new"\
        " channels from a \"rmake\" input file")
    @guild_owner_only()
    async def crmake(self, ctx: commands.Context, infile: discord.Attachment):
        # confirm owner intentions
        await ctx.send("This action has significant impact on your guild and is irreversible. "\
            "Are you sure you would like to proceed? [Y/N]")

        def check(msg: discord.Message):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
            msg.content.lower() in ["y", "n", "yes", "no"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.send("Did not receive valid confirmation in time, cancelling guild role wipe...")
            return
        if msg.content.lower() == "n" or msg.content.lower() == "no":
            await ctx.send("Cancelling guild role wipe...")
            return
        else:
            await ctx.send("Initiating guild role wipe...")
            # delete as many existing roles as possible
            old_rle_cnt = 0
            for rle in ctx.guild.roles:
                try:
                    await rle.delete()
                except:
                    old_rle_cnt += 1
            
            # create new channels
            await self.rmake(ctx, infile)
            await ctx.send(f"Guild roles remade. Failed to delete {old_rle_cnt} old roles.")


    @commands.hybrid_command(name="rmakesnap", with_app_command=True,\
        description="saves current channel hierarchy as a \"rmake\" text file")
    async def rmakesnap(self, ctx: commands.Context, des_filename: str):
        # parse filename
        await ctx.send("Parsing filename...")
        if des_filename.count('.') > 0:
            await ctx.send(f"{des_filename} is invalid, input filename cannot contain \'.\'.")
            return

        # write channels to file
        await ctx.send("Creating \"rmake\" file...")
        with open(f"{des_filename}.txt", 'wb') as fp: # open file as binary in case of non-ascii characters
            for rle in ctx.message.guild.roles:
                # get color
                fp.write(f"{rle.color.value}:".encode('utf-8'))
                # get hoist
                if rle.hoist:
                    fp.write("t:".encode('utf-8'))
                else:
                    fp.write("f:".encode('utf-8'))
                # get mentionable
                if rle.mentionable:
                    fp.write("t:".encode('utf-8'))
                else:
                    fp.write("f:".encode('utf-8'))
                # get name
                fp.write(f"{rle.name}:".encode('utf-8'))
                # get permissions
                fp.write(f"{rle.permissions.value}\n".encode('utf-8'))

        # send file to user and clean up
        fp.close()
        try:
            await ctx.author.send(file=discord.File(fp=f"{des_filename}.txt"), \
                content="Process complete. Here is your \"rmake\" text file.")
        except discord.Forbidden:
            await ctx.channel.send(file=discord.File(fp=f"{des_filename}.txt"), \
                content="Process complete. Here is your \"rmake\" text file.")
        os.unlink(fp.name)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rmaker(bot))