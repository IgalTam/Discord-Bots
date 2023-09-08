mod commands;

use std::collections::HashSet;
use std::env;
use std::sync::Arc;

use serenity::async_trait;
use serenity::client::bridge::gateway::ShardManager;
use serenity::framework::standard::macros::group;
use serenity::framework::StandardFramework;
use serenity::http::Http;
use serenity::model::event::ResumedEvent;
use serenity::model::gateway::Ready;
use serenity::model::prelude::*;
use serenity::prelude::*;
use tracing::error;
use std::collections::HashMap;
use chrono::prelude::*;
use async_timer::Interval;

use crate::commands::meta::*;
use crate::commands::reminder::*;
use crate::commands::reminder::{Reminder, ReminderUpdateError};

pub struct ShardManagerContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}

struct ReminderStorage {
    reminders: HashMap<u32, Reminder>,
}

impl ReminderStorage {
    fn new() -> ReminderStorage {
        ReminderStorage {
            reminders: HashMap::new(),
        }
    }

    async fn poll_reminders(&self) -> Result<(), ReminderUpdateError> {
        for (_, reminder) in &self.reminders {
            match reminder.expired().await {
                Ok(true) => { 
                    
                }
                Ok(false) => {

                }
                Err(e) => { return Err(ReminderUpdateError); }
            }
        }

        println!("polled all reminders");
        Ok(())
    }
}
struct ReminderStorageWrapper; 

impl TypeMapKey for ReminderStorageWrapper {
    type Value = Arc<RwLock<ReminderStorage>>;
}

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    /// initializes asynchronous timer for polling stored reminders
    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("Connected as {}", ready.user.name);
        let mut interval = Interval::platform_new(core::time::Duration::from_secs(2));
        loop {
            let reminder_lock = {
                let data_read = ctx.data.read().await;
                data_read.get::<ReminderStorageWrapper>().expect("Expected ReminderStorageWrapper in TypeMap.").clone()
            };
            {
                let reminders = reminder_lock.write().await;
                if let Err(e) = reminders.poll_reminders().await {
                    panic!("Failed to update reminders: {:?}", e);
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
// #[commands(multiply, ping, quit)]
#[commands(ping)]
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
        | GatewayIntents::MESSAGE_CONTENT;
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