import discord
from discord import app_commands
from dotenv import load_dotenv

from config.config import Config
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

        log.info("Tree commands have been synced")
    except Exception as e:
        log.error(
            "Encountered exception while connecting to discord: %s", str(e), exc_info=e
        )


@tree.command(
    name="timetable",
    description="Get anime time table for current week",
    guilds=[
        discord.Object(id=554630626175614978),
        discord.Object(id=1369602842645499994),
    ],
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


client.run(Config.get_discord_token())
