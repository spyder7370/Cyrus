import uuid

from sqlalchemy import text

from db.db import db, conn, metadata
from util.logger import log

RssRegistrationEntity = db.Table(
    "rss_registration",
    metadata,
    db.Column("id", db.Text(), nullable=False),
    db.Column("refresh_timestamp", db.Text(), nullable=False),
    db.Column("url", db.Text(), nullable=False, primary_key=True),
    db.Column("name", db.Text(), nullable=False),
    db.Column("channel_id", db.Text(), nullable=False, primary_key=True),
    db.Column("user_id", db.Text(), nullable=False),
    db.Column("server_id", db.Text(), nullable=False, primary_key=True),
    db.Column("server_name", db.Text(), nullable=False),
)


class RssRegistrationModel:
    id: str
    refresh_timestamp: str
    url: str
    name: str
    channel_id: str
    user_id: str
    server_id: str
    server_name: str


class RssRegistrationDao:
    @staticmethod
    def get_all() -> list[RssRegistrationModel] | None:
        try:
            query = "SELECT * FROM rss_registration"
            return conn.execute(text(query)).fetchall()
        except Exception as e:
            log.error(
                "Exception encountered while executing RssRegistrationDao.get_all %s",
                str(e),
                exc_info=e,
            )
            return []

    @staticmethod
    def get_all_by_server_id(server_id: str) -> list[RssRegistrationModel] | None:
        try:
            query = f"SELECT * FROM rss_registration where server_id = {server_id}"
            return conn.execute(text(query)).fetchall()
        except Exception as e:
            log.error(
                "Exception encountered while executing RssRegistrationDao.get_all_by_server_id %s",
                str(e),
                exc_info=e,
            )
            return []

    @staticmethod
    def get_by_id(id: str) -> RssRegistrationModel | None:
        try:
            query = f"SELECT * FROM rss_registration where id = {id}"
            return conn.execute(text(query)).fetchone()
        except Exception as e:
            log.error(
                "Exception encountered while executing RssRegistrationDao.get_by_id %s",
                str(e),
                exc_info=e,
            )
            return None

    @staticmethod
    def save(entity: RssRegistrationModel):
        try:
            query = db.insert(RssRegistrationEntity).values(
                id=str(uuid.uuid4()),
                refresh_timestamp=entity.refresh_timestamp,
                url=entity.url,
                name=entity.name,
                channel_id=entity.channel_id,
                user_id=entity.user_id,
                server_id=entity.server_id,
                server_name=entity.server_name,
            )
            result = conn.execute(query)
            conn.commit()
            return result
        except Exception as e:
            log.error(
                "Exception encountered while executing RssRegistrationDao.save %s",
                str(e),
                exc_info=e,
            )
            return []

    @staticmethod
    def delete_by_id(id: str):
        try:
            query = RssRegistrationEntity.delete().where(
                RssRegistrationEntity.columns.id == id
            )
            conn.execute(query)
            conn.commit()
            return True
        except Exception as e:
            log.error(
                "Exception encountered while executing RssRegistrationDao.delete %s",
                str(e),
                exc_info=e,
            )
            return False

    @staticmethod
    def update_by_id(id: str, refresh_timestamp: str):
        try:
            query = db.update(RssRegistrationEntity).values(
                id=id,
                refresh_timestamp=refresh_timestamp,
            )
            result = conn.execute(query)
            conn.commit()
            return result
        except Exception as e:
            log.error(
                "Exception encountered while executing RssRegistrationDao.update_by_id %s",
                str(e),
                exc_info=e,
            )
            return []
