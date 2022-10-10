import discord
from discord.ext import commands
# from discord.ext import commands // to be implemented later
from discord import client
from discord.utils import get
from dotenv import load_dotenv
from discord import colour as color
import getopt

load_dotenv()

DISCORD_TOKEN = 'OTI3NzY0MjQyOTY1MzQ0MzM3.YdO9yA.Q9Vx8UlVNEuv6HX0N_Z0t5Em-vo'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.command(name='make', help='[x] [name=BG_Group_] [role_make=False] create x private tc & vc, custom names optional,'
                               'associated roles optional')
async def make(ctx, count, name='BG_Group_', role_make=True):
    guild = ctx.message.guild
    dr = guild.default_role
    for ind in range(1, int(count)+1):
        cname = name + str(ind)
        # create custom category
        category = await guild.create_category(cname, overwrites=None, reason=None, position=None)
        # create tc
        tc = await guild.create_text_channel(cname, overwrites=None, category=category, reason=None)
        # create vc
        vc = await guild.create_voice_channel(cname, overwrites=None, category=category, reason=None)
        # if applicable, create role and assign permissions
        if role_make is True:
            role = await make_role(ctx, cname)
            await tc.set_permissions(dr, read_messages=False, send_messages=False)
            await tc.set_permissions(role, read_messages=True, send_messages=True, manage_channels=True)
            await vc.set_permissions(dr, connect=False, speak=False)
            await vc.set_permissions(role, connect=True, speak=True, manage_channels=True)

    await ctx.send('Created ' + str(count) + ' groups.')


@bot.command(name='clean', help='[name] removes all roles, tcs and vcs with name')
async def clean(ctx, name='BG_Group_'):
    guild = ctx.message.guild
    g_count = r_count = 0
    for ch in guild.channels:
        tc_name = format_to_tc(name)
        if (len(ch.name) >= len(name)+1 or len(ch.name) >= len(tc_name)+1) and \
        (ch.name[0:len(name)] == name or ch.name[0:len(tc_name)] == tc_name) and \
        (ch.name[len(name)].isdigit() or ch.name[len(tc_name)].isdigit()):
            await ch.delete()
            g_count += 1
        # elif len(ch.name) >= len(name)+1 and ch.name[0:len(name)] == name:
            # await ch.delete()
    for role in guild.roles:
        if len(role.name) >= len(name)+1 and role.name[0:len(name)] == name and role.name[len(name)].isdigit():
            await role.delete()
            r_count += 1
    await ctx.send(f"{g_count} groups cleaned, {r_count} roles cleaned.")

@bot.command(name='clean_spec', help='[name] [category=None] removes all tcs and vcs with name in category, \
    or those without a category if no category was specified')
async def clean_spec(ctx, name='BG_Group_', cat=None):
    """clears all channels with name from the given category"""
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
    await ctx.send(f"{cat} category not found.")

@bot.command(name='mtr', help='[role] [user1, user2, ...] give role to all listed members '
                              '(requires manage roles permission)')
async def mtr(ctx, role, *users):
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


async def mtr_2(ctx, role, users):
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
async def rmr(ctx, role, *users):
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


async def rmr_2(ctx, role, users):
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


def get_member(name, guild):
    """retrieves member object with nickname [name] and in guild [guild]"""
    for member in guild.members:
        if member.name == name or member.nick == name:
            return member
    return None


def get_role(role_str, guild):
    """retrieves role object with name [role] and in guilp[d [guild]"""
    for role in guild.roles:
        if role.name == role_str:
            return role
    return None

def format_to_tc(name):
    """converts name to text channel format"""
    lname = name.lower()
    return lname.replace(" ", "-")

@bot.command(name='make_role', help='[name] creates new role with given name')
async def make_role(ctx, role_name):
    guild = ctx.message.guild
    await ctx.send(f"{role_name} role created.")
    return await guild.create_role(reason=None, name=role_name)


@bot.command(name='rem_role', help='[name] removes all instances of role')
async def rem_role(ctx, role_name):
    guild = ctx.message.guild
    count = 0
    for role in await guild.fetch_roles():
        if role.name == role_name:
            await role.delete()
            count += 1
    await ctx.send(f"{count} instances of {role_name} removed.")


@bot.command(name='list_roles', help='lists all roles on server')
async def list_roles(ctx):
    guild = ctx.message.guild
    for role in await guild.fetch_roles():
        if "everyone" not in role.name:
            await ctx.send(role.name)
    await ctx.send(">> All roles listed.")


@bot.command(name='mult', help='use mult_help or mult -h for more info')
async def mult(ctx, *args):
    """general purpose command"""
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
async def mult_help(ctx):
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


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
