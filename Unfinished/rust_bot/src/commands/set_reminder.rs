use crate::commands::reminder::{Reminder, ReminderError};

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};
use serenity::client::Context;


/// Creates a reminder and installs it in the global ReminderStorage.
/// 
/// Command Arguments:
/// - Reminder event name
/// - Reminder event message
/// - Reminder target mentions (members/roles)
/// - Reminder expiration date/time ("year/month/day/hour/minute/second")
/// - Reminder interval type ("year", "month", "day", etc.)
/// - Reminder interval length (whole number)
pub fn run(options: &[CommandDataOption], ctx: &Context) -> Result<(), ReminderError> {
    // parse command arguments
    let event_name = options
        .get(0)
        .expect("Expected event name")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let event_message = options
        .get(1)
        .expect("Expected event message")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let targ_mention = options
        .get(2)
        .expect("Expected target mention")
        .resolved
        .as_ref()
        .expect("Expected Mentionable object");
    let xpr_date = options
        .get(3)
        .expect("Expected reminder expiration date")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let ivl_type = options
        .get(4)
        .expect("Expected reminder interval type")
        .resolved
        .as_ref()
        .expect("Expected String object");
    let ivl_qty = options
        .get(5)
        .expect("Expected reminder interval quantity")
        .resolved
        .as_ref()
        .expect("Expected Integer object");

    // create Reminder object
    // if let CommandDataOptionValue::User(user, _member) = option {
    //     format!("{}'s id is {}", user.tag(), user.id)
    // } else {
    //     "Please provide a valid user".to_string()
    // }
    // if let CommandDataOptionValue::String(date_str) = xpr_date {
    //     date_str
    // } else {
    //     return Err(ReminderError);
    // }

}

/// Registers ```set_reminder``` as a slash command, configures input formatting.
pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("set_reminder").description("Sets a reminder")
        .create_option(|option|{
            option
                .name("Event Name")
                .description("The name of the event.")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option    
                .name("Event Message")
                .description("The message to be shown on reminders for this event.")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("Target Role")
                .description("The user/role that is to be mentioned in reminders for this event.")
                .kind(CommandOptionType::Mentionable)
                .required(true)
        })
        .create_option(|option| {
            option    
                .name("Reminder Expiration Date")
                .description("The date and time for the reminder to expire. Use the format <year/month/day/hour/minute/second>.")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("Reminder Interval Type")
                .description("The type of interval between reminder pings (year/month/day/hour/minute).")
                .kind(CommandOptionType::String)
                .required(true)
        })
        .create_option(|option| {
            option
                .name("Reminder Interval Duration")
                .description("The quantity of the interval type between reminder pings (number).")
                .kind(CommandOptionType::Number)
                .required(true)
        })

}