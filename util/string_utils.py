class StringUtils:
    @staticmethod
    def is_empty(string: str) -> bool:
        return string is None or len(string.strip()) == 0

    @staticmethod
    def is_not_empty(string: str) -> bool:
        return StringUtils.is_empty(string=string) is False

    @staticmethod
    def trim_to_max_length(text: str, max_length: int = 1000) -> str:
        return text[:max_length] + "..." if len(text) > max_length else text
