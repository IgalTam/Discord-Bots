# Discord-Bots
Github containing my various Discord bot programs. Python-based scripts developed using the discord.py API.

##### General Required Dependencies
1) Python 3.11.1 ([found here](https://www.python.org/downloads/release/python-3111/)), or a similar version of Python
2) Additional Python Packages. Use ```pip``` for installation (all packages also contained in ```requirements.txt```):<br />
   a) Discord.py 2.1.0 ([found here](https://pypi.org/project/discord.py/2.1.0/))

   b) dotenv ([found here](https://pypi.org/project/python-dotenv/))

   c) For bots playing audio to a voice channel, PyNaCl is required ([found here](https://pypi.org/project/PyNaCl/))

   d) For bots playing audio to a voice channel, youtube_dl is required ([found here](https://pypi.org/project/youtube_dl/))

   e) Check the README in the directory of an individual bot for any additional packages to be installed

4) 3) Audio-based bots also require ```FFmpeg``` ([found here](https://ffmpeg.org/download.html)). See the next section for more on integration.

##### To use my bot code for yourself, do the following:
1) Create a new application for each bot you want to use through the [Discord developer portal](https://discord.com/developers/applications). There are numerous guides online to assist with this process.
2) In the directories of the bots you want to use, create a file called ```config.py``` and include a macro that matches the one in the main file of the corresponding bot. For instance, to use the Hunter Bot, in the directory ```Hunter Bot/```, create a file ```config.py``` that contains the line ```HUNTER = <your application token string>```. Check the README in the directory of an individual bot for any additional dependencies to be included in the bot's ```config.py``` file.
3) The config files for audio-based bots should contain a ```FFMPEG_PATH``` macro definition for the absolute path to your local ```ffmpeg.exe``` file.

##### Other Notes
1) Most of the active projects use Cogs for modularization, so feel free to create a bot with combined functionalities of my bots.
2) Most of the active projects support Hybrid commands, so using those bots' commands can be done either with their prefixes or with [slash commands](https://support.discord.com/hc/en-us/articles/1500000368501-Slash-Commands-FAQ). The slash command menu for applicable bots contains a *full list of commands, each of which has a short description and fillable parameters.<br /><br />
*Some bots are programmed with one or more utilities that are not compatible with slash commands. These must be run using standard prefix syntax, and are noted in individual project READMEs.

##### Common Modules
Most of my bot programs make use of common files containing several general purpose functions. As of the last update to this README, these files are ```bot_gen_utils.py``` (commonly used functions), ```botaudioutils.py``` (defines the Youtube_DL class used for audio-based bots), and the ```cmd_utils.py``` cog (useful user commands for bots to support). Here is a brief description of the functions and commands in ```bot_gen_utils.py``` and ```cmd_utils.py```:<br /><br />
__bot_gen_utils.py (functions)__<br />
```guild_find()```: Returns a discord.Guild object associated with the input guild name if the bot is a member of that guild<br />
```user_find()```: Returns a discord.Member object associated with the input username for a user who is a member of the input guild<br /><br />
__cmd_utils.py (commands)__<br />
```ping```: Pings the bot, which responds with the latency of the request<br />
```jchl```: The bot joins the message author's voice channel<br />
```lchl```: The bot leaves thea voice channel in the message's guild of origin to which it is already connected

##### Bot Access Token Macros (Active Projects)
As referred to earlier, each bot is programmed to import its access token from a macro in the corresponding ```config.py``` file. Here are the access macros of the active projects for reference:<br />
1) Bad Grouper: ```BAD_GRPR```
2) Hunter Bot: ```HUNTER``` (as referenced earlier)
3) Hunter Bot MkII: ```HUNTER2```
4) Impersonator Bot: ```IMPERS```
5) Vote Kicker: ```VOTEKICK```
