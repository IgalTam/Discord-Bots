# Hunter Bot

### Overview
This is a prank bot designed for jumpscaring voice channel users by playing the Hunter pouncing audio from Left 4 Dead and Left 4 Dead 2 (audio found [here](https://www.youtube.com/watch?v=G-ogxxcSZhM)). On request, the bot enters a specified voice channel, plays audio, then leaves the channel. A WIP feature is the ability to schedule a random time for the Hunter bot to "attack" a voice channel. Additionally, the Hunter Bot is compatible with the Hunter Bot MkII, providing a command to temporarily disable welcome messages on a server and automatically deleting all instances of messages mentioning the MkII. The Hunter Bot supports remote operation and can be activated from another guild.

### Special Notes
1) In the ```config.py``` file for this bot, include a macro ```HUNTER2_LNK```. This is intended for defining the invite link for the Hunter Bot MkII.
2) For guild safety and mitigating irresponsive actions, ```dw``` requires adminstrator permissions to use.
3) ```safety_disconnect``` is not intended for regular use, but can be called as a command if necessary.

### Command List

##### Main Suite (hunter_bot.py)
```play_scrm [guildn] [usern]```: Joins the voice channel of user with nickname _usern_ in guild _guildn_, plays audio, then leaves the channel. If not provided, _guildn_ defaults to the calling message's guild and _usern_ defaults to the calling message's author.<br />
```en_auto <delay>```: Calls ```play_scrm``` with default parameters after _delay_ minutes (command name is outdated).<br />
```en_auto_rand```: Same functionality as ```en_auto``` (command name is also outdated), but the delay is random.<br />
```get_system_flags```: Debug command that prints the system flags of the calling message's guild.<br />
```dw [dur] [guildn]```: Disables the welcome messages in guild _guildn_ for _dur_ seconds. If not provided, _guildn_ defaults to the calling message's guild and _dur_ defaults to 30.<br />
```jchl_spec [usrn] [guildn]```: Variant of standard utility ```jchl``` optimized for remote operation, causing the bot to join the voice channel of user _usrn_ in guild _guiln_. Same defaults as ```play_scrm```.