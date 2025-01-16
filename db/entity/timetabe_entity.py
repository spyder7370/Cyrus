import enum

from db.db import cursor
from util.list_utils import ListUtils


class TimeTableEntity(enum.Enum):
    refresh_timestamp = "refresh_timestamp",
    type = "type",
    json = "json",
    weeks = "weeks",
    timezone = "timezone"


class TimeTableDao:
    @staticmethod
    def get_all_by_query_date_and_timezone_and_type(timestamp: str, tz: str, type: str) -> list[TimeTableEntity]:
        query = f"SELECT * FROM timetable WHERE type = {type} AND timezone = {tz} AND weeks LIKE %{timestamp}%"
        result = cursor.execute(query).fetchall()

        if ListUtils.is_empty(result):
            return []
        return result
