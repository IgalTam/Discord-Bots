//! Reminder
//! Contains the struct definition and implementations for Reminder, as well as
//! all commands associated with scheduling and modifying Reminders.

use crate::ReminderStorageWrapper;

use serenity::framework::standard::macros::command;
use serenity::framework::standard::{Args, CommandResult};
use serenity::model::prelude::*;
use serenity::utils::MessageBuilder;
use serenity::prelude::*;
use chrono::{
    Duration,
    prelude::*,
};

#[derive(Debug)]
pub struct ReminderError;

/// Struct for storing reminder metadata.
pub struct Reminder {
    _rem_id: u32,
    rem_name: String,
    rem_msg: String,
    rem_author: String,
    rem_channel_id: ChannelId,
    rem_targ: Role,
    rem_expire: DateTime<Local>,
    rem_interval_type: String,
    rem_interval_qty: u32,
    next_poll: DateTime<Local>,
}

impl  Reminder {
    /// Creates a new Reminder object.
    pub fn new(id: u32, nm: String, msg: String, auth: String, chnl_id: ChannelId, targ: Role, 
               deadline: DateTime<Local>, ivt_type: String, ivt_qty: u32, next_poll: DateTime<Local>) -> Self {
        Reminder {
            _rem_id: id,
            rem_name: nm,
            rem_msg: msg,
            rem_author: auth,
            rem_channel_id: chnl_id,
            rem_targ: targ,
            rem_expire: deadline,
            rem_interval_type: ivt_type,
            rem_interval_qty: ivt_qty,
            next_poll: next_poll,
        }
    }

    /// Sets the next DateTime at which the reminder is to be posted after being polled.
    /// 
    /// Returns ```Ok(())``` on success, returns a ```ReminderError``` if an invalid ```rem_interval_type``` is stored.
    pub fn set_next_poll(&mut self) -> Result<(), ReminderError> {
        match self.rem_interval_type.as_str() {
            "day"=> self.next_poll += Duration::days(self.rem_interval_qty.into()),
            "hour" => self.next_poll += Duration::hours(self.rem_interval_qty.into()),
            "minute" => self.next_poll += Duration::minutes(self.rem_interval_qty.into()),
            _ => return Err(ReminderError),
        };
        Ok(())
    }

    /// Checks if the Reminder deadline has expired.
    /// 
    /// Returns a tuple of the form ```(has_expired, needs_post)```.
    /// ```has_expired``` is a boolean indicating whether the Reminder has expired 
    /// (its expiration DateTime is greater than the current DateTime). ```needs_post```
    /// is a boolean indicates whether the Reminder should be posted (with ```post_reminder```).
    pub async fn expired(&self) -> (bool, bool) {
        let cur_time = Local::now();
        if self.rem_expire <= cur_time && self.next_poll <= cur_time {  
            (true, true)     // reminder has expired, needs to be posted
        } else if self.rem_expire <= cur_time && self.next_poll > cur_time { 
            (true, false)     // reminder has expired, doesn't need to be posted
        } else if self.rem_expire > cur_time && self.next_poll <= cur_time {
            (false, true)     // reminder has not expired, needs to be posted
        } else {
            (false, false)  // reminder has not expired, doesn't need to be posted
        }
    }

    /// Posts the Reminder's stored message to the stored Channel.
    pub async fn post_reminder(&self, ctx: &Context) -> Result<(), ReminderError> {
        // get String of mention targets
        let mut mention_targs = String::new();
        mention_targs.push_str(&self.rem_targ.to_string());

        // build reminder message
        let post = MessageBuilder::new()
            .push(&self.rem_name)
            .push("\nReminder set by ")
            .push(&self.rem_author)
            .push("for ")
            .push(&mention_targs)
            .push(":\n")
            .push(&self.rem_msg)
            .push("\nReminder expires on ")
            .push(&self.rem_expire)
            .push(" (reminding every ")
            .push(self.rem_interval_qty)
            .push(" ")
            .push(&self.rem_interval_type)
            .push("(s)).")
            .build();

        // post reminder message
        if let Err(_) = self.rem_channel_id.say(&ctx.http, &post).await {
            return Err(ReminderError);
        }
        Ok(())
    }
}

/// Extracts the string contained within quotation marks (used for argument parsing).
/// 
/// Ex: assert_eq!(trim_quotes("\"arg_in_quotes\""), "arg_in_quotes");
fn trim_quotes(arg: String) -> String {
    arg.split("\"").collect()
}

