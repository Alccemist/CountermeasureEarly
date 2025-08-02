import discord,logging,os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv() # We call this to parse a .env file. Without it, we can't access environment variables like our token...

# [CONFIG]--------------------------------------------------------------------------

# Load environment vars from .env file. Remember to never commit the .env file to version control.
CMD_PREFIX:str = "!" # Our command prefix
SERVER_ID = os.getenv('SERVER_ID') # This is the ID of the server where the bot will operate.
	# This will be turned into an object, GUILD_ID, for use in all relevant services.
TOKEN = os.getenv('DISCORD_TOKEN')


assign_role_name = "sampleRole" # DEPRECATED: This is the name of the role that we assign to users when they invoke the command "assignRole".
censored_word = "bad word" # DEPRECATED: This is the word that we will censor in messages. If a user sends a message containing this word, it will be deleted.
# ^ probably should make a list instead. For now, just use a single word.

# [SETUP]--------------------------------------------------------------------------
GUILD_ID = discord.Object(id=int(SERVER_ID)) 
	# ^ We can't just equate it to the server ID. Need to use discord.Object to create an object with the ID.
	# This is because the guild ID is an integer, but discord.py expects an object with an ID attribute.

# logging to hosting device
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w') # mode is w - write mode

# Declare intents. Consult discordpy docu for more details.
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True 
intents.members = True
intents.reactions = True
# ---------------------------------------------------------------------------------

# [BASE UI COMPONENTS]
# [UI COMPONENTS]
# [Button View]
class SampleButtonsView(discord.ui.View): # Python syntax note — parentheses interior is our parent that we inherit.
	@discord.ui.button(label="Button0", style=discord.ButtonStyle.green, emoji="😼", custom_id="button0")
	async def button0_callback(self,interaction,button):
		await interaction.response.send_message("Ephemeral button clicked", ephemeral=True)
		# ephemeral means only the user who clicked the button will see the response.
	# for reference, button options https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.ButtonStyle

	@discord.ui.button(label="DON'T SAY THAT!!!", style=discord.ButtonStyle.red, custom_id="button1")
	async def button1_callback(self,interaction, button):
		await interaction.response.send_message("DONT SAY THAT!!! https://tenor.com/view/throat-sore-throat-rip-out-dummy-gif-11843671504878608031")

# [Dropdown View]
class SampleDropdownOptions(discord.ui.Select): # Using select class to create a dropdown menu.
	def __init__(self):
		options = [
			discord.SelectOption(
				label="Bidge",
				description="ooooh fugg my gbidge",
				emoji="😼", value="opt1"
			),
			discord.SelectOption(
				label="Muroh :sob:",
				description=":sob::sob::sob: Muroh",
				value="opt2"
			),
			discord.SelectOption(
				label="Create Buttons",
				description="Create some buttons with callbacks.",
				value="opt3"
			)
		]
		super().__init__(placeholder="Options", options=options, min_values=1, max_values=1)
		# min and max values limit how few or how many options can be selected.
		# super() calls the parent class constructor. It initializes the Select class with the options we defined.
	# Now, outside init, define the callback func for when the user selects an option.
	async def callback(self, interaction:discord.Interaction):
		if self.values[0] == "opt1": # self.values is a list of the selected values.
			await interaction.response.send_message("ooooooh fugggg my bidge", ephemeral=True)
		elif self.values[0] == "opt2":
			await interaction.response.send_message("uohhhh Muroh :sob::sob::sob:", ephemeral=True)
		elif self.values[0] == "opt3":
			await interaction.response.send_message(
				"Creating buttons:",
				view=SampleButtonsView()
			)

class SampleDropdownView(discord.ui.View):
	def __init__(self):
		super().__init__() # If we don't call this on a view, then add_item won't even exist
		self.add_item(SampleDropdownOptions())

# [HELPER FUNCTIONS]--------------------------------------------------------------------------
async def check_bot_setup_status(bot):
	# This is called whenever we want to check if the bot is set up correctly.
		# Usually called in on_ready events.
	print(f'Bot client "{bot.user.name}" RUNNING — ID {bot.user.id}')
	try: # try-except block to handle errors during command sync.
		synced = await bot.tree.sync(guild=GUILD_ID) # Pass guild by name since sync only expects 1 positional argument.
		print(f"Synced {len(synced)} commands with guild {SERVER_ID}.") # Using server ID here as it's an int already
	except Exception as e:
		print(f"Error syncing commands: {e}")

