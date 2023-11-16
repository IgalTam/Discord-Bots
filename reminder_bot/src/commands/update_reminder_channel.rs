//! Slash command functionality for `update_reminder_channel` command.
//! 
//! This command updates the posting channel of a scheduled Reminder instance.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::{PartialChannel, ChannelId};
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use tokio::runtime::Handle;

/// Updates the channel of the specified reminder. The default reminder channel is the one that ```set_reminder```
/// is initially called in.
/// 
/// Command Arguments:
/// - Reminder ID (can be found with `list_reminders`)
/// - New Reminder Channel name (must be a text channel) 
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

    let ch_arg = options
        .get(1)
        .expect("Expected new channel")
        .resolved
        .as_ref()
        .expect("Expected Channel object");
    let new_ch: &PartialChannel;
    if let CommandDataOptionValue::Channel(val) = ch_arg {
        new_ch = val;
    } else {
        return "Missing new name".to_string();
    }

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx, targ_id_num, new_ch.id, 
        new_ch.name.as_ref().unwrap()));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```update_reminder_channel```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, targ_id: u32, new_chnl_id: ChannelId, chnl_name: &String) -> String {
    let reminder_lock = {   // read and update bot metadata
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };
    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        if let Some(mut targ_rem) = reminders.reminders.get_mut(&targ_id) {
            targ_rem.rem_channel_id = new_chnl_id;   // update event name
            format!("Reminder {}: Reminder channel successfully changed to {}.", targ_id, chnl_name)
        } else {
            format!("Reminder {} not found in scheduler.", targ_id)
        }
    }
}

/// Registers ```update_reminder_channel``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("update_reminder_channel").description("Updates the posting channel of a scheduled reminder")
        .create_option(|option|{
            option
                .name("reminder_id")
                .description("The ID of the target reminder.")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
        .create_option(|option|{
            option
                .name("new_channel")
                .description("Updated channel for reminder.")
                .kind(CommandOptionType::Channel)
                .required(true)
        })
}