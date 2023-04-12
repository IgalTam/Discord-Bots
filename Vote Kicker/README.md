# Impersonator Bot

### Overview
This bot is designed for creating quick, arbitrary voting prompts. The Votekicker can host direct votes for kicking a member from a voice channel or timing them out (as per the defined Discord moderator action), and allows for general purpose votes with up to ten options. This bot has not yet been modernized to feature Cog-based modularization but does support Slash commands.

### Special Notes
1) In the ```config.py``` file for this bot, include a macro ```OP_ID_EXT```. This is an integer intended to be the ID associated with your Discord account, with the purpose of preventing you from being affected by ```votetimeout``` and ```votekick``` while developing this bot.
2) Voting is facilitated by means of reactions to bot-produced messages. The bot provides all possible reactions for each vote, and determines the winning outcome based on the option with the greatest amount of reactions. Ties are not exceptional unless explicitly mentioned.

### Command List

##### Main Suite (vote_kicker.py)
```votetimeout <kicked> <dur> [timer]```: Holds a "yes/no" vote for _timer_ seconds to determine whether the user _kicked_ will be timed out for _dur_ seconds. Ties are treated as "no". If not provided, _timer_ defaults to 30. Requires some administrative privileges.<br />
```votekick <kicked> [timer]```: Holds a "yes/no" vote for _timer_ seconds to determine whether the user _kicked_ will be kicked from their voice channel. Ties are treated as "no". If not provided, _timer_ defaults to 30.<br />
```genvote <message> [timer]```: Holds a "yes/no" vote for _timer_ seconds for the given prompt _message_. If not provided, _timer_ defaults to 30.<br />
```genmultvote <msg1> <msg2> [msg3] ... [msg10] [timer]```: Holds a multiple choice vote for _timer_ seconds with provided options _msg1_, _msg2_, ..., _msg10_. Each message prompt after _msg1_ and _msg2_ is optional.<br />
```ping```: Same as standard utility command. Will be moved into ```cmdutils.py``` cog during future modernization.
