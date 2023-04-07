# Discord-Bots
Github containing my various Discord bot programs. Python-based scripts developed using the discord.py API.

##### General Required Dependencies
1) Python 3.11.1 ([found here](https://www.python.org/downloads/release/python-3111/)), or a similar version of Python
2) Additional Python Packages (use ```pip``` for installation, each page contains pip command for installing)<br />
   a) Discord.py 2.1.0 ([found here](https://pypi.org/project/discord.py/2.1.0/))

   b) For bots playing audio to a voice channel, youtube_dl is required ([found here](https://pypi.org/project/youtube_dl/))

   c) Check the README in the directory of an individual bot for any additional packages to be installed

##### To use my bot code for yourself, do the following:
1) Create a new application for each bot you want to use through the [Discord developer portal](https://discord.com/developers/applications). There are numerous guides online to assist with this process.
2) In the directories of the bots you want to use, create a file called ```config.py``` and include a macro that matches the one in the main file of the corresponding bot. For instance, to use the Hunter Bot, in the directory ```Hunter Bot/```, create a file ```config.py``` that contains the line ```HUNTER = <your application token string>```. Check the README in the directory of an individual bot for any additional dependencies to be included in the bot's ```config.py``` file.

##### Other Notes
1) The active projects use Cogs for modularization, so feel free to create a bot with combined functionalities of my bots.
2) The active projects support Hybrid commands, so using those bots' commands can be done either with their prefixes or with [slash commands](https://support.discord.com/hc/en-us/articles/1500000368501-Slash-Commands-FAQ). The slash command menu for applicable bots contains a *full list of commands, each of which has a short description and fillable parameters.<br /><br />
*Some bots are programmed with one or more utilities that are not compatible with slash commands. These must be run using standard prefix syntax, and are noted in individual project READMEs.
