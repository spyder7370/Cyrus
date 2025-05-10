import uuid

from sqlalchemy import text

from db.db import db, conn, metadata
from util.logger import log

UpdatesRegistrationEntity = db.Table(
    "updates_registration",
    metadata,
    db.Column("id", db.Text(), nullable=False),
    db.Column("refresh_timestamp", db.Text(), nullable=False),
    db.Column("air_type", db.Text(), nullable=False),
    db.Column("channel_id", db.Text(), nullable=False),
    db.Column("user_id", db.Text(), nullable=False),
    db.Column("server_id", db.Text(), nullable=False, primary_key=True),
    db.Column("server_name", db.Text(), nullable=False),
)


class UpdatesRegistrationModel:
    id: str
    refresh_timestamp: str
    air_type: str
    channel_id: str
    user_id: str
    server_id: str
    server_name: str


class UpdatesRegistrationDao:
    @staticmethod
    def get_all() -> list[UpdatesRegistrationModel] | None:
        try:
            query = "SELECT * FROM updates_registration"
            return conn.execute(text(query)).fetchall()
        except Exception as e:
            log.error(
                "Exception encountered while executing UpdatesRegistrationDao.get_all %s",
                str(e),
                exc_info=e,
            )
            return []

    @staticmethod
    def get_by_server_id(server_id: str) -> UpdatesRegistrationModel | None:
        try:
            query = f"SELECT * FROM updates_registration where server_id = {server_id}"
            return conn.execute(text(query)).fetchone()
        except Exception as e:
            log.error(
                "Exception encountered while executing UpdatesRegistrationDao.get_by_server_id %s",
                str(e),
                exc_info=e,
            )
            return None

    @staticmethod
    def get_by_id(id: str) -> UpdatesRegistrationModel | None:
        try:
            query = f"SELECT * FROM updates_registration where id = {id}"
            return conn.execute(text(query)).fetchone()
        except Exception as e:
            log.error(
                "Exception encountered while executing UpdatesRegistrationDao.get_by_id %s",
                str(e),
                exc_info=e,
            )
            return None

    @staticmethod
    def save(entity: UpdatesRegistrationModel):
        try:
            query = db.insert(UpdatesRegistrationEntity).values(
                id=str(uuid.uuid4()),
                refresh_timestamp=entity.refresh_timestamp,
                air_type="sub",
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
                "Exception encountered while executing UpdatesRegistrationDao.save %s",
                str(e),
                exc_info=e,
            )
            return []

    @staticmethod
    def delete(server_id: str):
        try:
            query = UpdatesRegistrationEntity.delete().where(
                UpdatesRegistrationEntity.columns.server_id == server_id
            )
            conn.execute(query)
            conn.commit()
            return True
        except Exception as e:
            log.error(
                "Exception encountered while executing UpdatesRegistrationDao.delete %s",
                str(e),
                exc_info=e,
            )
            return False

    @staticmethod
    def update_by_id(id: str, refresh_timestamp: str):
        try:
            query = db.update(UpdatesRegistrationEntity).values(
                id=id,
                refresh_timestamp=refresh_timestamp,
            )
            result = conn.execute(query)
            conn.commit()
            return result
        except Exception as e:
            log.error(
                "Exception encountered while executing UpdatesRegistrationDao.update_by_id %s",
                str(e),
                exc_info=e,
            )
            return []
