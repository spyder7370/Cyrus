-- timetable definition

CREATE TABLE timetable (
	refresh_timestamp TEXT NOT NULL,
	"type" TEXT NOT NULL,
	json TEXT NOT NULL,
	weeks TEXT NOT NULL,
	primary key("type")
);