#[command]
/// Describes command usage and syntax.
async fn help(ctx: &Context, msg: &Message) -> CommandResult {
    msg.reply(ctx,
        "This bot maintains a schedule of reminders that periodically ping in indicated channels \
        to remind a target group of an upcoming event.\nAvailable commands:\n\n \
        **help (this command)**: provides information on bot usage.\n\n \
        **set_reminder** `\"<event name>\" \"<event message>\" \"<name of target role>\" <expiration date (of the form \
        <YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>)> <posting interval type (day, hour, or minute)> <posting interval length \
        (whole number)>`:\n\tcreates and schedules a new Reminder that will mention members of a specific role on the \
        specified interval. The expiration date should be in 24 hour form. The posting interval cannot be less than 10 minutes.\n\n \
        **list_reminders**: lists all actively scheduled reminders and relevant metadata, including reminder IDs.\n\n \
        **cancel_reminder** `<ID>`: deschedules the reminder with the inputted ID, if able.\n\n \
        **update_reminder_name** `<ID> <new name>`: updates the specified reminder's event name.\n\n \
        **update_reminder_msg** `<ID> <new message>`: updates the specified reminder's event message.\n\n \
        **update_reminder_target** `<ID> <new target role>`: updates the specified reminder's targeted role.\n\n \
        **update_reminder_expiration** `<ID> <expiration date (of the form \
            <YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>)>`: updates the specified reminder's expiration date and time.\n\n \
        **update_reminder_interval** `<ID> <new interval type (day/hour/minute)> <new interval quantity>`: updates \
            the specified reminder's posting interval. The new interval cannot be less than 10 minutes.\n\n \
        **update_reminder_channel** `<ID> <new channel name>`: updates the reminder's channel for posting location. \
            By default, this channel is the one that the reminder's **set_reminder** was originally called in.
        "
    ).await?;

    Ok(())
}

#[command]
/// Creates a reminder and installs it in the global ReminderStorage.
/// 
/// Command Arguments:
/// - Reminder event name
/// - Reminder event message
/// - Reminder target role
/// - Reminder expiration date/time ("year/month/day/hour/minute/second")
/// - Reminder interval type (day, hour, or minute (must be at least 10 minutes))
/// - Reminder interval length (whole number)
async fn set_reminder(ctx: &Context, msg: &Message, args: Args) -> CommandResult {
    // check for all required arguments
    if args.len() != 6 {
        msg.reply(ctx, "Six arguments (event name, message, mentioned role, expiration deadline, interval type, interval length) required.").await?;
        return Ok(());
    }

    let mut args_copy = args.clone();

    // parse arguments
    let name_str = trim_quotes(args_copy.single::<String>()?);
    let msg_str = trim_quotes(args_copy.single::<String>()?);

    let rem_role: Role;
    if let Some(guild) = msg.guild(&ctx.cache) {
        let role_str = trim_quotes(args_copy.single::<String>()?);
        if let Some(role) = guild.role_by_name(role_str.as_str()) {
            rem_role = role.clone();
        } else {
            msg.reply(ctx, format!("Role {} not found in guild {}", role_str, guild.name)).await?;
            return Ok(());
        }
    } else {
        msg.reply(ctx, "Guild not found").await?;
        return Ok(());
    }

    let date_take = args_copy.single::<String>()?.clone();
    let date_str: Vec<&str> = date_take.split('/').collect();
    if date_str.len() != 6 {
        msg.reply(ctx, &"Invalid expiration date formatting 
            (requires <YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>)".to_string()).await?;
        return Ok(());
    }
    let xpr_datetime: DateTime<Local> = Local.with_ymd_and_hms(
        date_str[0].parse::<i32>().unwrap(),
        date_str[1].parse::<u32>().unwrap(),
        date_str[2].parse::<u32>().unwrap(),
        date_str[3].parse::<u32>().unwrap(),
        date_str[4].parse::<u32>().unwrap(),
        date_str[5].parse::<u32>().unwrap(),
    ).unwrap();
    if xpr_datetime < Local::now() {
        msg.reply(ctx, &"Invalid expiration date. Must be set after the current time.").await?;
        return Ok(());
    }

    let ivl_type_temp = args_copy.single::<String>()?;
    let ivl_type_str = ivl_type_temp.as_str();
    let ivl_qty_num = args_copy.single::<u32>()?;

    // get context data
    let rem_auth: String;
    if let Some(auth_str) = msg.author_nick(&ctx.http).await {  // get event requester nickname if possible
        rem_auth = auth_str;
    } else {
        rem_auth = msg.author.name.clone();                             // otherwise get the requester name
    }
    let rem_channel_id = msg.channel_id;                     // get channel ID of the request

    // configure the DateTime for the first Reminder ping
    let mut first_poll = Local::now();
    match ivl_type_str {
        "day" => first_poll += Duration::days(ivl_qty_num.into()),
        "hour" => first_poll += Duration::hours(ivl_qty_num.into()),
        "minute" => {
            if ivl_qty_num < 10 {
                msg.reply(ctx, "Invalid interval length, must be at least 10 minutes".to_string()).await?;
                return Ok(());
            }
            first_poll += Duration::minutes(ivl_qty_num.into());
        }
        _ => {
            msg.reply(ctx, "Invalid interval type (must be year, month, day, hour, or minute)".to_string()).await?;
            return Ok(());
        }
    };

    // read and update bot metadata
    let reminder_lock = {
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };

    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        let assgn_id = reminders.next_rem_id;   // retrieve next ID to be assigned to the new reminder
        let new_rem = Reminder::new(       // create new reminder
            assgn_id,
            name_str.clone(),
            msg_str,
            rem_auth,
            rem_channel_id,
            rem_role,
            xpr_datetime,
            ivl_type_str.to_string(),
            ivl_qty_num,
            first_poll,
        );
        reminders.reminders.insert(assgn_id, new_rem);  // insert new reminder into reminder scheduler
        reminders.next_rem_id += 1;                          // update next reminder ID
    }

    msg.reply(ctx, &format!("Reminder for {} is set. Use **list_reminders** to see relevant metadata.", name_str)).await?;

    Ok(())
}

