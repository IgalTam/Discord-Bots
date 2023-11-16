//! Slash command functionality for set_reminder command.
//! 
//! This command configures a new Reminder instance, which will then be installed into the scheduler.

use crate::commands::reminder::Reminder;
use crate::ReminderStorageWrapper;

use serenity::builder::CreateApplicationCommand;
use serenity::model::application::interaction::application_command::ApplicationCommandInteraction;
use serenity::model::prelude::Role;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;
use chrono::{DateTime, Local, TimeZone, Duration};
use tokio::runtime::Handle;


/// Creates a reminder and installs it in the global ReminderStorage.
/// 
/// Command Arguments:
/// - Reminder event name
/// - Reminder event message
/// - Reminder target role
/// - Reminder expiration date/time ("YYYY/MM/DD/HH/MM/SS")
/// - Reminder interval type (day, hour, or minute (must be at least 10 minutes))
/// - Reminder interval length (whole number)
/// - Reminder first poll date/time (optional, "YYYY/MM/DD/HH/MM/SS")
pub fn run(options: &[CommandDataOption], ctx: &Context, inter: ApplicationCommandInteraction) -> String {
    // parse command arguments
    let event_name = options
        .get(0)
        .expect("Expected event name")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let name_str: &str;
    if let CommandDataOptionValue::String(ev_nm) = event_name {
        name_str = ev_nm;
    } else {
        return "Missing event name".to_string();
    }

    let event_message = options
        .get(1)
        .expect("Expected event message")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let msg_str: &str;
    if let CommandDataOptionValue::String(ev_msg) = event_message {
        msg_str = ev_msg;
    } else {
        return "Missing event message".to_string();
    }

    let targ_role = options
        .get(2)
        .expect("Expected target mention")
        .resolved
        .as_ref()
        .expect("Expected Mentionable object");
    let rem_role: &Role;
    if let CommandDataOptionValue::Role(ev_role) = targ_role {
        rem_role = ev_role;
    } else {
        return "Missing target role".to_string();
    }

    let xpr_date = options
        .get(3)
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
    let xpr_datetime: DateTime<Local> = Local.with_ymd_and_hms(
        date_str[0].parse::<i32>().unwrap(),
        date_str[1].parse::<u32>().unwrap(),
        date_str[2].parse::<u32>().unwrap(),
        date_str[3].parse::<u32>().unwrap(),
        date_str[4].parse::<u32>().unwrap(),
        date_str[5].parse::<u32>().unwrap(),
    ).unwrap();

    let ivl_type = options
        .get(4)
        .expect("Expected reminder interval type")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let ivl_type_str: &str;
    if let CommandDataOptionValue::String(ev_ivl_type) = ivl_type {
        ivl_type_str = ev_ivl_type;
    } else {
        return "Missing interval type (day, hour, or minute (at least 10 minutes))".to_string();
    }

    let ivl_qty = options
        .get(5)
        .expect("Expected reminder interval quantity")
        .resolved
        .as_ref()
        .expect("Expected Integer object");
    let ivl_qty_num: u32;
    if let CommandDataOptionValue::Integer(qty_str) = ivl_qty {
        if let Ok(val) = u32::try_from(*qty_str) {
            ivl_qty_num = val;
        } else {
            return "Invalid interval quantity".to_string();
        }
    } else {
        return "Missing interval quantity".to_string();
    }

    // configure the DateTime for the first Reminder ping
    let mut first_poll: DateTime<Local>;
    if let Some(arg) = options.get(6) {
        // if a date was passed in, parse it
        let date_str: Vec<&str>;
        if let CommandDataOptionValue::String(date) = arg.resolved.as_ref().expect("Expected String object") {
            date_str = date.split('/').collect();
            if date_str.len() != 6 {
                return "Invalid expiration date formatting 
                        (requires <year>/<month>/<day>/<hour>/<minute>/<second>)".to_string();
            }
        } else {
            return "Invalid expiration date".to_string();
        }
        first_poll = Local.with_ymd_and_hms(
            date_str[0].parse::<i32>().unwrap(),
            date_str[1].parse::<u32>().unwrap(),
            date_str[2].parse::<u32>().unwrap(),
            date_str[3].parse::<u32>().unwrap(),
            date_str[4].parse::<u32>().unwrap(),
            date_str[5].parse::<u32>().unwrap(),
        ).unwrap();
    } else {
        // otherwise, generate a starting date based on polling interval
        first_poll = Local::now();
        match ivl_type_str {
            "day" => first_poll += Duration::days(ivl_qty_num.into()),
            "hour" => first_poll += Duration::hours(ivl_qty_num.into()),
            "minute" => {
                if ivl_qty_num < 10 {
                    return "Invalid interval length, must be at least 10 minutes".to_string();
                }
                first_poll += Duration::minutes(ivl_qty_num.into());
            }
            _ => {
                return "Invalid interval type (must be year, month, day, hour, or minute)".to_string();
            }
        };
    }

    // enter the async runtime to update metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    futures::executor::block_on(run_ctx_handler(ctx, name_str, msg_str, inter, rem_role, xpr_datetime, ivl_type_str, ivl_qty_num, first_poll));
    drop(temp_rt);
    
    format!("Reminder for {} is set.", name_str)
}

/// Asynchronous portion of ```set_reminder```, involving access to the bot's metadata.
/// 
/// This code is separate from ```run()``` due to the use of ```futures::executor::block_on()``` to enter the main
/// Tokio runtime from a synchronous function.
async fn run_ctx_handler(ctx: &Context, name_str: &str, msg_str: &str, inter: ApplicationCommandInteraction,
                         rem_role: &Role, xpr_datetime: DateTime<Local>, ivl_type_str: &str, ivl_qty_num: u32, first_poll: DateTime<Local>) {
    // read bot metadata
    let reminder_lock = {
        let data_read = ctx.data.read().await;
        data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
    };

    {
        let mut reminders = reminder_lock.write().await;    // open mutex lock for writing
        let assgn_id = reminders.next_rem_id;   // retrieve next ID to be assigned to the new reminder
        let new_rem = Reminder::new(       // create new reminder
            assgn_id,
            name_str.to_string(),
            msg_str.to_string(),
            inter.user.name.clone(),
            inter.channel_id.clone(),
            rem_role.clone(),
            xpr_datetime,
            ivl_type_str.to_string(),
            ivl_qty_num,
            first_poll,
        );
        reminders.reminders.insert(assgn_id, new_rem);  // insert new reminder into reminder scheduler
        reminders.next_rem_id += 1;                          // update next reminder ID
    }
}

/// Registers ```set_reminder``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("set_reminder").description("Sets a reminder")
        .create_option(|option|{
            option
                .name("event_name")
                .description("The name of the event.")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option    
                .name("event_message")
                .description("The message to be shown on reminders for this event.")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("target_role")
                .description("The role that is to be mentioned in reminders for this event.")
                .kind(CommandOptionType::Role)
                .required(true)
        })
        .create_option(|option| {
            option    
                .name("reminder_expiration_date")
                .description("Expiration date, in <YYYY/MM/DD/HH/MM/SS>.")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("reminder_interval_type")
                .description("The type of interval between reminder pings (day/hour/minute).")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("reminder_interval_duration")
                .description("The quantity of the interval type between reminder pings (number).")
                .kind(CommandOptionType::Integer)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("first_poll_time")
                .description("The first time this reminder will be polled (optional, <YYYY/MM/DD/HH/MM/SS>).")
                .kind(CommandOptionType::String)
                .required(false)
        })

}