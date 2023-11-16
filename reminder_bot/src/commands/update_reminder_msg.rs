//! Slash command functionality for `update_reminder_msg` command.
//! 
//! This command updates the message field of a scheduled Reminder instance.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use tokio::runtime::Handle;

/// Updates the `event message` field of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Message
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

    let new_msg = options
        .get(1)
        .expect("Expected new message")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let msg_str: &str;
    if let CommandDataOptionValue::String(ev_msg) = new_msg {
        msg_str = ev_msg;
    } else {
        return "Missing new message".to_string();
    }

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx, targ_id_num, msg_str));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```update_reminder_msg```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, targ_id: u32, new_msg: &str) -> String {
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_msg = new_msg.to_string();   // update event message
            format!("Reminder {}: Event message successfully changed to {}.", targ_id, targ_rem.rem_msg)
        } else {
            format!("Reminder {} not found in scheduler.", targ_id)
        }
    }
}

/// Registers ```update_reminder_msg``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("update_reminder_msg").description("Updates the message of a scheduled reminder")
        .create_option(|option|{
            option
                .name("reminder_id")
                .description("The ID of the target reminder.")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
        .create_option(|option|{
            option
                .name("new_msg")
                .description("Updated message for reminder.")
                .kind(CommandOptionType::String)
                .required(true)
        })
}