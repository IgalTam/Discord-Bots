//! Reminder Bot [final name TBD]
//! 
//! A Rust-based Discord bot that allows for the creation of reminders for events, each of which ping a
//!  specific role on a configurable interval until the reminder expires.
//! 
//! Note that all long-term data storage is facilitated within program memory, so stopping the bot
//! will also wipe any active reminders.

mod commands;
use crate::commands::reminder::*;

use std::collections::HashSet;
use std::env;
use std::sync::Arc;
use std::collections::HashMap;

use serenity::async_trait;
use serenity::client::bridge::gateway::ShardManager;
use serenity::framework::standard::macros::group;
use serenity::framework::StandardFramework;
use serenity::http::Http;
use serenity::model::application::interaction::{Interaction, InteractionResponseType};
use serenity::model::{
    event::ResumedEvent,
    gateway::Ready,
    id::GuildId,
    prelude::*,
};
use serenity::prelude::*;
use tracing::error;
use async_timer::Interval;

pub struct ShardManagerContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}

/// Struct for storing the bot's command prefix in global data.
pub struct PrefixContainer;

impl TypeMapKey for PrefixContainer {
    type Value = Arc<String>;
}

/// Struct for storing and polling created Reminders.
struct ReminderStorage {
    next_rem_id: u32,
    reminders: HashMap<u32, Reminder>,
}

impl ReminderStorage {

    /// Creates a new ReminderStorage object.
    fn new() -> ReminderStorage {
        ReminderStorage {
            next_rem_id: 0,
            reminders: HashMap::new(),
        }
    }

    /// Polls all ```Reminders``` stored in ```reminders```,
    /// calling ```post_reminder()``` and ```set_next_poll()``` for
    /// each reminder ready to be posted and cleaning up expired ```Reminders```.
    /// 
    /// Raises a ```ReminderError``` when encountering errors
    /// during runtime, otherwise returns a tuple containing vectors
    /// with the IDs of expired reminders and reminders that require updated ```next_poll```s.
    async fn poll_reminders(&mut self, ctx: &Context) -> Result<Vec<u32>, ReminderError> {
        let mut expired: Vec<u32> = vec!();
        for (rem_id, reminder) in &mut self.reminders {
            let (has_exp, has_post) = reminder.expired().await;
            if has_post {   // the reminder is ready to be posted
                match reminder.post_reminder(ctx).await {
                    Err(e) => {
                        println!("Error encountered while polling reminders: {:?}", e);
                        return Err(e);
                    }
                    _ => (),
                }
                if !has_exp {   // update the next_poll of the reminder if it is not expired
                    if let Err(e) = reminder.set_next_poll() {
                        println!("Error encountered while updating reminder next poll: {:?}", e);
                        return Err(e);
                    }
                }
            }
            if has_exp {    // the reminder has expired -> add its ID to the expired vector
                expired.push(*rem_id);
            }
        }

        // println!("polled all reminders");
        Ok(expired)
    }
}
struct ReminderStorageWrapper; 

impl TypeMapKey for ReminderStorageWrapper {
    type Value = Arc<RwLock<ReminderStorage>>;
}

struct Handler;

#[async_trait]
impl EventHandler for Handler {

    // slash command handling
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            let content = match command.data.name.as_str() {
                "ping" => commands::ping::run(&command.data.options),
                "help" => commands::help::run(&command.data.options, &ctx),
                "set_reminder" => commands::set_reminder::run(&command.data.options, &ctx, command.clone()),
                "cancel_reminder" => commands::cancel_reminder::run(&command.data.options, &ctx),
                "list_reminders" => commands::list_reminders::run(&ctx),
                "update_reminder_name" => commands::update_reminder_name::run(&command.data.options, &ctx),
                "update_reminder_msg" => commands::update_reminder_msg::run(&command.data.options, &ctx),
                "update_reminder_target" => commands::update_reminder_target::run(&command.data.options, &ctx),
                "update_reminder_expiration" => commands::update_reminder_expiration::run(&command.data.options, &ctx),
                "update_reminder_interval" => commands::update_reminder_interval::run(&command.data.options, &ctx),
                "update_reminder_channel" => commands::update_reminder_channel::run(&command.data.options, &ctx),
                _ => "not implemented".to_string(),
            };

