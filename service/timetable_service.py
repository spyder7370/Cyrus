import json
from datetime import datetime, tzinfo, timezone

from components.dropdown import DiscordDropdownComponent
from components.embed import DiscordEmbedComponent
from components.view import DiscordViewComponent
from config.config import Config
from constants.time_table_constants import ALLOWED_TIMEZONES, ALLOWED_AIR_TYPES
from db.entity.timetabe_entity import TimeTableDao, TimeTableModel
from util.datetime_utils import DateTimeUtils
from util.http_client_utils import make_get_request
from util.list_utils import ListUtils
from util.logger import log
from util.utils import get_value_from_interaction


async def send_timetable_embeds_to_discord(
    interaction,
    timezone: str,
    type: str,
    current_timestamp: datetime = None,
    is_heading_followup: bool = False,
):
    data: dict = get_timetable(timezone, type, current_timestamp)
    embeds = data.get("embeds", [])
    view = data.get("view")
    embed_chunks = ListUtils.chunk_list(embeds, 10)
    if is_heading_followup:
        await interaction.followup.send(embeds=data.get("heading_embeds"))
    else:
        await interaction.response.send_message(embeds=data.get("heading_embeds"))
    for i, chunk in enumerate(embed_chunks):
        await interaction.followup.send(
            embeds=chunk, **({"view": view} if i == len(embed_chunks) - 1 else {})
        )


def filter_timetable_data(
    timetable_data: list[dict],
    start_timestamp: datetime,
    end_timestamp: datetime,
    filter_on_date: bool,
    tz: tzinfo = timezone.utc,
):
    timetable = []
    for data in timetable_data:
        episode_timestamp = DateTimeUtils.get_timestamp_from_string(
            data.get("episodeDate"), tz
        )
        if filter_on_date is True and DateTimeUtils.are_dates_equal(
            start_timestamp, episode_timestamp
        ):
            timetable.append(data)
        elif filter_on_date is False and DateTimeUtils.does_timestamp_lie_between(
            episode_timestamp, start_timestamp, end_timestamp
        ):
            log.info("%s release today", data.get("title"))
            timetable.append(data)
    return timetable


def get_timetable_data(
    start_timestamp: datetime | None,
    end_timestamp: datetime | None,
    tz: tzinfo,
    air_type: str,
):
    try:
        headers = {
            "Authorization": Config.get_as_api_token(),
            "User-Agent": "Cyrus",
        }
        timetable_data: list[dict] = make_get_request(
            url=f"https://animeschedule.net/api/v3/timetables/{air_type if air_type else 'sub'}",
            headers=headers,
        )
        if start_timestamp is None or end_timestamp is None:
            return timetable_data

        return filter_timetable_data(
            timetable_data, start_timestamp, end_timestamp, False, tz
        )
    except Exception as e:
        log.error(
            "Exception encountered while fetching timetable %s", str(e), exc_info=e
        )
        return []


def refresh_timetable_data_in_db(
    timezone_str: str, air_type: str, tz: tzinfo, current_timestamp: datetime
):
    timetable_data: list[dict] = get_timetable_data(None, None, tz, air_type)

    weeks = dict()
    for data in timetable_data:
        episode_day = DateTimeUtils.get_date_from_string(data.get("episodeDate"))
        weeks[(str(episode_day))] = True

    entity: TimeTableModel = TimeTableModel()
    entity.refresh_timestamp = str(current_timestamp)
    entity.type = air_type
    entity.json = json.dumps(timetable_data)
    entity.weeks = ",".join(weeks)
    entity.timezone = timezone_str
    TimeTableDao.save(entity)

    return timetable_data, entity.weeks


async def timetable_dropdown_callback(interaction):
    await interaction.response.edit_message(view=None)
    dropdown_value: dict = json.loads(get_value_from_interaction(interaction))
    date_str = dropdown_value.get("week")
    timezone_str = dropdown_value.get("timezone")
    tz = DateTimeUtils.get_timezone_from_string(timezone_str)
    current_timestamp = DateTimeUtils.get_timestamp_from_date(date_str, tz)

    await send_timetable_embeds_to_discord(
        interaction,
        timezone_str,
        dropdown_value.get("air_type"),
        current_timestamp,
        True,
    )


