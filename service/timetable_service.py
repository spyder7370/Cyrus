import pytz

from util.datetime_utils import DateTimeUtils
from util.http_client_utils import make_get_request
from util.logger import log


def get_timetable_data():
    headers = {
        'Authorization': 'Bearer ',
        'User-Agent': 'Cyrus'
    }
    timeline_data = make_get_request(url='https://animeschedule.net/api/v3/timetables/sub', headers=headers)

    for data in timeline_data:
        current_timestamp = DateTimeUtils.get_current_time()
        episode_timestamp = DateTimeUtils.get_timestamp_from_string(data['episodeDate'])
        if DateTimeUtils.are_dates_equal(current_timestamp, episode_timestamp):
            log.info("%s release today", data['title'])

# def get_timetable():

get_timetable()