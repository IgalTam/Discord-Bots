//! Slash command to indicate prefix-based command usage and syntax (shortcut to prefix version of ```help``` [see ```reminder.rs```]).

use crate::PrefixContainer;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::interaction::application_command::CommandDataOption;
use serenity::client::Context;
use tokio::runtime::Handle;

pub fn run(_options: &[CommandDataOption], ctx: &Context) -> String {
    // enter the async runtime to access metadata
    let handle = Handle::current();
    let temp_rt = handle.enter();
    let post = futures::executor::block_on(run_ctx_handler(ctx));
    drop(temp_rt);
    post
}

/// Asynchronous helper function for accessing prefix stored in global data.
pub async fn run_ctx_handler(ctx: &Context) -> String {
    let prefix = {
        let data_read = ctx.data.read().await;
        data_read.get::<PrefixContainer>().expect("Expected PrefixContainer in TypeMap.").clone()
    };
    format!("This bot is a low level implementation that uses prefix commands. The prefix \
        for this bot is `{}`. Type `{}help` for more info.", prefix, prefix)
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("help").description("Command usage and syntax")
}