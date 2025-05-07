class ListUtils:
    @staticmethod
    def is_empty(input_list: list) -> bool:
        return input_list is None or len(input_list) == 0

    @staticmethod
    def is_not_empty(input_list: list) -> bool:
        return ListUtils.is_empty(input_list=input_list) is False

    @staticmethod
    def chunk_list(input_list, chunk_size=10):
        if not isinstance(input_list, list):
            return []
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            chunk_size = 10
        return [
            input_list[i : i + chunk_size]
            for i in range(0, len(input_list), chunk_size)
        ]
