from discord.ui import View


class DiscordViewComponent:
    @staticmethod
    def get_view(props: dict) -> View:
        view_var = View()
        items = props.get("items")

        for item in items:
            view_var.add_item(item)
        return view_var
