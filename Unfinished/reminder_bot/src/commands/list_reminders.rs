//! Slash command functionality for `cancel_reminder` command.
//! 
//! This command deschedules a scheduled Reminder instance, if able.

use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::client::Context;
use tokio::runtime::Handle;

/// Lists all active reminders and their relevant metadata.
pub fn run(ctx: &Context) -> String {
    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let out_msg = futures::executor::block_on(run_ctx_handler(ctx));
    drop(temp_rt);
    out_msg
}

/// Asynchronous portion of ```list_reminders```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context) -> String {
    // read bot metadata
    let reminder_lock = {
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };

    {
        let reminders = reminder_lock.write().await;    // open mutex lock for writing
        if reminders.reminders.is_empty() {
            return "No reminders are currently scheduled.".to_string();
        }

        let mut output_message = String::new();
        output_message.push_str("Active Reminders:\n\n");
        for (rem_id, rem) in &reminders.reminders {
            let post_ch = rem.rem_channel_id.to_channel_cached(&ctx.cache).unwrap().to_string(); // get channel from channel ID
            output_message.push_str(format!("ID: {rem_id}\n\t\t{}, by {}.\n\t\tTargeting {}.\n\t\tActive in {}.\n\t\tExpires on {}. \
                \n\t\tPolling interval of {} {}(s).\n\t\tMessage: {}\n",
                rem.rem_name, rem.rem_author, rem.rem_targ.name, post_ch, rem.rem_expire,
                rem.rem_interval_qty, rem.rem_interval_type, rem.rem_msg).as_str());
        }
        return output_message;
    }
}

/// Registers ```list_reminders``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("list_reminders").description("Lists all scheduled reminders")
}