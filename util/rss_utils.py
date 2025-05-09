import ssl
from datetime import datetime, timezone

import dateutil.parser
import feedparser

from util.logger import log
from util.string_utils import StringUtils

if hasattr(ssl, "_create_unverified_context"):
    ssl._create_default_https_context = ssl._create_unverified_context


def get_rss_feeds(url: str, start_time: datetime) -> list:
    filtered_feeds = []
    try:
        if StringUtils.is_empty(url):
            return filtered_feeds

        if start_time is None:
            start_time = datetime.now(timezone.utc)

        feed = feedparser.parse(url)
        for entry in feed.entries:
            entry_date = dateutil.parser.parse(entry.published)
            if start_time <= entry_date:
                filtered_feeds.append(entry)
        return filtered_feeds
    except Exception as e:
        log.error(
            "Exception encountered while fetching rss feed %s", str(e), exc_info=e
        )
        return filtered_feeds
