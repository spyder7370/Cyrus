import ssl
from datetime import datetime, timedelta, timezone

import feedparser

from util.string_utils import StringUtils

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def get_rss_feeds(url: str, start_time: datetime, time_range: timedelta) -> list:
    filtered_feeds = []
    if StringUtils.is_empty(url):
        return filtered_feeds

    if start_time is None:
        start_time = datetime.now(timezone.utc)

    feed = feedparser.parse(url)
    for entry in feed.entries:
        entry_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
        if start_time - entry_date <= time_range:
            filtered_feeds.append(entry)
            # print("Entry Title:", entry.title)
            # print("Entry Link:", entry.link)
            # print("Entry Published Date:", entry.published)
            # print("\n")
    return filtered_feeds
