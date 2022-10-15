import discord
from discord.ext import commands
# from discord.ext import commands // to be implemented later
from discord import client
from discord.utils import get
from dotenv import load_dotenv
from discord import colour as color
import getopt
import asyncio

load_dotenv()

DISCORD_TOKEN = 'OTI3NzY0MjQyOTY1MzQ0MzM3.YdO9yA.Q9Vx8UlVNEuv6HX0N_Z0t5Em-vo'

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix="/*/", intents=intents)
    
    async def setup_hook(self) -> None:
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

bot = Bot() # bot initialization

# @bot.command(name='make', help='[x] [name=BG_Group_] [role_make=False] create x private tc & vc, custom names optional,'
#                                'associated roles optional')
@bot.hybrid_command(name = "make", with_app_command=True, description="create x private tc & vc, \
    custom names optional, associated roles optional")
@commands.has_permissions(administrator=True)
async def make(ctx: commands.Context, count, name, role_make=False):
    await ctx.send("Creating groups...")
    guild = ctx.message.guild
    dr = guild.default_role
    for ind in range(1, int(count)+1):
        cname = name + str(ind)
        # create custom category
        category = await guild.create_category(cname, reason=None, position=None)
        # create tc
        tc = await guild.create_text_channel(cname, category=category, reason=None)
        # create vc
        vc = await guild.create_voice_channel(cname, category=category, reason=None)
        # if applicable, create role and assign permissions
        if role_make is True:
            role = await make_role(ctx, cname)
            await tc.set_permissions(dr, read_messages=False, send_messages=False)
            await tc.set_permissions(role, read_messages=True, send_messages=True, manage_channels=True)
            await vc.set_permissions(dr, connect=False, speak=False)
            await vc.set_permissions(role, connect=True, speak=True, manage_channels=True)
    await ctx.send("Created " + str(count) + " groups.")


# @bot.command(name='clean', help='[name] removes all roles, tcs and vcs with name')
@bot.hybrid_command(name = "clean", with_app_command=True, description="removes all roles, tcs and vcs created \
    by Bad Grouper with name")
@commands.has_permissions(administrator=True)
async def clean(ctx: commands.Context, name):
    await ctx.send("Cleaning...")
    guild = ctx.message.guild
    g_count = r_count = 0
    for ch in guild.channels:
        tc_name = format_to_tc(name)
        if (len(ch.name) >= len(name)+1 or len(ch.name) >= len(tc_name)+1) and \
        (ch.name[0:len(name)] == name or ch.name[0:len(tc_name)] == tc_name) and \
        (ch.name[len(name)].isdigit() or ch.name[len(tc_name)].isdigit()):
            await ch.delete()
            g_count += 1
    for role in guild.roles:
        if len(role.name) >= len(name)+1 and role.name[0:len(name)] == name and role.name[len(name)].isdigit():
            await role.delete()
            r_count += 1
    await ctx.send(f"{g_count} channels cleaned, {r_count} roles cleaned.")

@bot.command(name='clean_spec', help='[name] [category=None] removes all tcs and vcs with name in category, \
    or those without a category if no category was specified')
# @bot.hybrid_command(name="clean_spec", with_app_command=True, description="removes all tcs and vcs with name in category, \
#     or those without a category if no category was specified")
async def clean_spec(ctx: commands.Context, name, cat=None):
    """clears all channels with name from the given category"""
    # [WIP] bugfix to enable hybrid command compatibility
    guild = ctx.message.guild
    g_count = 0
    if cat is None: # if category is none, check each channel with category none
        for ch in guild.channels:
            if ch.category is None:
                print(ch.name)
                tc_name  = format_to_tc(name)
                if ch.name[0:len(name)] == name or ch.name[0:len(tc_name)] == tc_name:
                    await ch.delete()
                    g_count += 1
        if g_count == 0:
            await ctx.send("No channels cleaned.")
        else:
            await ctx.send(f"{g_count} channels successfully cleaned.")
        return
    else:
        for cat_y in guild.categories:  # find category
            if cat_y.name == cat:
                for ch in cat_y.channels:   # clear channel(s)
                    print(ch.name)
                    tc_name  = format_to_tc(name)
                    if ch.name[0:len(name)] == name or ch.name[0:len(tc_name)] == tc_name:
                        await ch.delete()
                        g_count += 1
                if g_count == 0:
                    await ctx.send("No channels cleaned.")
                else:
                    await ctx.send(f"{g_count} channels successfully cleaned.")
                return
        await ctx.send(f"{g_count} category not found.")

@bot.command(name='mtr', help='[role] [user1, user2, ...] give role to all listed members '
                              '(requires manage roles permission)')
