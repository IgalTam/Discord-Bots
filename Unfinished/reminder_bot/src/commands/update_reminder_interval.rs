//! Slash command functionality for `update_reminder_interval` command.
//! 
//! This command updates the posting interval of a scheduled Reminder instance.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use tokio::runtime::Handle;

/// Updates the posting interval of the specified reminder. This change will not take effect
/// until the subsequent next posting of the reminder.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Interval Type (day/hour/minute)
/// - New Reminder Interval Quantity (if type is "minute", this field cannot be less than 10)
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

    let ivl_type_arg = options
        .get(1)
        .expect("Expected reminder interval type")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let new_ivl_type: &str;
    if let CommandDataOptionValue::String(val) = ivl_type_arg {
        new_ivl_type = val;
    } else {
        return "Missing interval type (day, hour, or minute (at least 10 minutes))".to_string();
    }

    let ivl_qty_arg = options
        .get(2)
        .expect("Expected reminder interval quantity")
        .resolved
        .as_ref()
        .expect("Expected Integer object");
    let new_ivl_qty: u32;
    if let CommandDataOptionValue::Integer(val) = ivl_qty_arg {
        if let Ok(val) = u32::try_from(*val) {
            new_ivl_qty = val;
        } else {
            return "Invalid interval quantity".to_string();
        }
    } else {
        return "Missing interval quantity".to_string();
    }

    if new_ivl_type == "minute" && new_ivl_qty < 10 {
        return "Invalid interval length, must be at least 10 minutes".to_string();
    }

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx, targ_id_num, new_ivl_type, new_ivl_qty));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```update_reminder_interval```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, targ_id: u32, new_type: &str, new_qty: u32) -> String {
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_interval_type = new_type.to_string();      // update interval type
            targ_rem.rem_interval_qty = new_qty;                    // update interval length
            format!("Reminder {}: Interval successfully changed to {} {}(s).", 
                targ_id, targ_rem.rem_interval_qty, targ_rem.rem_interval_type)
        } else {
            format!("Reminder {} not found in scheduler.", targ_id)
        }
    }
}

/// Registers ```update_reminder_interval``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("update_reminder_interval").description("Updates the posting interval of a scheduled reminder")
        .create_option(|option|{
            option
                .name("reminder_id")
                .description("The ID of the target reminder.")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("new_interval_type")
                .description("The type of interval between reminder pings (day/hour/minute).")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("new_interval_duration")
                .description("The quantity of the interval type between reminder pings (number).")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
}