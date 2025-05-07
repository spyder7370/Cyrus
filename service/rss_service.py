import ssl
from datetime import datetime, timedelta, timezone

import feedparser

if hasattr(ssl, "_create_unverified_context"):
    ssl._create_default_https_context = ssl._create_unverified_context


def fetch_feeds(url: str):
    feed = feedparser.parse(url)
    now = datetime.now(timezone.utc)
    time_range = timedelta(minutes=15)
    for entry in feed.entries:
        entry_date = datetime.strptime(
            entry.published, "%a, %d %b %Y %H:%M:%S %z"
        ).astimezone(timezone.utc)
        print(now - entry_date)
        print(entry_date - now)
        # if last refresh was more than time_range ago, fetch all posts from last_refresh_time till now and update last_refresh_time
        if now - entry_date <= time_range:
            print("entry")
            # print("Entry Title:", entry.title)
            # print("Entry Link:", entry.link)
            # print("Entry Published Date:", entry.published)
            # print("\n")


def schedule_feed():
    url = "https://honeysanime.com/feed/"
    fetch_feeds(url)
