from discord.ext import commands
from dotenv import load_dotenv
import random

load_dotenv()

DISCORD_TOKEN = 'OTE2OTM2Njg1NDk1OTMwODgw.YaxZ1Q.AvJc0NNPEdJcNbLiVFxaBdZDCIk'

bot = commands.Bot(command_prefix='%')
bot.delay = True  # global boolean for auto mode

teams = None


class Player:
    def __init__(self, skill, name):
        self.skill = skill
        self.name = name


class Teams:
    def __init__(self):
        self.player_count = 0
        self.player_arr = []


@bot.command(name='make_player', help='make_player [skill] [name] makes new player and adds it to Teams')
async def make_player(ctx, skill, name):
    global teams
    if skill.isdigit() is False:
        await ctx.send('Invalid skill')
    elif get_player(name) is True:
        await ctx.send('Player already entered')
    else:
        player = Player(skill, name)
        teams.player_arr.append(player)
        teams.player_count += 1
        await ctx.send('Player ' + player.name + ' made')


@bot.command(name='make_teams', help='creates 2 teams that are as balanced')
async def make_teams(ctx):
    global teams
    if len(teams.player_arr) == 0:
        await ctx.send('Teams are empty')
    else:
        teams.player_arr.sort(reverse=True, key=get_skill)
        shuffle_teams()
        for player in teams.player_arr:
            print(player.skill, player.name)
        for player in teams.player_arr:
            if teams.player_arr.index(player) % 2 == 0:
                await ctx.send('Team 1: ' + player.name)
            else:
                await ctx.send('Team 2: ' + player.name)


@bot.command(name='make_teams2', help='make_teams [count]: creates count teams')
async def make_teams2(ctx, count):
    pass


@bot.command(name='check_player', help='check_player [name]: see if a player of given name is already in the list')
async def check_player(ctx, name):
    if get_player(name) is not None:
        await ctx.send(name + ' is entered')
    else:
        await ctx.send(name + ' is not entered')


@bot.command(name='rem_player', help='rem_player [name]: remove player of given name from list')
async def rem_player(ctx, name):
    global teams
    player = get_player(name)
    if player is not None:
        teams.player_arr.remove(player)
        await ctx.send(name + ' removed')
    else:
        await ctx.send(name + ' is not entered')


@bot.command('rem_teams', help='clears teams')
async def rem_teams(ctx):
    global teams
    if len(teams.player_arr) == 0:
        await ctx.send('Teams are empty')
    else:
        teams.player_arr = []
        await ctx.send('Teams cleared')


def get_player(name):
    global teams
    for player in teams.player_arr:
        if player.name == name:
            return player
    return None


def get_skill(player):
    return player.skill


def shuffle_teams():
    global teams
    new_arr = []
    temp_arr = []
    skill = int(teams.player_arr[0].skill)
    print(skill)
    for player in teams.player_arr:
        print('player', player.name)
        if player.skill == skill:
            temp_arr.append(player)
        else:
            skill -= 1
            random.shuffle(temp_arr)
            new_arr = new_arr + temp_arr
            temp_arr = []
            temp_arr.append(player)
    teams.player_arr = new_arr


@bot.event
async def on_ready():
    print("bot ready")
    global teams
    teams = Teams()


@bot.command(name='ping', help='pingpong')
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
