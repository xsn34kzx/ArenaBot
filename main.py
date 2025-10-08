import discord
import os
import re
from dotenv import load_dotenv

load_dotenv()

game_thumbnail_dict: dict[str, str] = {
    "ssbu": r"https://www.smashbros.com/assets_v2/img/howtoplay/top_icon_basic_pc.png"
}

type_color_dict: dict[str, int] = {
    "All Skill Levels":  0xFFBD0E,
    "Veteran Players":   0xCF2845,
    "Glorious Smashers": 0x795BB7,
    "Anything Goes":     0x57AFED,
    "Playground":        0x1DB247,
    "amiibo Battle":     0x1F9796,
    # TODO: Find a picture of the actual color
    "Beginners Only":    0x808000,
    "Elite Only":        0xFFBE0E 
}

arena_id_regex: re.Pattern[str] = re.compile(r"[A-HJ-NP-Y0-9]{5}")

class BattleArena:
    def __init__(self, author: discord.Member | discord.User, id: str,
                 password: int | None, name: str, max_players: int | None,
                 visibility: str | None, type: str | None,
                 format: str | None) -> None:
        # In-game properties
        self.id = id
        self.name = name
        self.password = password
        self.type = type
        self.visibility = visibility
        self.format = format
        self.max_players = max_players

        # Metadata
        self.author = author 
        # TODO: Add field
        # self.data_time_created = ""

    def get_embed(self) -> discord.Embed:
        """
        Creates and returns a Discord embed summarizing the details of the
        battle arena.
        """

        arena_color = (
            type_color_dict[self.type] if self.type is not None
            else 0x000000
        )

        avatar_url = (
            self.author.avatar.url if self.author.avatar is not None 
            else self.author.default_avatar.url
        )

        response_embed = (
            discord.Embed(title=self.name, color=arena_color)
            .set_footer(text=f"Opened by {self.author.name}", icon_url=avatar_url)
            .set_thumbnail(url=game_thumbnail_dict["ssbu"])
        )

        arena_details = f"- **ID**: {self.id}"

        # Adding optional fields
        if self.password is not None:
            arena_details += f"\n- **Password**: {str(self.password)}"
        if self.max_players is not None:
            arena_details += f"\n- **Max Players**: {str(self.max_players)}"
        if self.type is not None:
            arena_details += f"\n- **Type**: {self.type}"
        if self.format is not None:
            arena_details += f"\n- **Format**: {self.format}"

        return response_embed.add_field(name="Details", value=arena_details)

bot = discord.Bot()

arenas: dict[int, BattleArena] = {}

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
    choices=type_color_dict.keys(),
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
    arena_author = ctx.author
    hash_input = arena_author.id + ctx.guild_id

    if hash_input in arenas:
        await ctx.respond("You already have an arena open!", ephemeral=True)
    else:
        if arena_id_regex.match(id) is not None:
            arena_name = (
                name if name is not None 
                else f"{ctx.author.name}'s Arena"
            )

            new_arena = BattleArena(arena_author, id, password, arena_name,
                                max_players, "", type, format)
            arenas[hash_input] = new_arena

            await ctx.respond(embed=new_arena.get_embed())
        else:
            await ctx.respond("The provided arena ID was invalid!",
                              ephemeral=True)

@bot.slash_command(name="close")
async def close_arena(ctx: discord.ApplicationContext):
    hash_input = ctx.author.id + ctx.guild_id
    cur_arena = arenas.pop(hash_input, None)
    if cur_arena is not None:
        await ctx.respond("Your arena has been closed!", ephemeral=True)
    else:
        await ctx.respond("You don't have an arena to close!", ephemeral=True)

@bot.slash_command(
    name="find",
    description="Find a Battle Arena from a User"
)
@discord.option(
    "user",
    discord.SlashCommandOptionType.user
)
async def find_arena(ctx: discord.ApplicationContext, user: discord.User):
    hash_input = user.id + ctx.guild_id

    if hash_input in arenas:
        await ctx.respond(embed=arenas[hash_input].get_embed(), ephemeral=True)
    else:
        await ctx.respond(f"Couldn't find an arena opened by {user.mention}!",
                          ephemeral=True)

# TODO: Add filter categories
@bot.slash_command(name="list")
async def list_arenas(ctx: discord.ApplicationContext):
    response_embed = discord.Embed(title=f"{ctx.guild.name} - Battle Arenas",
                                   color=0x000000)

    for key, value in arenas.items():
        cur_guild_id = key - value.author.id
        if cur_guild_id == ctx.guild_id:
            arena_details = f"- Owner: {value.author.mention}\n- ID: {value.id}"

            if value.password is not None:
                arena_details += f" / Password: {value.password}"

            response_embed.add_field(name=value.name, value=arena_details,
                                     inline=False)

    if len(response_embed.fields) == 0:
        response_embed.add_field(name="", value="There are no arenas open in this server!")

    await ctx.respond(embed=response_embed)

bot.run(os.getenv('TOKEN'))
