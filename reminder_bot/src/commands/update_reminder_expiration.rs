//! Slash command functionality for `update_reminder_expiration` command.
//! 
//! This command updates the expiration date of a scheduled Reminder instance.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use tokio::runtime::Handle;
use chrono::{DateTime, Local, TimeZone};

/// Updates the expiration deadline of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder expiration date/time ("year/month/day/hour/minute/second")
pub fn run(options: &[CommandDataOption], ctx: &Context) -> String {
    // parse arguments
    let targ_id = options
        .get(0)
        .expect("Expected reminder ID number (use `list_reminders` if needed)")
        .resolved
        .as_ref()
        .expect("Expected Integer object");
    let targ_id_num: u32;
    if let CommandDataOptionValue::Integer(id_num) = targ_id {
        if let Ok(val) = u32::try_from(*id_num) {
            targ_id_num = val;
            } else {
                return "Invalid ID number".to_string();
            }
    } else {
        return "Missing ID number".to_string();
    }

    let xpr_date = options
        .get(1)
        .expect("Expected reminder expiration date")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let date_str: Vec<&str>;
    if let CommandDataOptionValue::String(date) = xpr_date {
        date_str = date.split('/').collect();
        if date_str.len() != 6 {
            return "Invalid expiration date formatting 
                    (requires <year>/<month>/<day>/<hour>/<minute>/<second>)".to_string();
        }
    } else {
        return "Invalid expiration date".to_string();
    }
    let new_xpr: DateTime<Local> = Local.with_ymd_and_hms(
        date_str[0].parse::<i32>().unwrap(),
        date_str[1].parse::<u32>().unwrap(),
        date_str[2].parse::<u32>().unwrap(),
        date_str[3].parse::<u32>().unwrap(),
        date_str[4].parse::<u32>().unwrap(),
        date_str[5].parse::<u32>().unwrap(),
    ).unwrap();
    if new_xpr < Local::now() {
        return "Invalid expiration date. Must be set after the current time.".to_string();
    }

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx, targ_id_num, new_xpr));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```update_reminder_expiration```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, targ_id: u32, new_xpr: DateTime<Local>) -> String {
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_expire = new_xpr;   // update event expiration date
            format!("Reminder {}: Expiration deadline successfully changed to {}.", targ_id, targ_rem.rem_expire)
        } else {
            format!("Reminder {} not found in scheduler.", targ_id)
        }
    }
}

/// Registers ```update_reminder_expiration``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("update_reminder_expiration").description("Updates the expiration of a scheduled reminder")
        .create_option(|option|{
            option
                .name("reminder_id")
                .description("The ID of the target reminder.")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
        .create_option(|option| {
            option    
                .name("new_expiration_date")
                .description("New expiration date, in <YYYY/MM/DD/HH/MM/SS>.")
                .kind(CommandOptionType::String)
                .required(true)
        })
}