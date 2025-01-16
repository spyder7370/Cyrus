from discord import Embed

def get_embed() -> Embed:
    embed_var = Embed(title="Title", description="Desc", color=0xF1C232)
    embed_var.add_field(name="Field1", value="hi", inline=False)
    embed_var.add_field(name="Field2", value="hi2", inline=False)
    return embed_var