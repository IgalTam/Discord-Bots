//! Reminder Bot
//! A Rust-based Discord bot that creates reminders for events, each of which ping people/roles on a configurable interval until the reminder expires.

mod commands;

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

use crate::commands::meta::*;
use crate::commands::reminder::{Reminder, ReminderError, SET_REMINDER_COMMAND};

pub struct ShardManagerContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}

// #[derive(IndexMut)]
struct ReminderStorage {
    next_rem_id: u32,
    reminders: HashMap<u32, Reminder>,
}

/// Struct for storing and polling created Reminders.
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
            let (has_exp, has_post, cur_time) = reminder.expired().await;
            if has_post {   // the reminder is ready to be posted
                match reminder.post_reminder(ctx, cur_time).await {
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

        println!("polled all reminders");
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

    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            println!("Received command interaction: {:#?}", command);

            let content = match command.data.name.as_str() {
                "ping" => commands::ping::run(&command.data.options),
                "set_reminder" => commands::set_reminder::run(&command.data.options, &ctx, command.clone()),
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

    // initializes slash commands asynchronous handler for polling stored reminders
    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("Connected as {}", ready.user.name);

        // set up slash commands
        let guild_id = GuildId(
            env::var("GUILD_ID")
                .expect("Expected GUILD_ID in environment")
                .parse()
                .expect("GUILD_ID must be an integer"),
        );
        let _commands = GuildId::set_application_commands(&guild_id, &ctx.http, |commands| {
            commands
                .create_application_command(|command| commands::ping::register(command))
                .create_application_command(|command| commands::set_reminder::register(command))
        }).await;
        // println!("I now have the following guild slash commands: {:#?}", _commands);
        // println!("set_reminder stuff: {:#?}", _commands[1].);

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
#[commands(ping, set_reminder)]
struct General;

#[tokio::main]
async fn main() {
    // This will load the environment variables located at `./.env`, relative to
    // the CWD. See `./.env.example` for an example on how to structure this.
    dotenv::dotenv().expect("Failed to load .env file");

    let token = env::var("DISCORD_TOKEN").expect("Expected a token in the environment");

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
        StandardFramework::new().configure(|c| c.owners(owners).prefix("/%/")).group(&GENERAL_GROUP);

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