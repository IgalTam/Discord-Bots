use serenity::framework::standard::macros::command;
use serenity::framework::standard::{Args, CommandResult};
use serenity::model::prelude::*;
use serenity::utils::MessageBuilder;
use serenity::prelude::*;
use chrono::prelude::*;
use crate::ReminderStorageWrapper;

#[derive(Debug)]
pub struct ReminderError;

trait MentionShowable: Mentionable + std::fmt::Display {}

/// Struct for storing reminder metadata.
pub struct Reminder<'a> {
    rem_id: u32,
    rem_name: String,
    rem_msg: String,
    // rem_author: Member,
    rem_author: String,
    // rem_channel: Channel,
    rem_channel_id: ChannelId,
    // rem_targs: Vec<Role>,
    rem_targ: &'a dyn MentionShowable,
    // rem_targs: Vec<String>,
    rem_expire: DateTime<Local>,
    rem_interval_type: String,
    rem_interval_qty: u32,
}

impl<'a>  Reminder<'a> {
    /// Creates a new Reminder object.
    fn new(id: u32, nm: String, msg: String, auth: String, chnl_id: ChannelId, targ: &'a dyn MentionShowable, deadline: DateTime<Local>, ivt_type: String, ivt_qty: u32) -> Self {
        Reminder {
            rem_id: id,
            rem_name: nm,
            rem_msg: msg,
            rem_author: auth,
            rem_channel_id: chnl_id,
            rem_targ: targ,
            rem_expire: deadline,
            rem_interval_type: ivt_type,
            rem_interval_qty: ivt_qty,
        }
    }

    /// Checks if the Reminder deadline has expired.
    /// 
    /// Returns ```true``` if the Reminder has expired, ```false```
    /// if the Reminder has not yet epxired, and a ```ReminderUpdateError``` if
    /// the current, real world time is past the Reminder's expiration time
    /// (the Reminder should have expired, but didnt').
    pub async fn expired(&self) -> Result<(bool, DateTime<Local>), ReminderError> {
        let cur_time = Local::now();
        if self.rem_expire == cur_time {
            Ok((true, cur_time))
        } else if self.rem_expire < cur_time {
            Ok((false, cur_time))
        } else {
            Err(ReminderError)
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

/// Creates a reminder and installs it in the global ReminderStorage.
/// 
/// Command Arguments:
/// - Reminder event name
/// - Reminder message
/// - Reminder target mentions (members/roles)
/// - Reminder expiration date/time ("<year>/<month>/<day>/<hour>/<minute>/<second>")
/// - Reminder interval type ("year", "month", "day", etc.)
/// - Reminder interval length (whole number)
#[command]
async fn set_reminder(ctx: &Context, msg: &Message, args: Args) -> CommandResult {
    // check for all required arguments
    if args.len() != 7 {
        msg.reply(ctx, "Six arguments (event name, message, mentions, expiration deadline, interval type, interval length) required.").await?;
        return Ok(());
    }

    // let 

    let reminder_lock = {
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    let confirm = {
        let reminders = reminder_lock.write().await;

    };



    Ok(())
}

///
#[command]
async fn cancel_reminder(ctx: &Context, msg: &Message, mut args: Args) -> CommandResult {

    Ok(())
}

///
#[command]
async fn list_reminders(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

    Ok(())
}

///
#[command]
async fn update_reminder_message(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

    Ok(())
}

///
#[command]
async fn update_reminder_targets(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

    Ok(())
}

///
#[command]
async fn update_reminder_deadline(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

    Ok(())
}

///
#[command]
async fn update_reminder_interval(ctx: &Context, msg: &Message,  mut args: Args) -> CommandResult {

    Ok(())
}