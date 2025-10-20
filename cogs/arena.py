from src import BattleArena, ArenaBot
from discord.ext import commands
import discord

class ArenaCog(commands.Cog):
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

    arena = discord.SlashCommandGroup("arena")

    def __init__(self, bot: ArenaBot) -> None:
        self.bot = bot

    @arena.command(
        name="open",
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
        choices=BattleArena.type_color_dict.keys(),
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
        self,
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
    
        if hash_input in self.bot.arenas:
            await ctx.respond("You already have an arena open!", ephemeral=True)
        else:
            if BattleArena.id_regex.match(id) is not None:
                arena_name = (
                    name if name is not None 
                    else f"{ctx.author.name}'s Arena"
                )
    
                new_arena = BattleArena(arena_author, id, password, arena_name,
                                    max_players, "", type, format)
                self.bot.arenas[hash_input] = new_arena
    
                interaction = await ctx.send_response(embed=new_arena.get_embed())
                message = await interaction.original_response()
    
                new_arena.message_id = message.id
            else:
                await ctx.respond("The provided arena ID was invalid!",
                                  ephemeral=True)
    
    @arena.command(
        name="close",
        description="Close a Battle Arena"
    )
    async def close_arena(self, ctx: discord.ApplicationContext):
        hash_input = ctx.author.id + ctx.guild_id
        cur_arena = self.bot.arenas.pop(hash_input, None)
        if cur_arena is not None:
            try:
                last_message = await ctx.channel.fetch_message(cur_arena.message_id)
                await last_message.delete()
            except discord.NotFound:
                # NOTE: Purposefully ignoring if the message was already deleted
                pass
            # TODO: Do something with these exceptions
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
    
            await ctx.respond("Your arena has been closed!", ephemeral=True)
        else:
            await ctx.respond("You don't have an arena to close!", ephemeral=True)
    
    @arena.command(
        name="find",
        description="Find a Battle Arena from a User"
    )
    @discord.option(
        "user",
        discord.SlashCommandOptionType.user
    )
    async def find_arena(self, ctx: discord.ApplicationContext, user: discord.User):
        hash_input = user.id + ctx.guild_id
    
        if hash_input in self.bot.arenas:
            await ctx.respond(embed=self.bot.arenas[hash_input].get_embed(), ephemeral=True)
        else:
            await ctx.respond(f"Couldn't find an arena opened by {user.mention}!",
                              ephemeral=True)
    
    # TODO: Add filter categories
    @arena.command(
        name="list",
        description="List Battle Arenas in the Server"
    )
    async def list_arenas(self, ctx: discord.ApplicationContext):
        response_embed = discord.Embed(title=f"{ctx.guild.name} - Battle Arenas",
                                       color=0x000000)
    
        for key, value in self.bot.arenas.items():
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
    
    @arena.command(
        name="edit",
        description="Edit a Battle Arena"
    )
    @discord.option(
        "id",
        discord.SlashCommandOptionType.string,
        description="The ID of the Battle Arena",
        min_length=5,
        max_length=5,
        required=False
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
        choices=BattleArena.type_color_dict.keys(),
        required=False
    )
    @discord.option(
        "format",
        discord.SlashCommandOptionType.string,
        description="The format of the Battle Arena",
        choices=format_options,
        required=False
    )
    async def edit_arena(
        self,
        ctx: discord.ApplicationContext,
        id: str | None,
        password: int | None,
        name: str | None,
        max_players: int | None,
        type: str | None,
        format: str | None
    ):
        hash_input = ctx.guild_id + ctx.author.id
    
        if hash_input not in self.bot.arenas:
            await ctx.send_response("You don't have an arena to edit!",
                                    ephemeral=True)
        else:
            cur_arena = self.bot.arenas[hash_input]
    
            arena_modified = False
    
            if id is not None and BattleArena.id_regex.match(id):
                if id != cur_arena.id:
                    cur_arena.id = id
                    arena_modified = True
            if password is not None:
                if password != cur_arena.password:
                    cur_arena.password = password
                    arena_modified = True
            if name is not None:
                if name != cur_arena.name:
                    cur_arena.name = name
                    arena_modified = True
            if max_players is not None:
                if max_players != cur_arena.max_players:
                    cur_arena.max_players = max_players
                    arena_modified = True
            if type is not None:
                if type != cur_arena.type:
                    cur_arena.type = type
                    arena_modified = True
            if format is not None:
                if format != cur_arena.format:
                    cur_arena.format = format
                    arena_modified = True
    
            if arena_modified:
                try:
                    message = await ctx.fetch_message(cur_arena.message_id)
                    await message.edit(embed=cur_arena.get_embed())
                except discord.NotFound:
                    message = await ctx.send(embed=cur_arena.get_embed())
                    cur_arena.message_id = message.id
                # TODO: Do something with these exceptions
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
                await ctx.send_response("Your arena was edited successfully!",
                                        ephemeral=True)
            else:
                await ctx.send_response("No changes were made to your arena!",
                                        ephemeral=True)

def setup(bot: ArenaBot):
    bot.add_cog(ArenaCog(bot))
