import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# Load environment vars from .env file. Remember to never commit your .env file to version control.
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up logging. A handler is a component that sends log messages to a specific destination.
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w') # mode is w - write mode

# Manually enable the intents that we need. Consult discordpy docu for more details.
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable members intent


# --- [BOT SERVICE] --------------------------------------------------------------------------
bot = commands.Bot(command_prefix='!', intents = intents) # Create a bot instance with a convenient command prefix and our intents

@bot.event # Decorator for events. A decorator is a function that modifies another function.
async def on_ready(): # Recall functions in python have indent syntax. Too many hours in C++ lmao
	print(f'Logged in as {bot.user.name} - ID {bot.user.id}') # Making it an f-string allows us to embed variables directly in the string.

bot.run(token, log_handler=handler, log_level=logging.debug)
