class ListUtils:
    @staticmethod
    def is_empty(input_list: list) -> bool:
        return input_list is None or len(list) == 0

    @staticmethod
    def is_not_empty(input_list: list) -> bool:
        return ListUtils.is_empty(input_list=input_list) is False