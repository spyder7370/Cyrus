import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from config.config import Config
from service.episode_updates_service import (
    register_episode_updates,
    deregister_episode_updates,
    schedule_updates_feed,
)
from service.rss_service import register_rss, get_rss_feeds_for_server, schedule_feeds
from service.timetable_service import send_timetable_embeds_to_discord
from util.logger import log

load_dotenv()
# Connect to discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    try:
        log.info("%s has connected to Discord", client.user)
        log.info(
            "%s has connected to %s discord server(s)",
            client.user,
            str(len(client.guilds)),
        )

        await tree.sync(guild=discord.Object(id=554630626175614978))
        await tree.sync(guild=discord.Object(id=1369602842645499994))
        await tree.sync()

        log.info("Tree commands have been synced")

        schedule_rss_feeds.start()
        log.info("Started scheduling of rss feeds")

        schedule_episode_updates.start()
        log.info("Started scheduling of episode updates")
    except Exception as e:
        log.error(
            "Encountered exception while connecting to discord: %s", str(e), exc_info=e
        )
        schedule_rss_feeds.stop()
        schedule_episode_updates.stop()


@tree.command(
    name="timetable",
    description="Get anime time table for the current week",
)
@app_commands.choices(
    timezone=[
        app_commands.Choice(name="Asia/Kolkata", value="Asia/Kolkata"),
        app_commands.Choice(name="UTC", value="UTC"),
    ]
)
@app_commands.choices(
    type=[
        app_commands.Choice(name="All", value="all"),
        app_commands.Choice(name="Sub", value="sub"),
        app_commands.Choice(name="Dub", value="dub"),
        app_commands.Choice(name="Raw", value="raw"),
    ]
)
async def timetable_slash_command(
    interaction, timezone: str = "UTC", type: str = "sub"
):
    log.info("Fetching timetable for timezone: %s", timezone)
    await send_timetable_embeds_to_discord(interaction, timezone, type)


@tree.command(
    name="register-rss",
    description="Add rss feed to a channel",
)
async def register_rss_slash_command(
    interaction, channel: discord.TextChannel, url: str, alias: str
):
    try:
        register_rss(
            str(channel.id),
            url,
            str(interaction.user.id),
            str(interaction.guild.id),
            interaction.guild.name,
            alias,
        )
        await interaction.response.send_message(
            "Successfully added rss feed to channel"
        )
    except Exception as e:
        log.error(
            "Encountered exception while adding rss feed to channel %s: %s",
            channel.id,
            str(e),
            exc_info=e,
        )
        await interaction.response.send_message(
            "Something went wrong while adding rss feed to channel"
        )


@tree.command(
    name="list-rss",
    description="List all rss feed of the server",
)
async def list_rss_slash_command(interaction):
    data: dict = get_rss_feeds_for_server(
        str(interaction.guild.id), interaction.guild.name
    )
    embeds = data.get("embeds", [])
    views = data.get("views")
    await interaction.response.send_message(embeds=data.get("heading_embeds"))
    for i, embed in enumerate(embeds):
        await interaction.followup.send(embed=embed, view=views[i])


@tree.command(
    name="remove-rss",
    description="Remove rss feed from the server",
)
async def remove_rss_slash_command(interaction):
    await interaction.response.send_message(
        "Please use `/list-rss` to remove rss feeds"
    )


@tree.command(
    name="register-updates",
    description="Add episode updates feed to a channel",
)
async def register_updates_slash_command(interaction, channel: discord.TextChannel):
    try:
        register_episode_updates(
            str(channel.id),
            str(interaction.user.id),
            str(interaction.guild.id),
            interaction.guild.name,
        )
        await interaction.response.send_message(
            "Successfully added episode updates feed to channel"
        )
    except Exception as e:
        log.error(
            "Encountered exception while adding episode updates feed to channel %s: %s",
            channel.id,
            str(e),
            exc_info=e,
        )
        await interaction.response.send_message(
            "Something went wrong while adding episode updates feed to channel"
        )


@tree.command(
    name="remove-updates-feed",
    description="Remove episode updates feed from the server",
)
async def deregister_updates_slash_command(interaction):
    data = deregister_episode_updates(str(interaction.guild.id), interaction.guild.name)
    await interaction.response.send_message(
        embeds=data.get("embeds", []), view=data.get("view")
    )


@tree.command(
    name="health",
    description="Validate if the bot is working",
)
async def health_slash_command(interaction):
    await interaction.response.send_message("OK")


@tasks.loop(minutes=15)
async def schedule_rss_feeds():
    try:
        await schedule_feeds(client)
    except Exception as e:
        log.error("RSS scheduling failed: %s", str(e), exc_info=e)


@tasks.loop(minutes=15)
async def schedule_episode_updates():
    try:
        await schedule_updates_feed(client)
    except Exception as e:
        log.error("Episode scheduling failed: %s", str(e), exc_info=e)


client.run(Config.get_discord_token())
