-- timetable definition

CREATE TABLE timetable
(
    refresh_timestamp TEXT NOT NULL,
    "type"            TEXT NOT NULL,
    json              TEXT NOT NULL,
    weeks             TEXT NOT NULL,
    primary key ("type")
);

CREATE TABLE rss_registration
(
    id                TEXT NOT NULL,
    refresh_timestamp TEXT NOT NULL,
    url               TEXT NOT NULL,
    name              TEXT NOT NULL,
    channel_id        TEXT NOT NULL,
    user_id           TEXT NOT NULL,
    server_id         TEXT NOT NULL,
    server_name       TEXT NOT NULL,
    primary key (channel_id, url, server_id)
);

CREATE TABLE updates_registration
(
    id                TEXT NOT NULL,
    refresh_timestamp TEXT NOT NULL,
    air_type          TEXT NOT NULL,
    channel_id        TEXT NOT NULL,
    user_id           TEXT NOT NULL,
    server_id         TEXT NOT NULL,
    server_name       TEXT NOT NULL,
    primary key (server_id)
);