# Impersonator Bot

### Overview
This bot was originally designed to emulate the behavior of the Hunter Bot, but with different audio. However, the design has been expanded upon to enable the impersonation of a target user. The bot takes on the nickname, profile picture, and activity of the target. Additionally, it can be set to appear offline or online and can join/leave a voice channel of the user's choice. The bot can also retrieve the image file for a user or guild, and can be remotely operated like the Hunter Bot.

### Special Notes
1) In the ```config.py``` file for this bot, include a macro ```DEF_PFP_PATH```. This should be an absolute path to the image file that you want your bot's profile picture to default to for ```sb``` calls.
2) Due to limits on the frequency of profile customization allowed by the Discord client, one or more components of ```gb``` may fail if used repeatedly in a small time interval.

### Command List

##### Main Suite (impersonator.py)
```mp [guildn] [usrn]```: Aside from the audio played, parallels the functionality of the Hunter Bot's ```play_scrm``` command.<br />
```gb <usrn> [guildn]```: Impersonates the user _usrn_ in the guild _guildn_ as described in the Overview. If not provided, _guildn_ defaults to the calling message's guild.<br />
```sd [guildn]```: Resets the bot to its default appearance in the guild _guildn_. If not provided, _guildn_ defaults to the calling message's guild.<br />
```gpp <usrn> [guildn]```: Sends the stored image file for the profile picture of the user _usrn_ in guild _guildn_ to the calling message's text channel. If not provided, _guildn_ defaults to the calling message's guild.<br />
```gsp <usrn> [guildn]```: Sends the stored image file for the profile picture of the guild _guildn_ to the calling message's text channel.<br />
```go_offline```: Sets the bot's status to be offline.<br />
```go_online```: Sets the bot's status to be online.<br />
```jchl_spec [usrn] [guildn]```: Variant of standard utility ```jchl``` optimized for remote operation, causing the bot to join the voice channel of user _usrn_ in guild _guiln_. Same defaults as ```mp```. As with ```mp```, this command parallels the command of the same name implemented for the Hunter Bot.
