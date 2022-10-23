import discord
from discord.ext import commands
import asyncio

class Gmaker(commands.Cog):
    """commands for creating guild channels from input files
    and creating input files via interactive input"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Gmaker Cog loaded.")
    
    @commands.hybrid_command(name="gmake", with_app_command=True,\
        description="creates channels based on an input file")
    async def gmake(self, ctx: commands.Context, infile: discord.Attachment):
        
        # parse file
        await ctx.send("Parsing file...")
        if(infile.filename[len(infile.filename)-4:] != ".txt"):
            await ctx.send(f"{infile} is invalid, input must be .txt.")
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
            for chnl in chnls: # processing individual channel names
                if chnl.count(':') != 1:
                    await ctx.send("Skipping invalid channel...")
                else:
                    chnl_arr = chnl.split(':')
                    chnl_type, chnl_nm = chnl_arr[0], chnl_arr[1]
                    if chnl_type == "cat":
                        cur_cat = await ctx.message.guild.create_category(chnl_nm)
                    elif chnl_type == "tc":
                        await ctx.message.guild.create_text_channel(chnl_nm, category=cur_cat)
                    elif chnl_type == "vc":
                        await ctx.message.guild.create_voice_channel(chnl_nm, category=cur_cat)
                    else:
                        await ctx.send("Skipping invalid channel...")
            await ctx.send(f"Operation complete. {len(chnls)} channels created.")
        except FileNotFoundError:
            await ctx.send("File not found. Make sure to include the complete path.")
        

    @commands.hybrid_command(name="cgmake", with_app_command=True,\
        description="clears all channels in guild, then creates new"\
        " channels from input file")
    @commands.has_permissions(administrator=True)
    async def cgmake(self, ctx: commands.Context, infile: discord.Attachment):
        for chnl in ctx.message.guild.channels:
            if chnl != ctx.message.channel:
                await chnl.delete()
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
    async def gmakeinter(self, ctx: commands.Context):
        # TODO
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Gmaker(bot))