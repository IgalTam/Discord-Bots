# Discord-Bots
Github containing my various Discord bot programs. Python-based scripts developed using the discord.py API.

##### General Required Dependencies
1) Python 3.11.1 ([found here](https://www.python.org/downloads/release/python-3111/)), or a similar version of Python
2) Additional Python Packages (use ```pip``` for installation, each page contains pip command for installing)<br />
   a) Discord.py 2.1.0 ([found here](https://pypi.org/project/discord.py/2.1.0/))

   b) For bots playing audio to a voice channel, use youtube_dl ([found here](https://pypi.org/project/youtube_dl/))

   c) Check the README in the directory of an individual bot for any additional packages to be installed

##### To use the bot code for yourself, complete the following:
1) In the directories of the bots you want to use, create a file called ```config.py``` and include a macro that matches the one in the main file of the corresponding bot. For instance, to use the Hunter Bot, in the directory ```Hunter Bot/```, create a file ```config.py``` that contains the line ```HUNTER = <your application token string>```. Check the README in the directory of an individual bot for any additional dependencies to be included in the bot's ```config.py``` file.
  
