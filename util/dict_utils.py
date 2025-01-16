class DictUtils:
    @staticmethod
    def is_empty(input_dict: dict) -> bool:
        return input_dict is None or len(input_dict) == 0

    @staticmethod
    def is_not_empty(input_dict: dict) -> bool:
        return DictUtils.is_empty(input_dict=input_dict) is False