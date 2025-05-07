from util.utils import get_config


class Config:
    @staticmethod
    def get_discord_token():
        return get_config("DISCORD_TOKEN")

    @staticmethod
    def get_as_api_token():
        return get_config("AS_API_TOKEN")
