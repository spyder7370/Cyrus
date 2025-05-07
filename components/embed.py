from discord import Embed


class DiscordEmbedComponent:
    @staticmethod
    def get_embeds(props: list[dict]) -> list[Embed]:
        embeds = []
        for prop in props:
            embed_var = Embed(
                title=prop.get("title"),
                description=prop.get("description"),
                color=prop.get("color"),
            )
            fields: list[dict] = prop.get("fields", [])
            for field in fields:
                if not field:
                    continue
                embed_var.add_field(
                    name=field.get("name"),
                    value=field.get("value"),
                    inline=field.get("inline"),
                )
            embed_var.set_thumbnail(url=prop.get("thumbnail"))
            embeds.append(embed_var)
        return embeds

    @staticmethod
    def get_error_embed(
        msg: str = "Something went wrong, please try again later.",
    ) -> Embed:
        return Embed(title="Request Failed", description=msg, color=0xF90F07)