            if let Err(why) = command
                .create_interaction_response(&ctx.http, |response| {
                    response
                        .kind(InteractionResponseType::ChannelMessageWithSource)
                        .interaction_response_data(|message| message.content(content))
                })
                .await
            {
                println!("Cannot respond to slash command: {}", why);
            }
        }
    }

    // initializes slash commands and asynchronous handler for polling stored reminders
    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("Connected as {}", ready.user.name);

        // set up slash commands for all guilds this bot is a member of
        let guild_ids = ctx.cache.guilds();
        for guild_id in guild_ids {
            GuildId::set_application_commands(&guild_id, &ctx.http, |commands| {
                commands
                    .create_application_command(|command| commands::ping::register(command))
                    .create_application_command(|command| commands::help::register(command))
                    .create_application_command(|command| commands::set_reminder::register(command))
                    .create_application_command(|command| commands::cancel_reminder::register(command))
                    .create_application_command(|command| commands::list_reminders::register(command))
                    .create_application_command(|command| commands::update_reminder_name::register(command))
                    .create_application_command(|command| commands::update_reminder_msg::register(command))
                    .create_application_command(|command| commands::update_reminder_target::register(command))
                    .create_application_command(|command| commands::update_reminder_expiration::register(command))
                    .create_application_command(|command| commands::update_reminder_interval::register(command))
                    .create_application_command(|command| commands::update_reminder_channel::register(command))
            }).await.unwrap();
        }

        // engage reminder handler
        let mut interval = Interval::platform_new(core::time::Duration::from_secs(60)); // polls all reminders every minute
        loop {
            // poll reminders, retrieve IDs of expired reminders
            let reminder_lock = {
                let data_read = ctx.data.read().await;
                data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
            };
            let expired_rems = {
                let mut reminders = reminder_lock.write().await;
                match reminders.poll_reminders(&ctx).await {
                    Ok(expired) => expired.clone(),
                    Err(e) => panic!("Failed to update reminders: {:?}", e),
                }
            };
            // remove expire reminders from ReminderStorage
            let reminder_lock = {
                let data_read = ctx.data.read().await;
                data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
            };
            {
                let mut reminders = reminder_lock.write().await;
                for rem_id in expired_rems {
                    reminders.reminders.remove(&rem_id);
                }
            }
            interval.as_mut().await;
        }
    }

    async fn resume(&self, _: Context, _: ResumedEvent) {
        println!("Resumed");
    }

}

#[group]
#[commands(help, set_reminder, cancel_reminder, list_reminders,
        update_reminder_name, update_reminder_message, update_reminder_target,
        update_reminder_expiration, update_reminder_interval, update_reminder_channel)]
struct General;

#[tokio::main]
/// Main bot program. Adapted from Serenity GitHub examples.
async fn main() {
    // This will load the environment variables located at `./.env`, relative to
    // the CWD. See `./.env.example` for an example on how to structure this.
    dotenv::dotenv().expect("Failed to load .env file");

    let token = env::var("DISCORD_TOKEN").expect("Expected a token in the environment");
    let prefix = env::var("PREFIX").expect("Expected a prefix in the environment");

    let http = Http::new(&token);

    // We will fetch your bot's owners and id
    let (owners, _bot_id) = match http.get_current_application_info().await {
        Ok(info) => {
            let mut owners = HashSet::new();
            owners.insert(info.owner.id);

            (owners, info.id)
        },
        Err(why) => panic!("Could not access application info: {:?}", why),
    };

    // Create the framework
    let framework =
        StandardFramework::new().configure(|c| c.owners(owners).prefix(prefix.clone())).group(&GENERAL_GROUP);

    let intents = GatewayIntents::GUILD_MESSAGES
        | GatewayIntents::DIRECT_MESSAGES
        | GatewayIntents::MESSAGE_CONTENT
        | GatewayIntents::GUILD_MEMBERS
        | GatewayIntents::GUILDS;
    let mut client = Client::builder(&token, intents)
        .framework(framework)
        .event_handler(Handler)
        .await
        .expect("Err creating client");

    {
        let mut data = client.data.write().await;
        data.insert::<ShardManagerContainer>(client.shard_manager.clone());
        data.insert::<PrefixContainer>(Arc::new(prefix.to_string()));
        data.insert::<ReminderStorageWrapper>(Arc::new(RwLock::new(ReminderStorage::new())));
    }

    let shard_manager = client.shard_manager.clone();

    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.expect("Could not register ctrl+c handler");
        shard_manager.lock().await.shutdown_all().await;
    });

    if let Err(why) = client.start().await {
        error!("Client error: {:?}", why);
    }
}