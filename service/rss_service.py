from datetime import timedelta

from bs4 import BeautifulSoup
from discord import ButtonStyle

from components.button import DiscordButtonComponent
from components.embed import DiscordEmbedComponent
from components.view import DiscordViewComponent
from db.entity.rss_registration_entity import RssRegistrationModel, RssRegistrationDao
from util.datetime_utils import DateTimeUtils
from util.list_utils import ListUtils
from util.logger import log
from util.rss_utils import get_rss_feeds
from util.string_utils import StringUtils
from util.utils import get_value_from_button_interaction


async def rss_button_callback(interaction):
    button_value = get_value_from_button_interaction(interaction)
    await interaction.response.edit_message(view=None)
    res = RssRegistrationDao.delete_by_id(button_value)
    await interaction.followup.send(
        "Successfully removed feed"
        if res
        else "Something went wrong while removing feed"
    )


def get_all_feeds_embed(feeds: list[RssRegistrationModel], server_name: str):
    views = []
    for _feed in feeds:
        button = DiscordButtonComponent.get_button(
            {
                "style": ButtonStyle.red,
                "value": _feed.id,
                "label": "Remove feed",
                "callback": rss_button_callback,
            }
        )
        view = DiscordViewComponent.get_view({"items": [button]})
        views.append(view)

    heading_embed_props = [
        {
            "title": f"**All RSS feeds for `{server_name}`**",
        },
    ]
    heading_embeds = DiscordEmbedComponent.get_embeds(heading_embed_props)

    embed_props = [
        {
            "title": _feed.name,
            "fields": [
                {
                    "name": "Link",
                    "value": f"[Click here]({_feed.url})",
                    "inline": True,
                },
                {
                    "name": "Channel",
                    "value": f"<#{_feed.channel_id}>",
                    "inline": True,
                },
                {
                    "name": "Requested by",
                    "value": f"<@{_feed.user_id}>",
                    "inline": True,
                },
            ],
            "footer": {
                "text": f"Last refreshed on: {DateTimeUtils.get_timestamp_from_string(_feed.refresh_timestamp).strftime("%I:%M %p UTC")}"
            },
        }
        for _feed in feeds
    ]
    embeds = DiscordEmbedComponent.get_embeds(embed_props)

    return {
        "heading_embeds": heading_embeds,
        "embeds": embeds,
        "views": views,
    }


def get_feed_embeds(feeds: list) -> list:
    embed_props = [
        {
            "title": _feed.title,
            "description": BeautifulSoup(
                StringUtils.trim_to_max_length(_feed.summary, 2000)
            ).get_text(separator="\n\n", strip=True),
            "fields": [
                {
                    "name": "",
                    "value": f"[Read more]({_feed.link})",
                }
            ],
            "footer": {
                "text": f"Published on: {DateTimeUtils.get_timestamp_from_unknown_string(_feed.published).strftime("%I:%M %p UTC")}"
            },
        }
        for _feed in feeds
    ]
    return DiscordEmbedComponent.get_embeds(embed_props)


def get_error_embed(msg: str = None) -> dict:
    return {
        "heading_embeds": [DiscordEmbedComponent.get_error_embed(msg)],
        "view": None,
    }


def update_feed_refresh_time(id, current_time):
    RssRegistrationDao.update_by_id(id, current_time)


async def schedule_feeds(client):
    current_time = DateTimeUtils.get_current_utc_time()

    all_registrations: list[RssRegistrationModel] = RssRegistrationDao.get_all()
    feeds_to_channel_map = {}
    for registration in all_registrations:
        if registration.url not in feeds_to_channel_map:
            feeds_to_channel_map[registration.url] = []
        feeds_to_channel_map[registration.url].append(
            {"channel_id": registration.channel_id, "id": registration.id}
        )

    for url, channel_ids in feeds_to_channel_map.items():
        feeds: list = get_rss_feeds(url, current_time - timedelta(minutes=15))
        log.info("Fetched %s feeds for url %s", len(feeds), url)
        embeds = get_feed_embeds(feeds)
        for dic in channel_ids:
            channel_id = dic.get("channel_id")
            _id = dic.get("id")
            channel_to_upload_to = client.get_channel(int(channel_id))
            for embed in embeds:
                await channel_to_upload_to.send(embed=embed)
            update_feed_refresh_time(_id, current_time)


def register_rss(
    channel_id: str,
    url: str,
    user_id: str,
    server_id: str,
    server_name: str,
    alias: str,
):
    if StringUtils.is_empty(alias):
        alias = url
    log.info("Registering rss feed for %s", channel_id)
    entity: RssRegistrationModel = RssRegistrationModel()
    entity.refresh_timestamp = str(DateTimeUtils.get_current_utc_time())
    entity.url = url
    entity.name = alias
    entity.channel_id = channel_id
    entity.user_id = user_id
    entity.server_id = server_id
    entity.server_name = server_name
    RssRegistrationDao.save(entity)


def get_rss_feeds_for_server(server_id: str, server_name: str):
    try:
        log.info("Getting all rss feeds for server %s", server_id)
        feeds: list[RssRegistrationModel] = RssRegistrationDao.get_all_by_server_id(
            server_id
        )
        if ListUtils.is_empty(feeds):
            feeds = []
        return get_all_feeds_embed(feeds, server_name)
    except Exception as e:
        log.error(
            "Encountered exception while getting all rss feeds for server %s: %s",
            server_id,
            str(e),
            exc_info=e,
        )
        return get_error_embed()
