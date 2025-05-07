import discord
from discord import app_commands
from dotenv import load_dotenv

from config.config import Config
from service.timetable_service import get_timetable
from util.list_utils import ListUtils
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

        log.info("Tree commands have been synced")
    except Exception as e:
        log.error(
            "Encountered exception while connecting to discord: %s", str(e), exc_info=e
        )


@tree.command(
    name="timetable",
    description="Get anime time table for current week",
    guild=discord.Object(id=554630626175614978),
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
    data: dict = get_timetable(timezone, type)
    embeds = data.get("embeds", [])
    view = data.get("view")
    embed_chunks = ListUtils.chunk_list(embeds, 10)
    await interaction.response.send_message(embeds=data.get("heading_embeds"))
    for i, chunk in enumerate(embed_chunks):
        await interaction.followup.send(
            embeds=chunk, **({"view": view} if i == len(embed_chunks) - 1 else {})
        )


client.run(Config.get_discord_token())
