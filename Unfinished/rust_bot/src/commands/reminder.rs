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

// trait MentionShowable: Mentionable + std::fmt::Display {}

/// Struct for storing reminder metadata.
pub struct Reminder {
    _rem_id: u32,
    rem_name: String,
    rem_msg: String,
    // rem_author: Member,
    rem_author: String,
    // rem_channel: Channel,
    rem_channel_id: ChannelId,
    // rem_targs: Vec<Role>,
    rem_targ: Role,
    // rem_targs: Vec<String>,
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
            "day"=> self.next_poll.checked_add_signed(Duration::days(self.rem_interval_qty.into())).unwrap(),
            "hour" => self.next_poll.checked_add_signed(Duration::hours(self.rem_interval_qty.into())).unwrap(),
            "minute" => self.next_poll.checked_add_signed(Duration::minutes(self.rem_interval_qty.into())).unwrap(),
            _ => return Err(ReminderError),
        };
        Ok(())
    }

    /// Checks if the Reminder deadline has expired.
    /// 
    /// Returns a tuple of the form ```(has_expired, needs_post, current_time)```.
    /// ```has_expired``` is a boolean indicating whether the Reminder has expired 
    /// (its expiration DateTime is greater than the current DateTime). ```needs_post```
    /// is a boolean indicates whether the Reminder should be posted (with ```post_reminder```).
    /// ```current_time``` is the current DateTime object obtained in this method, passed along
    /// for further calculations.
    pub async fn expired(&self) -> (bool, bool, DateTime<Local>) {
        let cur_time = Local::now();
        if self.rem_expire >= cur_time && self.next_poll >= cur_time {  
            (true, true, cur_time)     // reminder has expired, needs to be posted
        } else if self.rem_expire >= cur_time && self.next_poll < cur_time { 
            (true, false, cur_time)     // reminder has expired, doesn't need to be posted
        } else if self.rem_expire < cur_time && self.next_poll >= cur_time {
            (false, true, cur_time)     // reminder has not expired, needs to be posted
        } else {
            (false, false, cur_time)  // reminder has not expired, doesn't need to be posted
        }
    }

    /// Posts the Reminder's stored message to the stored Channel.
    pub async fn post_reminder(&self, ctx: &Context, cur_time: DateTime<Local>) -> Result<(), ReminderError> {
        // evaluate remaining duration on timer
        if self.rem_expire < cur_time {
            return Err(ReminderError);
        }
        let remaining_duration = self.rem_expire - cur_time;

        // get String of mention targets
        let mut mention_targs = String::new();        
        // for targ in &self.rem_targs {
        //     mention_targs.push('@');
        //     mention_targs.push_str(&targ.name);
        //     mention_targs.push(' ');
        // }
        mention_targs.push_str(&self.rem_targ.to_string());

        // build reminder message
        let post = MessageBuilder::new()
            .push(&self.rem_name)
            .push("\nReminder set by ")
            // .mention(&self.rem_author)
            .push(&self.rem_author)
            .push("for ")
            // .mention(&self.rem_targs)
            .push(&mention_targs)
            .push(":\n")
            .push(&self.rem_msg)
            .push("\nEvent set for ")
            .push(&remaining_duration)
            .push(" (reminding every ")
            .push(self.rem_interval_qty)
            .push(" ")
            .push(&self.rem_interval_type)
            .push(").")
            .build();

        // post reminder message
        if let Err(_) = self.rem_channel_id.say(&ctx.http, &post).await {
            return Err(ReminderError);
        }
        Ok(())
    }
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
    let name_str = args_copy.single::<String>()?;
    let msg_str = args_copy.single::<String>()?;

    let rem_role: Role;
    if let Some(guild) = msg.guild(&ctx.cache) {
        let role_str = args_copy.single::<String>()?;
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
            (requires <year>/<month>/<day>/<hour>/<minute>/<second>)".to_string()).await?;
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
    let first_poll = Local::now();
    match ivl_type_str {
        "day" => first_poll.checked_add_signed(Duration::days(ivl_qty_num.into())).unwrap(),
        "hour" => first_poll.checked_add_signed(Duration::hours(ivl_qty_num.into())).unwrap(),
        "minute" => {
            if ivl_qty_num < 10 {
                msg.reply(ctx, "Invalid interval length, must be at least 10 minutes".to_string()).await?;
                return Ok(());
            }
            first_poll.checked_add_signed(Duration::minutes(ivl_qty_num.into())).unwrap()
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

    msg.reply(ctx, &format!("Reminder for {} is set.", name_str)).await?;

    Ok(())
}

// ///
// #[command]
// async fn cancel_reminder(ctx: &Context, msg: &Message, mut args: Args) -> CommandResult {

//     Ok(())
// }

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
        for (rem_id, rem) in &reminders.reminders {
            output_message.push_str(format!("Reminder {rem_id}:\n\t\t{}, by {}.\n\t\tActive in {}.\n\t\tExpires on {}. \
                \n\t\tPolling interval of {} {}(s).\n\t\tMessage: {}\n", 
                rem.rem_name, rem.rem_author, rem.rem_channel_id.to_channel(&ctx.http).await?.to_string(), rem.rem_expire,
                rem.rem_interval_qty, rem.rem_interval_type, rem.rem_msg).as_str());
        }
        msg.reply(&ctx.http, output_message).await?;
    }

    Ok(())
}

// ///
// #[command]
// async fn update_reminder_message(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

//     Ok(())
// }

// ///
// #[command]
// async fn update_reminder_targets(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

//     Ok(())
// }

// ///
// #[command]
// async fn update_reminder_deadline(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

//     Ok(())
// }

// ///
// #[command]
// async fn update_reminder_interval(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

//     Ok(())
// }