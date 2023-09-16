use crate::commands::reminder::{Reminder, ReminderError};

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption,
    CommandDataOptionValue,
};



/// Creates a reminder and installs it in the global ReminderStorage.
/// 
/// Command Arguments:
/// - Reminder event name
/// - Reminder message
/// - Reminder target mentions (members/roles)
/// - Reminder expiration date/time ("<year>/<month>/<day>/<hour>/<minute>/<second>")
/// - Reminder interval type ("year", "month", "day", etc.)
/// - Reminder interval length (whole number)
pub fn run(options: &[CommandDataOption]) -> String {
    let option = options
        .get(0)
        .expect("Expected user option")
        .resolved
        .as_ref()
        .expect("Expected user object");

    if let CommandDataOptionValue::User(user, _member) = option {
        format!("{}'s id is {}", user.tag(), user.id)
    } else {
        "Please provide a valid user".to_string()
    }
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
                .description("The role that is to be mentioned in reminders for this event.")
                .kind(CommandOptionType::Role)
                .required(true)
        })

}