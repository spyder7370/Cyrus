from datetime import timedelta

import discord
from bs4 import BeautifulSoup
from discord import ButtonStyle

from components.button import DiscordButtonComponent
from components.embed import DiscordEmbedComponent
from components.view import DiscordViewComponent
from config.config import Config
from db.entity.updates_registration_entity import (
    UpdatesRegistrationModel,
    UpdatesRegistrationDao,
)
from util.datetime_utils import DateTimeUtils
from util.http_client_utils import make_get_request
from util.logger import log
from util.rss_utils import get_rss_feeds
from util.string_utils import StringUtils
from util.utils import get_value_from_button_interaction


def update_feed_refresh_time(id, current_time):
    UpdatesRegistrationDao.update_by_id(id, current_time)


def get_feed_embeds(feeds: list) -> dict:
    embed_props = []
    views = []
    base_img_url = "https://img.animeschedule.net/production/assets/public/img/"

    for _feed in feeds:
        show_name = _feed.link.rsplit("/", 1)[-1]
        headers = {
            "Authorization": Config.get_as_api_token(),
            "User-Agent": "Cyrus",
        }
        show_data = make_get_request(
            url=f"https://animeschedule.net/api/v3/anime/{show_name}",
            headers=headers,
        )
        embed_desc = BeautifulSoup(
            StringUtils.trim_to_max_length(_feed.summary, 2000)
        ).get_text(separator="\n\n", strip=True)

        embed_prop = {
            "title": f"**{show_data.get("title")}**",
            "description": f"**__{embed_desc}__**",
            "fields": [
                {
                    "name": "Summary",
                    "value": StringUtils.trim_to_max_length(
                        show_data.get("description"), 2000
                    ),
                },
                {
                    "name": "",
                    "value": "・".join(
                        f"`{genre.get('name')}`" for genre in show_data.get("genres")
                    ),
                },
            ],
            "image": f"{base_img_url}{show_data.get("imageVersionRoute")}",
            "footer": {
                "text": f"Published on: {DateTimeUtils.get_timestamp_from_unknown_string(_feed.published).strftime("%I:%M %p UTC")}"
            },
        }
        embed_props.append(embed_prop)

        buttons = []
        if show_data.get("websites").get("mal") is not None:
            buttons.append(
                DiscordButtonComponent.get_button(
                    {
                        "style": ButtonStyle.premium,
                        "label": "MAL",
                        "url": f"https://{show_data.get("websites").get("mal")}",
                    }
                )
            )
        if show_data.get("websites").get("aniList") is not None:
            buttons.append(
                DiscordButtonComponent.get_button(
                    {
                        "style": ButtonStyle.primary,
                        "label": "AniList",
                        "url": f"https://{show_data.get("websites").get("aniList")}",
                    }
                )
            )
        if _feed.link is not None:
            buttons.append(
                DiscordButtonComponent.get_button(
                    {
                        "style": ButtonStyle.secondary,
                        "label": "AS",
                        "url": _feed.link,
                    }
                )
            )

        view = DiscordViewComponent.get_view({"items": [*buttons]})
        views.append(view)
    embeds = DiscordEmbedComponent.get_embeds(embed_props)
    return {"embeds": embeds, "views": views}


async def remove_feed_button_callback(interaction):
    button_value = get_value_from_button_interaction(interaction)
    await interaction.response.edit_message(view=None)
    res = UpdatesRegistrationDao.delete(button_value)
    await interaction.followup.send(
        "Successfully removed feed"
        if res
        else "Something went wrong while removing feed"
    )


def get_deregister_embed(registration: UpdatesRegistrationModel):
    embed_props = [
        {
            "title": f"**Are you sure you want to remove the following feed for `{registration.server_name}`?**",
            "color": discord.Color.red(),
            "fields": [
                {
                    "name": "Air type",
                    "value": f"{registration.air_type}",
                    "inline": True,
                },
                {
                    "name": "Channel",
                    "value": f"<#{registration.channel_id}>",
                    "inline": True,
                },
                {
                    "name": "Requested by",
                    "value": f"<@{registration.user_id}>",
                    "inline": True,
                },
            ],
            "footer": {
                "text": f"Last refreshed on: {DateTimeUtils.get_timestamp_from_string(registration.refresh_timestamp).strftime("%I:%M %p UTC")}"
            },
        }
    ]
    embeds = DiscordEmbedComponent.get_embeds(embed_props)

    button = DiscordButtonComponent.get_button(
        {
            "style": ButtonStyle.red,
            "value": registration.server_id,
            "label": "Confirm",
            "callback": remove_feed_button_callback,
        }
    )
    view = DiscordViewComponent.get_view({"items": [button]})

    return {"embeds": embeds, "view": view}


def error_embed(server_name: str):
    heading_embed_props = [
        {
            "title": f"No feeds are available for `{server_name}`",
            "description": "Please register a feed using `/register-updates`",
            "color": discord.Color.red(),
        },
    ]
    heading_embeds = DiscordEmbedComponent.get_embeds(heading_embed_props)
    return {"embeds": heading_embeds}


def register_episode_updates(
    channel_id: str,
    user_id: str,
    server_id: str,
    server_name: str,
):
    log.info("Registering episode updates feed for %s", channel_id)
    entity: UpdatesRegistrationModel = UpdatesRegistrationModel()
    entity.refresh_timestamp = str(DateTimeUtils.get_current_utc_time())
    entity.channel_id = channel_id
    entity.user_id = user_id
    entity.server_id = server_id
    entity.server_name = server_name
    UpdatesRegistrationDao.save(entity)


def deregister_episode_updates(server_id: str, server_name: str):
    registration: UpdatesRegistrationModel = UpdatesRegistrationDao.get_by_server_id(
        server_id
    )
    if registration is None:
        return error_embed(server_name)
    return get_deregister_embed(registration)


async def schedule_updates_feed(client):
    current_time = DateTimeUtils.get_current_utc_time()
    all_registrations: list[UpdatesRegistrationModel] = UpdatesRegistrationDao.get_all()

    feeds: list = get_rss_feeds(
        "https://animeschedule.net/subrss.xml", current_time - timedelta(minutes=15)
    )
    log.info("Fetched %s feeds for episode updates", len(feeds))
    embeds_zip = get_feed_embeds(feeds)
    embeds = embeds_zip.get("embeds")
    views = embeds_zip.get("views")
    for reg in all_registrations:
        channel_id = reg.channel_id
        _id = reg.id
        channel_to_upload_to = client.get_channel(int(channel_id))
        for i, embed in enumerate(embeds):
            await channel_to_upload_to.send(embed=embed, view=views[i])
        update_feed_refresh_time(_id, current_time)
