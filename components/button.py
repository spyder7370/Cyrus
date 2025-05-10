from discord.ui import Button


class DiscordButtonComponent:
    @staticmethod
    def get_button(props: dict) -> Button:
        callback_function = props.get("callback")
        button_var = Button(
            style=props.get("style"),
            custom_id=props.get("value"),
            label=props.get("label"),
            url=props.get("url"),
        )
        button_var.callback = callback_function
        return button_var
