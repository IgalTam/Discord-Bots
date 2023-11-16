//! Slash command functionality for `update_reminder_name` command.
//! 
//! This command updates the name field of a scheduled Reminder instance.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use tokio::runtime::Handle;

/// Updates the `event name` field of the specified reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Name
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

    let new_name = options
        .get(1)
        .expect("Expected new name")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let name_str: &str;
    if let CommandDataOptionValue::String(ev_nm) = new_name {
        name_str = ev_nm;
    } else {
        return "Missing new name".to_string();
    }

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx, targ_id_num, name_str));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```update_reminder_name```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, targ_id: u32, new_name: &str) -> String {
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_name = new_name.to_string();   // update event name
            format!("Reminder {}: Event name successfully changed to {}.", targ_id, targ_rem.rem_name)
        } else {
            format!("Reminder {} not found in scheduler.", targ_id)
        }
    }
}

/// Registers ```update_reminder_name``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("update_reminder_name").description("Updates the name of a scheduled reminder")
        .create_option(|option|{
            option
                .name("reminder_id")
                .description("The ID of the target reminder.")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
        .create_option(|option|{
            option
                .name("new_name")
                .description("Updated name for reminder.")
                .kind(CommandOptionType::String)
                .required(true)
        })
}