#[command]
/// Cancels an active reminder based on its ID (can be found by using ```list_reminders```).
/// 
/// Command Argument: Reminder ID (whole number).
async fn cancel_reminder(ctx: &Context, msg: &Message, mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 1 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/cancel_reminder <reminderID>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;

    // remove reminder from ReminderStorage
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(extr_rem) = reminders.reminders.remove(&targ_id) {
            msg.reply(ctx, format!("Reminder {}: {} successfully descheduled.", targ_id, extr_rem.rem_name)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}

#[command]
/// Lists all active reminders and their relevant metadata.
async fn list_reminders(ctx: &Context, msg: &Message) -> CommandResult {

    // read and update bot metadata
    let reminder_lock = {
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };

    {
        let reminders = reminder_lock.write().await;    // open mutex lock for writing

        if reminders.reminders.is_empty() {
            msg.reply(&ctx.http, "No reminders are currently scheduled.").await?;
            return Ok(());
        }

        let mut output_message = String::new();
        output_message.push_str("Active Reminders:\n\n");
        for (rem_id, rem) in &reminders.reminders {
            output_message.push_str(format!("ID: {rem_id}\n\t\t{}, by {}.\n\t\tTargeting {}.\n\t\tActive in {}.\n\t\tExpires on {}. \
                \n\t\tPolling interval of {} {}(s).\n\t\tMessage: {}\n",
                rem.rem_name, rem.rem_author, rem.rem_targ.name, rem.rem_channel_id.to_channel(&ctx.http).await?.to_string(), rem.rem_expire,
                rem.rem_interval_qty, rem.rem_interval_type, rem.rem_msg).as_str());
        }
        msg.reply(&ctx.http, output_message).await?;
    }

    Ok(())
}

#[command]
/// Updates the `event name` field of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Name
async fn update_reminder_name(ctx: &Context, msg: &Message, mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 2 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/update_reminder_name <reminderID> <new_name>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;
    let new_rem_name = trim_quotes(args.single::<String>()?);

    // update target Reminder's name field
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_name = new_rem_name;
            msg.reply(ctx, format!("Reminder {}: Event name successfully changed to {}.", targ_id, targ_rem.rem_name)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}

#[command]
/// Updates the `event message` field of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Name
async fn update_reminder_message(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 2 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/update_reminder_message <reminderID> <new_message>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;
    let new_rem_msg = trim_quotes(args.single::<String>()?);

    // update target Reminder's event message field
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_msg = new_rem_msg;
            msg.reply(ctx, format!("Reminder {}: Event message successfully changed to {}.", targ_id, targ_rem.rem_msg)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}

#[command]
/// Updates the target role of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Target Role name (must be an actual Role in the guild)
async fn update_reminder_target(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 2 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/update_reminder_target <reminderID> <name_of_role>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;
    let new_rem_role: Role;
    if let Some(guild) = msg.guild(&ctx.cache) {
        let role_str = trim_quotes(args.single::<String>()?);
        if let Some(role) = guild.role_by_name(role_str.as_str()) {
            new_rem_role = role.clone();
        } else {
            msg.reply(ctx, format!("Role {} not found in guild {}", role_str, guild.name)).await?;
            return Ok(());
        }
    } else {
        msg.reply(ctx, "Guild not found").await?;
        return Ok(());
    }

    // update target Reminder's target role field
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_targ = new_rem_role;
            msg.reply(ctx, format!("Reminder {}: Target role successfully changed to {}.", targ_id, targ_rem.rem_targ.name)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}

#[command]
/// Updates the expiration deadline of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder expiration date/time ("year/month/day/hour/minute/second")
async fn update_reminder_expiration(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 2 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/update_reminder_expiration <reminderID> <<YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;
    let date_take = args.single::<String>()?.clone();
    let date_str: Vec<&str> = date_take.split('/').collect();
    if date_str.len() != 6 {
        msg.reply(ctx, &"Invalid expiration date formatting 
            (requires <YYYY>/<MM>/<DD>/<HH>/<MM>/<SS>)".to_string()).await?;
        return Ok(());
    }
    let new_xpr_datetime: DateTime<Local> = Local.with_ymd_and_hms(
        date_str[0].parse::<i32>().unwrap(),
        date_str[1].parse::<u32>().unwrap(),
        date_str[2].parse::<u32>().unwrap(),
        date_str[3].parse::<u32>().unwrap(),
        date_str[4].parse::<u32>().unwrap(),
        date_str[5].parse::<u32>().unwrap(),
    ).unwrap();
    if new_xpr_datetime < Local::now() {
        msg.reply(ctx, &"Invalid expiration date. Must be set after the current time.").await?;
        return Ok(());
    }

    // update target Reminder's expiration date/time field
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_expire = new_xpr_datetime;
            msg.reply(ctx, format!("Reminder {}: Expiration deadline successfully changed to {}.", targ_id, targ_rem.rem_expire)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}

#[command]
/// Updates the posting interval of the specified reminder. This change will not take effect
/// until the subsequent next posting of the reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Interval Type (day/hour/minute)
/// - New Reminder Interval Quantity (if type is "minute", this field cannot be less than 10)
async fn update_reminder_interval(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 3 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/update_reminder_interval <reminderID> <day/hour/minute> <number>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;
    let new_ivl_type = args.single::<String>()?;
    let new_ivl_qty_num = args.single::<u32>()?;

    // update target Reminder's interval type and quantity fields
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_interval_type = new_ivl_type;
            targ_rem.rem_interval_qty = new_ivl_qty_num;
            msg.reply(ctx, format!("Reminder {}: Interval successfully changed to {} {}(s).", 
                targ_id, targ_rem.rem_interval_qty, targ_rem.rem_interval_type)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}

#[command]
/// Updates the channel of the specified reminder. The default reminder channel is the one that ```set_reminder```
/// is initially called in.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Channel name (must be a text channel) 
async fn update_reminder_channel(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {
    // parse arguments
    if args.len() != 2 {
        msg.reply(ctx, "Invalid number of arguments. Usage: \"/%/update_reminder_channel <reminderID> <text channel name>.\"").await?;
        return Ok(());
    }
    let targ_id = args.single::<u32>()?;

    // find the new channel by ID, if able
    let chnl_name = trim_quotes(args.single::<String>()?);
    let new_chnl_id: ChannelId;
    if let Some(guild) = msg.guild(&ctx.cache) {
        if let Some(chnl_id) = guild.channel_id_from_name(&ctx.cache, chnl_name.clone()) {
            new_chnl_id = chnl_id.clone();
        } else {
            msg.reply(ctx, format!("Channel {} not found in guild {}", chnl_name, guild.name)).await?;
            return Ok(());
        }
    } else {
        msg.reply(ctx, "Guild not found").await?;
        return Ok(());
    }

    // update target Reminder's channel ID field
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_channel_id = new_chnl_id;
            msg.reply(ctx, format!("Reminder {}: Reminder channel successfully changed to {}.", 
                targ_id, chnl_name)).await?;
        } else {
            msg.reply(ctx, format!("Reminder {} not found in scheduler.", targ_id)).await?;
        }
    }

    Ok(())
}