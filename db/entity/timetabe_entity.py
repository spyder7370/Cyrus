from sqlalchemy import text

from db.db import db, conn, metadata

from util.logger import log

TimeTableEntity = db.Table(
    "timetable",
    metadata,
    db.Column("refresh_timestamp", db.Text(), nullable=False),
    db.Column("type", db.Text(), nullable=False, primary_key=True),
    db.Column("json", db.Text(), nullable=False),
    db.Column("weeks", db.Text(), nullable=False),
)


class TimeTableModel:
    refresh_timestamp: str
    type: str
    json: str
    weeks: str


class TimeTableDao:
    @staticmethod
    def get_by_type(air_type: str) -> TimeTableModel | None:
        try:
            query = f'SELECT * FROM timetable WHERE type = "{air_type}"'
            return conn.execute(text(query)).fetchone()
        except Exception as e:
            log.error(
                "Exception encountered while executing TimeTableDao.get_by_timezone_and_type %s",
                str(e),
                exc_info=e,
            )
            return None

    @staticmethod
    def save(entity: TimeTableModel):
        try:
            query = db.insert(TimeTableEntity).values(
                refresh_timestamp=entity.refresh_timestamp,
                type=entity.type,
                json=entity.json,
                weeks=entity.weeks,
            )
            result = conn.execute(query)
            conn.commit()
            return result
        except Exception as e:
            log.error(
                "Exception encountered while executing TimeTableDao.save %s",
                str(e),
                exc_info=e,
            )
            return []

    @staticmethod
    def delete(air_type: str):
        try:
            query = TimeTableEntity.delete().where(
                TimeTableEntity.columns.type == air_type
            )
            conn.execute(query)
            conn.commit()
            return True
        except Exception as e:
            log.error(
                "Exception encountered while executing TimeTableDao.delete %s",
                str(e),
                exc_info=e,
            )
            return False
