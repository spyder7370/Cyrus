from discord import SelectOption
from discord.ui import Select

from util.list_utils import ListUtils
from util.string_utils import StringUtils


def get_dropdown_options(options: list[dict]) -> list:
    dropdown_options = []
    if ListUtils.is_empty(options):
        return dropdown_options

    for option in options:
        label = option.get('label')
        description = option.get('description')
        if StringUtils.is_not_empty(label) and StringUtils.is_not_empty(description):
            dropdown_options.append(SelectOption(label=label, description=description))
    return dropdown_options


def get_dropdown_component(props: dict) -> Select:
    options_raw = props.get('options')
    callback_function = props.get('callback')

    if ListUtils.is_empty(options_raw) or callback_function is None:
        return Select()

    dropdown_options = get_dropdown_options(options_raw)
    dropdown = Select(
        placeholder=props.get('placeholder'),
        min_values=props.get('min_values'),
        max_values=props.get('max_values'),
        options=dropdown_options
    )
    dropdown.callback = callback_function
    return dropdown
