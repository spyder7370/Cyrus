import os

from util.logger import log


def get_config(key: str):
    try:
        return os.environ[key]
    except Exception as e:
        log.error("Environment variable %s not found: %s", key, str(e), exc_info=e)
        raise e


def get_value_from_interaction(interaction):
    try:
        return list(interaction.data.values())[0][0]
    except Exception as e:
        log.error(
            "Exception encountered while getting value from discord interaction %s",
            str(e),
            exc_info=e,
        )
        return None


def get_value_from_button_interaction(interaction):
    try:
        return interaction.data.get("custom_id")
    except Exception as e:
        log.error(
            "Exception encountered while getting button value from discord interaction %s",
            str(e),
            exc_info=e,
        )
        return None
