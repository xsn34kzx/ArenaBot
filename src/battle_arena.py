from discord import Embed, Member, User
import re

class BattleArena:
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

    game_thumbnail_dict: dict[str, str] = {
        "ssbu": r"https://www.smashbros.com/assets_v2/img/howtoplay/top_icon_basic_pc.png"
    }

    id_regex: re.Pattern[str] = re.compile(r"[A-HJ-NP-Y0-9]{5}")

    def __init__(self, author: Member | User, id: str,
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
        # TODO: Make this int | None
        self.message_id = 0
        # TODO: Add field
        # self.data_time_created = ""

    def get_embed(self) -> Embed:
        """
        Creates and returns a Discord embed summarizing the details of the
        battle arena.
        """

        arena_color = (
            BattleArena.type_color_dict[self.type] if self.type is not None
            else 0x000000
        )

        avatar_url = (
            self.author.avatar.url if self.author.avatar is not None 
            else self.author.default_avatar.url
        )

        response_embed = (
            Embed(title=self.name, color=arena_color)
            .set_footer(text=f"Opened by {self.author.name}", icon_url=avatar_url)
            .set_thumbnail(url=BattleArena.game_thumbnail_dict["ssbu"])
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

