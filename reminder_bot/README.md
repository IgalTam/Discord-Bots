# Reminder Bot

### Overview
The Reminder Bot is a Rust-based Discord bot that is implemented with a low-level Rust-based Discord library. The bot allows for the scheduling of reminder instances for events, which will periodically appear as messages sent in a text channel pinging a specific role on the server. Upon startup, the bot installs and maintains an event handler that polls all active reminders every minute. Reminder metadata is fully configurable through available commands. Due to not being programmed using discord.py, the unique details of this bot can be found in the **Special Notes** section.

### Special Notes
1) Reminder Bot is programmed in Rust v1.70, using the [Serenity Discord bot library](https://github.com/serenity-rs/serenity) among other Rust crates. Serenity's MSRV (minimum supported Rust version) should be enough to run this program, and all other dependencies will be downloaded during compilation. Downloading Rust itself can be found [here](https://www.rust-lang.org/tools/install).
2) To use this bot, within the ```reminder_bot``` workspace (the directory that this readme is located in), run ```cargo run``` to activate the bot.
Alternatively, use ```cargo build``` to compile the code and dependencies.
3) As an additional requirement for running this bot, create a ```.env``` file in this directory. This file should contain the following:<br />
```
REMINDER_BOT_TOKEN="<your bot token>"
RUST_LOG=debug
PREFIX="<command prefix of your choice>"
```

### Command List

##### Main Suite (reminder_bot/src/*)
```ping```: Pings the bot. Use to check if Reminder Bot is currently active and functioning.<br />
```help (slash command)```: Indicates the configured prefix, and directs towards the prefix ```help``` variant.<br />
```help (prefix command)```: Describes basic functionality and list of prefix commands.<br />
**NOTE: ALL FURTHER COMMANDS ARE AVAILABLE AS BOTH PREFIX AND SLASH COMMANDS**<br />
```set_reminder "[event_name]" "[event_message]" "[target_role>]" [expiration_date (of the form <YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>)] [interval_type (day, hour, or minute)] [interval_length (whole number)]```: Creates and schedules a new Reminder with name *event_name* that will mention members of *target_role* on the specified interval via a Discord message in the channel that this command was called in. This message will also contain *event_message*, *expiration_date*, *interval_type*, and *interval_length*. The expiration date should be in 24 hour form, and the posting interval cannot be less than 10 minutes.<br />
```list_reminders```: Lists all actively scheduled reminders and relevant metadata, including reminder IDs.<br />
```cancel_reminder [id]```: Deschedules the reminder with ID _id_, if able.<br />
```update_reminder_name [id] [new_name]```: Updates the reminder with ID _id_ to have the event name *new_name*, if able.<br />
```update_reminder_msg [id] [new_msg]```: Updates the reminder with ID _id_ to have the event message *new_msg*, if able.<br />
```update_reminder_target [id] [new_target_role]```: Updates the reminder with ID _id_ to have the target role *new_target_role*, if able.<br />
```update_reminder_expiration [id] [new_expiration_date (of the form <YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>)]```: Updates the reminder with ID _id_ to have the expiration date/time *new_expiration_date*, if able.<br />
```update_reminder_interval [id] [new_interval_type (day/hour/minute)] [new_interval_length]```: Updates the reminder with ID _id_ to have the posting interval represented by *new_interval_type* and *new_interval_length*, if able. The new interval cannot be less than 10 minutes.<br />
```update_reminder_channel [id] [new_channel_name]```: Updates the reminder with ID _id_ to have the text channel *new_channel_name* for posting location. By default, this channel is the one that the reminder's ```set_reminder``` was originally called in.