def get_timetable_embed(
    data: list[dict], day, weeks, air_type: str, timezone_str: str
) -> dict:
    tz = DateTimeUtils.get_timezone_from_string(timezone_str)
    base_img_url = "https://img.animeschedule.net/production/assets/public/img/"
    heading_embed_props = [
        {
            "title": f"`{air_type.upper()}` **Anime schedule for {datetime.strptime(day, "%Y-%m-%d").strftime('%B %d')}**",
            "color": 0,
        },
    ]
    embed_props = [
        {
            "title": _data.get("title", "Untitled"),
            "color": 0,
            "thumbnail": f"{base_img_url}{_data.get("imageVersionRoute")}",
            "fields": [
                {
                    "name": "Episode",
                    "value": f"{_data.get("episodeNumber", "N/A")}",
                    "inline": True,
                },
                {
                    "name": "Airing on",
                    "value": f"{DateTimeUtils.get_timestamp_from_string(_data.get("episodeDate"), tz).strftime(f"%I:%M %p")}",
                    "inline": True,
                },
                (
                    {
                        "name": "Air type",
                        "value": f"{_data.get("airType", "N/A")}",
                        "inline": True,
                    }
                    if air_type == "all"
                    else None
                ),
            ],
        }
        for _data in data
    ]
    heading_embeds = DiscordEmbedComponent.get_embeds(heading_embed_props)
    embeds = DiscordEmbedComponent.get_embeds(embed_props)

    dropdown_var = DiscordDropdownComponent.get_dropdown_component(
        {
            "options": [
                {
                    "label": datetime.strptime(week, "%Y-%m-%d").strftime("%B %d"),
                    "value": f'{{"week": "{week}", "air_type": "{air_type}", "timezone": "{timezone_str}"}}',
                    "default": week == day,
                }
                for week in weeks
            ],
            "callback": timetable_dropdown_callback,
            "placeholder": "Select day",
            "min_values": 1,
            "max_values": 1,
        }
    )
    view_var = DiscordViewComponent.get_view({"items": [dropdown_var]})

    return {"heading_embeds": heading_embeds, "embeds": embeds, "view": view_var}


def get_timetable_error_embed(msg: str = None) -> dict:
    return {"embed": DiscordEmbedComponent.get_error_embed(msg), "view": None}


def get_timetable(
    timezone_str: str, air_type: str, current_timestamp: datetime = None
) -> dict:
    try:
        if timezone_str not in ALLOWED_TIMEZONES or air_type not in ALLOWED_AIR_TYPES:
            return get_timetable_error_embed(
                "Invalid input value, please select a valid value."
            )

        timezone = DateTimeUtils.get_timezone_from_string(timezone_str)
        if not current_timestamp:
            current_timestamp = DateTimeUtils.get_current_time(timezone)
        current_day = str(current_timestamp.date())
        # Check if timetable is there for type
        existing_data: TimeTableModel = TimeTableDao.get_by_type(air_type)
        if existing_data is None or current_day not in existing_data.weeks:
            # Refresh data in db and construct embed
            if existing_data is not None:
                TimeTableDao.delete(air_type)
            new_data, weeks = refresh_timetable_data_in_db(
                timezone_str,
                air_type,
                timezone,
                DateTimeUtils.convert_timestamp_to_utc(current_timestamp),
            )
            filtered_data = filter_timetable_data(
                new_data, current_timestamp, current_timestamp, True, timezone
            )
            return get_timetable_embed(
                filtered_data, current_day, weeks.split(","), air_type, timezone_str
            )

        # Construct embed
        filtered_data = filter_timetable_data(
            json.loads(existing_data.json),
            current_timestamp,
            current_timestamp,
            True,
            timezone,
        )
        return get_timetable_embed(
            filtered_data,
            current_day,
            existing_data.weeks.split(","),
            air_type,
            timezone_str,
        )
    except Exception as e:
        log.error(
            "Exception encountered while getting timetable for discord %s",
            str(e),
            exc_info=e,
        )
        return get_timetable_error_embed()
