# Hunter Bot MkII

### Overview
The Hunter Bot MkII is a follow up implementation to the original Hunter Bot, and is intended for use when the original is muted by one or more users. This bot operates similarly to the Hunter Bot, but performs its "attack" immediately upon joining a guild, then leaves the guild. Specifying a target voice channel is WIP. More optimizations and modernization are a desired goal.

### Special Notes
1) To optimize operational efficiency, the MkII does not support hybrid commands and does not use Cog-based modularization.

### Command List

##### Main Suite (hunter_bot_mk_2.py)
```p```: Older version of the Hunter Bot's ```play_scrm``` command, left over for convenience but not intended for use. See the Hunter Bot for more details.<br />
```ping```: Same as standard utility command. Will be moved into ```cmdutils.py``` cog during future modernization.