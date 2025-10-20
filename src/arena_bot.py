from discord import Bot
from .battle_arena import BattleArena

class ArenaBot(Bot):
    arenas: dict[int, BattleArena] = {}

    async def on_ready(self):
        print(f"{self.user} is ready and online!")

