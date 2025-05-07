class StringUtils:
    @staticmethod
    def is_empty(string: str) -> bool:
        return string is None or len(string.strip()) == 0

    @staticmethod
    def is_not_empty(string: str) -> bool:
        return StringUtils.is_empty(string=string) is False
