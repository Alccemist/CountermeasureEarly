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

# [Bot Initialization]
@bot.event
async def on_ready():
	print(f'Bot "{bot.user.name}" RUNNING — ID {bot.user.id}') # Making it an f-string allows us to embed variables directly in the string.

# [Member Join Event]
@bot.event
async def on_member_join(member):
	print(f'{member.name} has joined the server.')

# [Member Remove Event]
@bot.event
async def on_member_remove(member):
	print(f'{member.name} has left the server.')

# [Message Event]
@bot.event
async def on_message(message):
	if message.author == bot.user: # Ignore messages sent by the bot itself
		return
	if "shit" in message.content.lower():
		await message.delete() # await is used to wait for the completion of an asynchronous operation.
		await message.channel.send(f"{message.author.mention}, DON'T SAY THAT!!!! https://tenor.com/view/throat-sore-throat-rip-out-dummy-gif-11843671504878608031")

	await bot.process_commands(message) # allows us to continue processing commands after handling the message event.
	# process_commands is manually called because we are overriding the on_message event.
	# This is critical for bot function. Otherwise, nothing will register after this event...
	



bot.run(token, log_handler=handler, log_level=logging.DEBUG) # We need to use .DEBUG, not .debug... the former is the constant. Latter a func.
