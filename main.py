import discord
import os
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()

class BattleArena:
    def __init__(self, user_id: int, id: str, password: int | None, name: str,
                 max_players: int | None, visibility: str | None, type: str |
                 None, format: str | None) -> None:
        # Arena properties
        self.id = id
        self.name = name
        self.password = password
        self.type = type
        self.visibility = visibility
        self.format = format
        self.max_players = max_players

        # Metadata
        self.user_id = user_id
        # TODO: Add field
        # self.data_time_created = ""
        pass

# TODO: Make a dictionary of guild id's to lists of BattleArenas
arenas: dict[int, BattleArena] = {}

thumbnails: dict[str, str] = {
    "ssbu": r"https://www.smashbros.com/assets_v2/img/howtoplay/top_icon_basic_pc.png"
}

types_to_colors: dict[str, int] = {
    "None": 0xFFFFFF,
    "All Skill Levels": 0xFFBD0E,
    "Veteran Players": 0xCF2845,
    "Glorious Smashers": 0x795BB7,
    "Anything Goes": 0x57AFED,
    "Playground": 0x1DB247,
    "amiibo Battle": 0x1F9796,
    # TODO: Find a picture of the actual color
    "Beginners Only": 0x808000,
    "Elite Only": 0xFFBE0E 
}

visibility_options: list[str] = [
    "Public",
    "Friends"
]

format_options: list[str] = [
    "4-Player Smash",
    "3-Player Smash",
    "1-on-1",
    "Team Battle"
]

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(
    name="arena", 
    description="Open a Battle Arena"
)
@discord.option(
    "id",
    discord.SlashCommandOptionType.string,
    description="The ID of the Battle Arena",
    min_length=5,
    max_length=5
)
@discord.option(
    "password", 
    discord.SlashCommandOptionType.integer,
    description="The password of the Battle Arena, which can be 8 digits at most",
    max_value=99999999,
    required=False
)
@discord.option(
    "name", 
    discord.SlashCommandOptionType.string,
    description="The name of the Battle Arena",
    max_length=22,
    required=False
)
@discord.option(
    "max_players", 
    discord.SlashCommandOptionType.integer,
    description="The maximum number of players allowed in the Battle Arena",
    min_value=2,
    max_value=8,
    required=False
)
@discord.option(
    "type",
    discord.SlashCommandOptionType.string,
    description="The type of the Battle Arena",
    choices=types_to_colors.keys(),
    required=False
)
@discord.option(
    "format",
    discord.SlashCommandOptionType.string,
    description="The format of the Battle Arena",
    choices=format_options,
    required=False
)
async def add_arena(
    ctx: discord.ApplicationContext, 
    id: str,
    password: int | None,
    name: str | None,
    max_players: int | None,
    type: str | None,
    format: str | None
):
    # TODO: Add ID validation
    hash_input = ctx.author.id + ctx.guild_id
    if hash_input in arenas:
        await ctx.respond("You already have an arena open!")
    else:
        arena_name = name if name is not None else f"{ctx.author.name}'s Arena"
        arena_color = types_to_colors[type] if type is not None else types_to_colors["None"]

        new_arena = BattleArena(ctx.author.id, id, password, arena_name,
                                max_players, "", type, format)
        avatar_url = ctx.author.avatar.url if ctx.author.avatar is not None else ctx.author.default_avatar.url
        arenas[hash_input] = new_arena

        response_embed = (
            discord.Embed(title=new_arena.name, color=arena_color)
            .add_field(name="ID:", value=new_arena.id)
            .set_footer(text=f"Owned by {ctx.author.name}", icon_url=avatar_url)
            .set_thumbnail(url=thumbnails["ssbu"])
        )

        # Adding optional fields
        if password is not None:
            response_embed.add_field(name="Password:", value=str(password))
        if max_players is not None:
            response_embed.add_field(name="Max Players:", value=str(max_players))
        if type is not None:
            response_embed.add_field(name="Type:", value=type)
        if format is not None:
            response_embed.add_field(name="Format:", value=format)

        await ctx.respond(embed=response_embed)

@bot.slash_command(name="close")
async def close_arena(ctx: discord.ApplicationContext):
    hash_input = ctx.author.id + ctx.guild_id
    cur_arena = arenas.pop(hash_input, None)
    if cur_arena is not None:
        await ctx.respond("Your arena has been closed!", ephemeral=True)
    else:
        await ctx.respond("You don't have an arena to close!", ephemeral=True)

@bot.slash_command(name="list")
async def list_arenas(ctx: discord.ApplicationContext):
    response_embed = discord.Embed(title=f"{ctx.guild.name} - Battle Arenas",
                                   color=0x000000)

    for key, value in arenas.items():
        cur_guild_id = key - value.user_id
        if cur_guild_id == ctx.guild_id:
            arena_str = f"- Owner: {ctx.author.mention}\n- ID: {value.id}"

            if value.password is not None:
                arena_str += f" / Password: {value.password}"

            response_embed.add_field(name=value.name, value=arena_str, inline=False)

    if len(response_embed.fields) == 0:
        response_embed.add_field(name="", value="There are no arenas open in this server!")

    await ctx.respond(embed=response_embed)

bot.run(os.getenv('TOKEN'))