async def try_loading_cog(bot:commands.Bot, cog_name: str):
	# Use this when attempting to load a cog by name. If all is well, load it. If not, an error. If cog already exists, reload.
	try:
		if cog_name in bot.extensions:
			await bot.load_extension(cog_name) # Check reaction_roles .py for an explanation of cogs
		else:
			await bot.load_extension(cog_name)
	except Exception as e:
		print(f"Error loading {cog_name}: {e}")

# [CLASSES & INSTANTIATION]--------------------------------------------------------------------------
class MyBot(commands.Bot): # We'll create a class for event handling and shared state.
	def __init__(self):
		super().__init__(
			command_prefix=CMD_PREFIX,
			intents=intents,
		)
		# CommandTrees are used to store all of our commands and their info.
		# By default, our commands.Bot will create a tree for us. We reference it with self.tree internally,
			# or by (instance_name).tree externally
		self.GUILD_ID = SERVER_ID

	async def setup_hook(self):
		await try_loading_cog(self, "cogs.reaction_roles")
	
	# Bot Events do not rely on any input. Useful for automatically responding to certain events in the server.
	# [Bot Ready Event]
	async def on_ready(self):
		await check_bot_setup_status(self)

	# [Member Join Event]
	async def on_member_join(member):
		print(f'{member.name} has joined the server.')

	# [Member Remove Event]
	async def on_member_remove(member):
		print(f'{member.name} has left the server.')

	# [Message Event]
	async def on_message(self, message):
		if message.author == self.user: # Ignore messages sent by the MyBot itself
			return
		if censored_word in message.content.lower():
			await message.delete() # await is used to wait for the completion of an asynchronous operation.
			await message.channel.send(f"{message.author.mention} DON'T SAY THAT!!!! https://tenor.com/view/throat-sore-throat-rip-out-dummy-gif-11843671504878608031")

		await self.process_commands(message) # allows us to continue processing commands after handling the message event.
		# process_commands is manually called because we are overriding the on_message event.
		# This is critical for MyBot function. Otherwise, nothing will register after this event...

# Instantiate our MyBot:
bot = MyBot() # Notice that from now on, we're using our bot INSTANCE to define commands.

# [BOT SLASH COMMANDS]--------------------------------------------------------------------------
	# Global updates take up to an hour to propagate, while guild-specific slash commands are immediate.
	# This is why it's imperative to only use our server for testing purposes.

# [MyBot Latency Cmd]
@bot.tree.command(name="check_latency", description="Check the bot client's latency.", guild=GUILD_ID)
async def check_latency(interaction:discord.Interaction):
	await interaction.response.send_message(f"{interaction.user.mention} PING | Bot LATENCY: {round(bot.latency * 1000)}ms")

# [Embedded Message Cmd] - Premade colors: https://discordpy.readthedocs.io/en/latest/api.html?highlight=colour#discord.Colour
@bot.tree.command(name="create_embed", 
					 description="Create an embedded message.",
					 guild=GUILD_ID)					 
async def create_embed(interaction:discord.Interaction):
	embed = discord.Embed(
		title = "Embedded Message",
		description = "This is an example of an embedded message.",
		color = discord.Color.red(),
		timestamp = interaction.created_at,
	)
	embed.add_field(name="Field 1", value="This is a field.", inline=False)
	embed.add_field(name="Field 2", value="This is an inline field.", inline=True)
	embed.add_field(name="Field 3", value="This is another inline field.", inline=True)
	embed.set_footer(text="This is a footer.")
	embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
	embed.set_thumbnail(url=interaction.user.avatar.url)
	# embed.set_image(url=" ... ")  # We can set an image if we want, too.
	await interaction.response.send_message(
		embed = embed
	)

# [Button Command]
@bot.tree.command(name="create_buttons", 
					 description="Create some buttons with callbacks.",
					 guild=GUILD_ID)
async def create_dropdown(interaction:discord.Interaction):
	await interaction.response.send_message(
		"Luh Buttons",
		view = sampleButtonsView()
	)

# [Dropdown Command]
@bot.tree.command(name="create_dropdown", 
					 description="Create some dropdowns with callbacks.",
					 guild=GUILD_ID)
async def create_dropdown(interaction:discord.Interaction):
	view = SampleDropdownView()
	await interaction.response.send_message(
		"Luh Dropdown:",
		view=view
	)

# At the end of our file, we run the bot on our instance.
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG) # We need to use .DEBUG, not .debug... the former is the constant. Latter a func.
