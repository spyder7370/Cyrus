from datetime import datetime, timezone, tzinfo, date

import pytz

from util.string_utils import StringUtils


class DateTimeUtils:
    @staticmethod
    def get_current_time(tz: tzinfo = None) -> datetime:
        current_utc_time = datetime.now(timezone.utc)

        if tz is None:
            return current_utc_time

        return current_utc_time.astimezone(tz=tz)

    @staticmethod
    def get_current_utc_time() -> datetime:
        return DateTimeUtils.get_current_time()

    @staticmethod
    def convert_timestamp_from_utc(
        timestamp: datetime = None, tz: tzinfo = None
    ) -> datetime | None:
        if timestamp is None or tz is None:
            return None

        return timestamp.astimezone(tz=tz)

    @staticmethod
    def convert_timestamp_to_utc(timestamp: datetime = None) -> datetime | None:
        if timestamp is None:
            return None

        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def get_timestamp_from_string(
        timestamp_string: str = None, tz: tzinfo = None
    ) -> datetime | None:
        if StringUtils.is_empty(timestamp_string):
            return None

        if tz is None:
            return datetime.fromisoformat(timestamp_string)

        return datetime.fromisoformat(timestamp_string).astimezone(tz=tz)

    @staticmethod
    def get_timestamp_from_date(date_string: str, tz: tzinfo = None) -> datetime | None:
        if StringUtils.is_empty(date_string):
            return None
        return datetime.strptime(date_string, "%Y-%m-%d").replace(tzinfo=tz)

    @staticmethod
    def get_date_from_string(
        timestamp_string: str = None, tz: tzinfo = None
    ) -> date | None:
        if StringUtils.is_empty(timestamp_string):
            return None

        if tz is None:
            return datetime.fromisoformat(timestamp_string).date()

        return datetime.fromisoformat(timestamp_string).astimezone(tz=tz).date()

    @staticmethod
    def are_dates_equal(timestamp1: datetime, timestamp2: datetime) -> bool:
        if timestamp1 is None or timestamp2 is None:
            return False

        return timestamp1.date() == timestamp2.date()

    @staticmethod
    def does_timestamp_lie_between(
        timestamp: datetime, start_timestamp: datetime, end_timestamp: datetime
    ) -> bool:
        if timestamp is None or start_timestamp is None or end_timestamp is None:
            return False

        return start_timestamp <= timestamp <= end_timestamp

    @staticmethod
    def get_timezone_from_string(tz_str: str) -> tzinfo:
        return pytz.timezone(tz_str)
