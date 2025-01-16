import discord
from discord import app_commands

from db.db import cursor
from util.logger import log

# Connect to db
cursor.execute("")

# Connect to discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    try:
        log.info("%s has connected to Discord", client.user)
        log.info("%s has connected to %s discord server(s)", client.user, str(len(client.guilds)))

        await tree.sync(guild=discord.Object(id=554630626175614978))

        log.info("Tree commands have been synced")
    except Exception as e:
        log.error("Encountered exception while connecting to discord: %s", str(e), exc_info=e)


@tree.command(
    name="timetable",
    description="Get anime time table for current week",
    guild=discord.Object(id=554630626175614978)
)
@app_commands.choices(timezone=[
    app_commands.Choice(name="Asia/Kolkata", value="Asia/Kolkata"),
    app_commands.Choice(name="UTC", value="UTC")
])
async def timetable_slash_command(interaction, timezone: str = None):
    log.info("Fetching timetable for timezone: %s", timezone)
    embed_var = discord.Embed(title="Title", description="Desc", color=0x00ff00)
    embed_var.add_field(name="Field1", value="hi", inline=False)
    embed_var.add_field(name="Field2", value="hi2", inline=False)

    async def callback(interaction):
        await interaction.response.send_message(f"okay selected {list(interaction.data.values())[0][0]}")


    view_var = discord.ui.View()
    dropdown_ops = [discord.SelectOption(label="label1", description="desc1"), discord.SelectOption(label="label2", description="desc2")]
    dropdown = discord.ui.Select(placeholder="select something", min_values=1, max_values=1, options=dropdown_ops)
    dropdown.callback = callback
    view_var.add_item(dropdown)
    await interaction.response.send_message(embed=embed_var, view=view_var)


client.run('')
