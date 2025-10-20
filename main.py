from dotenv import load_dotenv
from src import ArenaBot
import os

load_dotenv()

bot = ArenaBot()
bot.load_extension("cogs.arena")

bot.run(os.getenv('TOKEN'))
