from io import TextIOWrapper
import discord
from discord.ext import commands
import asyncio
import os
import tempfile

class Gmaker(commands.Cog):
    """commands for creating guild channels from input files
    and creating input files via interactive input"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Gmaker Cog loaded.")

    def guild_owner_only():
        async def predicate(ctx: commands.Context):
            return ctx.author == ctx.guild.owner  # checks if author is the owner
        return commands.check(predicate)
    
    @commands.hybrid_command(name="gmake", with_app_command=True,\
        description="creates channels based on an input file")
    async def gmake(self, ctx: commands.Context, infile: discord.Attachment):
        
        # parse file
        await ctx.send("Parsing file...")
        if infile.filename[len(infile.filename)-4:] != ".txt":
            await ctx.send(f"{infile} is invalid, input must be a standard .txt file.")
            return
        
        # process file contents
        await ctx.send("Processing file...")
        try:
            await infile.save(fp=infile.filename) # save attachment as file-like obj for reading
            with open(infile.filename, mode='r') as fo:
                fconts = fo.read()
                chnls = fconts.split('\n')
            fo.close()
            cur_cat = None
            succ_chns = 0
            for chnl in chnls: # processing individual channel names
                if chnl.count(':') != 1:
                    await ctx.send("Skipping invalid channel...")
                else:
                    chnl_arr = chnl.split(':')
                    chnl_type, chnl_nm = chnl_arr[0], chnl_arr[1]
                    if chnl_type == "cat":
                        cur_cat = await ctx.message.guild.create_category(chnl_nm)
                        succ_chns += 1
                    elif chnl_type == "tc":
                        await ctx.message.guild.create_text_channel(chnl_nm, category=cur_cat)
                        succ_chns += 1
                    elif chnl_type == "vc":
                        await ctx.message.guild.create_voice_channel(chnl_nm, category=cur_cat)
                        succ_chns += 1
                    else:
                        await ctx.send("Skipping invalid channel...")
            os.unlink(fo.name)
            await ctx.send(f"Operation complete. {len(succ_chns)} channels created.")
        except FileNotFoundError:
            await ctx.send("File not found. Make sure to include the complete path.")
        

    @commands.hybrid_command(name="cgmake", with_app_command=True,\
        description="clears all channels in guild, then creates new"\
        " channels from input file")
    @guild_owner_only()
    async def cgmake(self, ctx: commands.Context, infile: discord.Attachment):
        # confirm owner intentions
        await ctx.send("This action has significant impact on your guild and is irreversible. "\
            "Are you sure you would like to proceed? [Y/N]")

        def check(msg: discord.Message):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
            msg.content.lower() in ["y", "n", "yes", "no"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.send("Did not receive valid confirmation in time, cancelling guild channel wipe...")
            return
        if msg.content.lower() == "n" or msg.content.lower() == "no":
            await ctx.send("Cancelling guild channel wipe...")
            return
        else:
            await ctx.send("Initiating guild channel wipe...")
            # delete all channels except for ctx channel
            for chnl in ctx.message.guild.channels:
                if chnl != ctx.message.channel:
                    await chnl.delete()
            
            # create new channels
            await self.gmake(ctx, infile)
            await ctx.send("Guild channels remade. Deleting this channel in 30 seconds.")
            await asyncio.sleep(30)
            await ctx.message.channel.delete()
    
    @commands.hybrid_command(name="gmakesnap", with_app_command=True,\
        description="saves current channel layout as \"gmake\" text file")
    async def gmakesnap(self, ctx: commands.Context):
        # TODO
        pass

    @commands.hybrid_command(name="gmakeinter", with_app_command=True,\
        description="dynamically takes user input to create \"gmake\" text file")
    async def gmakeinter(self, ctx: commands.Context, des_filename: str):
        # parse filename
        await ctx.send("Parsing filename...")
        if des_filename.count('.') > 0:
            await ctx.send(f"{des_filename} is invalid, input filename cannot contain \'.\'.")
            return

        # internal function definitions
        def check(msg: discord.Message):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
            msg.content.lower() in ["y", "n", "yes", "no"]
        
        def check_chnl_type(msg: discord.Message):
            return msg.author == ctx.author and msg.channel == ctx.channel and \
            msg.content.lower() in ["t", "v", "tc", "vc", "text", "voice", "text channel", "voice channel"]
        
        def check_chnl_cont(msg: discord.Message):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content

        async def poll_cont(file_pointer: TextIOWrapper):
            # write channel to file_pointer
            await ctx.send("New channel. What type would you like it to be? [text/voice]")
            msg = await self.bot.wait_for("message", check=check_chnl_type)
            if msg.content.lower() == "t" or msg.content.lower() == "tc" or msg.content.lower() == "text" or msg.content.lower() == "text channel":
                file_pointer.write("tc:")
            elif msg.content.lower() == "v" or msg.content.lower() == "vc" or msg.content.lower() == "voice" or msg.content.lower() == "voice channel":
                file_pointer.write("vc:")
            await ctx.send("What name would you like this channel to have?")
            msg = await self.bot.wait_for("message", check=check_chnl_cont)
            file_pointer.write(f"{msg.content}\n")

            # check if user wants to create more channels in this category
            await ctx.send("Would you like to include another channel in this category? [Y/N]")
            msg = await self.bot.wait_for("message", check=check)
            if msg.content.lower() == "n" or msg.content.lower() == "no":
                return True
            return False

        # create new file
        fp = open(f"{des_filename}.txt", 'w')
        
        # interactive ops
        try:
            # get initial user confirmation
            await ctx.send("This command will guide you through an interactive process"\
            " to create a \"gmake\" text file with your desired channels. Are you ready"\
            " to proceed? [Y/N]")
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            if msg.content.lower() == "n" or msg.content.lower() == "no":
                await ctx.send("Cancelling operation...")
                return

            # create categoryless channels
            await ctx.send("Do you wish to include categoryless channels? [Y/N]")
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            if msg.content.lower() == "y" or msg.content.lower() == "yes":
                while True:
                    if await poll_cont(fp):
                        break
            
            # create category channels
            while True:
                await ctx.send("Do you wish to include a new category? [Y/N]")
                msg = await self.bot.wait_for("message", check=check, timeout=60)
                if msg.content.lower() == "y" or msg.content.lower() == "yes":
                    fp.write("cat:")
                    await ctx.send("What name would you like this category to have?")
                    msg = await self.bot.wait_for("message", check=check_chnl_cont)
                    fp.write(f"{msg.content}\n")

                    # create category member channels
                    await ctx.send("Do you wish to include new channels in this category? [Y/N]")
                    msg = await self.bot.wait_for("message", check=check, timeout=60)
                    if msg.content.lower() == "y" or msg.content.lower() == "yes":
                        while True:
                            if await poll_cont(fp):
                                break
                else:
                    break
            
            # send file to user and cleanup
            fp.close()
            try:
                await ctx.author.send(file=discord.File(fp=f"{des_filename}.txt"), content="Process complete. Here is your \"gmake\" text file.")
            except discord.Forbidden:
                await ctx.channel.send(file=discord.File(fp=f"{des_filename}.txt"), content="Process complete. Here is your \"gmake\" text file.")
            os.unlink(fp.name)
        except asyncio.TimeoutError:
            # clean up on communication failure
            await ctx.send("Did not receive communication in time, cancelling operation...")
            fp.close()
            os.unlink(fp.name)
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(Gmaker(bot))