async def mtr(ctx: commands.Context, role, *users):
    guild = ctx.message.guild
    role_obj = get_role(role, guild)
    if ctx.message.author.guild_permissions.manage_roles is False:
        await ctx.send('You do not have permission to use this command!')
    elif role_obj is None:
        await ctx.send(f'{role} is not a valid role on this server.')
    else:
        for user in users:
            upd_user = get_member(user, guild)
            if upd_user is None:
                await ctx.send(f"{user} is not a member of this server.")
                return
            try:
                await upd_user.add_roles(role_obj)
            except discord.errors.Forbidden:
                await ctx.send(f"Cannot give {role} to {user}!")
        await ctx.send('{} now have {} role'.format(users, role))


async def mtr_2(ctx: commands.Context, role, users):
    """version compatible with mult"""
    guild = ctx.message.guild
    role_obj = get_role(role, guild)
    conf_usrs = []
    if ctx.message.author.guild_permissions.manage_roles is False:
        await ctx.send('You do not have permission to use this command!')
    elif role_obj is None:
        await ctx.send(f'{role} is not a valid role on this server.')
    else:
        for user in users:
            upd_user = get_member(user, guild)
            if upd_user is None:
                await ctx.send(f"{user} is not a member of this server.")
                return
            try:
                await upd_user.add_roles(role_obj)
                conf_usrs.append(user)
            except discord.errors.Forbidden:
                await ctx.send(f"Cannot give {role} to {user}!")
        if len(conf_usrs) > 0:
            await ctx.send('{} now have {} role'.format(conf_usrs, role))


@bot.command(name='rmr', help='[role] [user1, user2, ...] remove role from all listed members '
                              '(requires manage roles permission)')
# @bot.hybrid_command(name="rmr", with_app_command=True, description="remove role from all listed members \
#                                 (requires manage roles permission)")
async def rmr(ctx: commands.Context, role, *users):
    # variable argument count not yet supported for hybrid/slash commands
    guild = ctx.message.guild
    role_obj = get_role(role, guild)
    if ctx.message.author.guild_permissions.manage_roles is False:
        await ctx.send('You do not have permission to use this command!')
    elif role_obj is None:
        await ctx.send(f'{role} is not a valid role on this server.')
    else:
        end_users = []
        for user in users:
            upd_user = get_member(user, guild)
            if upd_user is None:
                await ctx.send(f"{user} is not a member of this server.")
                return
            try:
                await upd_user.remove_roles(role_obj)
                end_users.append(user)
            except discord.errors.Forbidden:
                await ctx.send(f"Cannot remove {role} from {user}!")
        if len(end_users) >= 1:
            await ctx.send('{} removed from {}'.format(role, end_users))


async def rmr_2(ctx: commands.Context, role, users):
    """version compatible with mult"""
    guild = ctx.message.guild
    role_obj = get_role(role, guild)
    if ctx.message.author.guild_permissions.manage_roles is False:
        await ctx.send('You do not have permission to use this command!')
    elif role_obj is None:
        await ctx.send(f'{role} is not a valid role on this server.')
    else:
        end_users = []
        for user in users:
            upd_user = get_member(user, guild)
            if upd_user is None:
                await ctx.send(f"{user} is not a member of this server.")
                return
            try:
                await upd_user.remove_roles(role_obj)
                end_users.append(user)
            except discord.errors.Forbidden:
                await ctx.send(f"Cannot remove {role} from {user}!")
        if len(end_users) >= 1:
            await ctx.send('{} removed from {}'.format(role, end_users))


def get_member(name, guild: discord.Guild):
    """retrieves member object with nickname [name] and in guild [guild]"""
    for member in guild.members:
        if member.name == name or member.nick == name:
            return member
    return None


def get_role(role_str, guild: discord.Guild):
    """retrieves role object with name [role] and in guilp[d [guild]"""
    for role in guild.roles:
        if role.name == role_str:
            return role
    return None

def format_to_tc(name: str):
    """converts name to text channel format"""
    lname = name.lower()
    return lname.replace(" ", "-")

# @bot.command(name='make_role', help='[name] creates new role with given name')
@bot.hybrid_command(name="make_role", with_app_command=True, description="creates new role with given name")
async def make_role(ctx: commands.Context, role_name):
    guild = ctx.message.guild
    await ctx.send(f"{role_name} role created.")
    return await guild.create_role(reason=None, name=role_name)


# @bot.command(name='rem_role', help='[name] removes all instances of role')
@bot.hybrid_command(name="rem_role", with_app_command=True, description="removes all instances of role with given name")
async def rem_role(ctx: commands.Context, role_name):
    guild = ctx.message.guild
    count = 0
    for role in await guild.fetch_roles():
        if role.name == role_name:
            await role.delete()
            count += 1
    await ctx.send(f"{count} instances of {role_name} removed.")


