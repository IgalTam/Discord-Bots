//! Slash command functionality for `cancel_reminder` command.
//! 
//! This command deschedules a scheduled Reminder instance, if able.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use tokio::runtime::Handle;


/// Cancels an active reminder based on its ID (can be found by using ```list_reminders```).
/// 
/// Command Argument: Reminder ID (whole number).
pub fn run(options: &[CommandDataOption], ctx: &Context) -> String {
    // parse argument
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

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx, targ_id_num));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```cancel_reminder```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, targ_id: u32) -> String {
    // read bot metadata
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(extr_rem) = reminders.reminders.remove(&targ_id) {
            format!("Reminder {}: {} successfully descheduled.", targ_id, extr_rem.rem_name)    
        } else {
            format!("Reminder {} not found in scheduler.", targ_id)
        }
    }
}

/// Registers ```cancel_reminder``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("cancel_reminder").description("Removes a reminder")
        .create_option(|option|{
            option
                .name("reminder_id")
                .description("The ID of the target reminder.")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
}