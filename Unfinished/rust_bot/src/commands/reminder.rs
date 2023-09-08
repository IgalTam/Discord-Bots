use serenity::framework::standard::macros::command;
use serenity::framework::standard::{Args, CommandResult};
use serenity::model::prelude::*;
use serenity::prelude::*;
use chrono::prelude::*;

#[derive(Debug)]
pub struct ReminderUpdateError;

///
pub struct Reminder {
    rem_id: u32,
    rem_name: String,
    rem_msg: String,
    rem_author: Member,
    rem_channel: Channel,
    rem_targs: Vec<Member>,
    rem_expire: DateTime<Local>,
    rem_interval_type: String,
    rem_interval_qty: u32,
}

impl Reminder {
    fn new(id: u32, nm: String, msg: String, auth: Member, chnl: Channel, targs: Vec<Member>, deadline: DateTime<Local>, ivt_type: String, ivt_qty: u32) -> Self {
        Reminder {
            rem_id: id,
            rem_name: nm,
            rem_msg: msg,
            rem_author: auth,
            rem_channel: chnl,
            rem_targs: targs,
            rem_expire: deadline,
            rem_interval_type: ivt_type,
            rem_interval_qty: ivt_qty,
        }
    }

    pub async fn expired(&self) -> Result<bool, ReminderUpdateError> {
        let cur_time = Local::now();
        if self.rem_expire == cur_time {
            Ok(true)
        } else if self.rem_expire < cur_time {
            Ok(false)
        } else {
            Err(ReminderUpdateError)
        }
    }

    pub async fn post_reminder(&self, cur_time: DateTime<Local>) {
        
    }
}

///
#[command]
async fn set_reminder(ctx: &Context, msg: &Message, mut args: Args) -> CommandResult {
    
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