# @bot.command(name='list_roles', help='lists all roles on server')
@bot.hybrid_command(name="list_roles", with_app_command=True, description="lists all roles on server")
async def list_roles(ctx: commands.Context):
    guild = ctx.message.guild
    role_str = ""
    for role in await guild.fetch_roles():
        if "everyone" not in role.name:
            role_str += f"{role.name}\n"
    await ctx.send(role_str)
    await ctx.send(">> All roles listed.")


@bot.command(name='mult', help='use mult_help or mult -h for more info')
async def mult(ctx: commands.Context, *args):
    """general purpose command"""
    # variable argument count not yet supported for hybrid/slash commands
    role = make_b = clean_b = move = chan_role = role_del = False
    role_name = group_name = clean_name = move_name = role_del_name = None
    count = 0
    rorm = -1
    if args is None:
        await ctx.send("Insufficient parameters!")
    else:
        try:
            opts, args = getopt.getopt(args, "hr:R:m:M:Ac:v:ge")
        except getopt.GetoptError as err:
            await ctx.send(err)
        for o, a in opts:
            if o == "-h":
                await mult_help(ctx)
                return
            elif o == "-R":
                role_del = True
                role_del_name = a
            elif o == "-r":
                role = True
                role_name = a
            elif o == '-A':
                chan_role = True
            elif o == "-M":
                make_b = True
                count = a
            elif o == "-m":
                group_name = a
            elif o == "-c":
                clean_b = True
                clean_name = a
            elif o == "-v":
                move = True
                move_name = a
            elif o == "-g":
                if len(args) == 0:
                    await ctx.send("No users to move.")
                    return
                rorm = 0
            elif o == "-e":
                if rorm == 0:
                    await ctx.send("-g and -e are incompatible.")
                    return
                if len(args) == 0:
                    await ctx.send("No users to move.")
                    return
                rorm = 1
            else:
                await ctx.send(f"{a}: Unhandled Option.")

        # set defaults in event of specific missing parameters
        if make_b is False and group_name is not None:
            # -m provided with no -M
            await ctx.send("-m: Defaulting to 1 group.")
            make_b = True
            count = 1

        # order of execution: c -> r -> m -> v/g/e
        if clean_b is True:
            try:
                await clean(ctx, clean_name)
            except discord.errors.HTTPException as err:
                await ctx.send("Name must be between 1 and 100 characters in length.")
        if role_del is True:
            try:
                await rem_role(ctx, role_del_name)
            except discord.errors.HTTPException as err:
                await ctx.send("Name must be between 1 and 100 characters in length.")
        if role is True:
            try:
                await make_role(ctx, role_name)
            except discord.errors.HTTPException as err:
                await ctx.send("Name must be between 1 and 100 characters in length.")
        if make_b is True:
            try:
                await make(ctx, count, group_name, chan_role)
            except discord.errors.HTTPException as err:
                await ctx.send("Name must be between 1 and 100 characters in length.")
        if move is True:
            try:
                if rorm == 0:
                    await mtr_2(ctx, move_name, args)
                elif rorm == 1:
                    await rmr_2(ctx, move_name, args)
                elif rorm == -1:
                    await ctx.send("Insufficient moving options provided, -g or -e required.")
            except discord.errors.HTTPException as err:
                await ctx.send("Name must be between 1 and 100 characters in length.")
        await ctx.send("End of mult.")


@bot.command(name='mult_help', help='explains mult (think Unix man pages)')
async def mult_help(ctx: commands.Context):
    """essentially a man page for mult"""
    await ctx.send("mult -r [name='BG_Group_'] -R [name] -A -m [name='BG_Group_'] -M [count] -c [name='BG_Group_'] "
                   "-v [name] -g -e [usr1, usr2, ...]\n-r [name='BG_Group_']: create role with name\n-R [name]: "
                   "removes role with name\n-A: create role for channels (requires -M)\n-m "
                   "[name='BG_Group_']: create tcs & vcs with name\n-M [count]: number of groups to make\n-c "
                   "[name='BG_Group_']: clean all channels & roles with name\n-v [name]: move all listed users with "
                   "role, list at end of command\n-g: give role to users, requires -v\n-e: remove role from users, "
                   "requires -v\n-h: shows this page, overrides other options")

@bot.event
async def on_ready():
    print("bot ready")


# @bot.command(name='ping', help='pingpong')
@bot.hybrid_command(name="ping", with_app_command=True, description="pingpong")
async def ping(ctx: commands.Context):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
