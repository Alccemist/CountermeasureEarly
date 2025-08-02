import discord,os,asyncio,aiosqlite # asyncio, aiosqlite to be used. Check TODO
from discord.ext import commands
from discord import app_commands

# Cogs are a way to organize commands and events in Discord.py.
# They allow us to group related commands and events together, making our code cleaner and more manageable

# TODO: Set up reaction roles database. Current rxn roles system is based on memory.

class ReactionRoles(commands.Cog):
	def __init__(self, Bot: commands.Bot):
		# recall we're defining an __init__ method to initialize the extension of cog, including its parameters.
		self.Bot = Bot 
		self.mapping: dict[int, dict[str, int]] = {} # This will map message IDs to a dictionary of emoji-role pairs.
		self.GUILD_ID = Bot.GUILD_ID


	# [Reaction Events]
		# We are using Commands.Cog.listener in place of @Bot.event.
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent): 
	# A raw reaction is a reaction that is not cached. Useful for persistence.
	# A note on functions within classes: they become instance methods. 
		# Instance methods always take "self" as the first parameter.
		if payload.message_id not in self.mapping:
			return
		roleId = self.mapping[payload.message_id].get(str(payload.emoji)) # Get the role ID from the mapping.
		if not roleId:
			return
		guild = self.Bot.get_guild(payload.guild_id) # Get the guild (server) where the reaction was added.
			# This comes from the bot, not just our cog....
		member = guild.get_member(payload.user_id) # Get the member who added the reaction.
		if member:
			await member.add_roles(guild.get_role(roleId)) # Add the role to the member.

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent):
		# Applies the same logic as above, but for removing rxns instead.
		if payload.message_id not in self.mapping:
			return
		roleId = self.mapping[payload.message_id].get(str(payload.emoji))
		if not roleId:
			return
		guild = self.Bot.get_guild(payload.guild_id)
		member = guild.get_member(payload.user_id)
		if member:
			await member.remove_roles(guild.get_role(roleId))
		
	# [Reaction Roles Command]
	# This uses a modal due to its complexity. For simpler input-based commands, we can do @app_commands.describe().
	@app_commands.command()
	@app_commands.guilds(discord.Object(id=int(os.getenv("SERVER_ID"))))
	async def create_reaction_roles(self, interaction:discord.Interaction):
		modal = ReactionRolesModal()
		modal.cog = self
		await interaction.response.send_modal(modal)
		# Check if the caller is an admin:
		if interaction.guild_id != self.GUILD_ID:
			return await interaction.response.send_message("Wrong server...", ephemeral=True)
		if not interaction.user.guild_permissions.administrator:
			await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
			return
		else:
			
			await interaction.response.send_modal(ReactionRolesModal())


# [Reaction Roles Setup & Modal]
class ReactionRolesModal(discord.ui.Modal, title="Reaction Roles Setup"):
	# Set up inputs for the modal.
	titleInput = discord.ui.TextInput(
		label="Title",
		max_length=100,
		placeholder="Reaction Roles Title",
		required=True
	)
	descInput = discord.ui.TextInput(
		label="Description",
		max_length=2000,
		placeholder="Message description",
		required=True,
		style=discord.TextStyle.paragraph # This allows for multi-line input.
	)
	colInput = discord.ui.TextInput(
		label="Post Color",
		max_length=7,
		placeholder="Hex color code (e.g. #1EEB0C)",
		required=False
	)
	emojiInput = discord.ui.TextInput(
		label="Emoji|Role Mapping",
		max_length=2000,
		placeholder="format: Emoji|Role, e.g. '😼|SampleRole, ❤️|Larper'",
		required=True,
		style=discord.TextStyle.paragraph
	)

	async def on_submit(self,interaction:discord.Interaction): # Note that the lib uses snake_case for methods. First accidentally used camelCase...
		# [Color input service]
		color=discord.Color.default()
		if self.colInput.value: # Executes if we've a proper color input:
			try:
				color=discord.Color.from_str(self.colInput.value)
			except ValueError:
				await interaction.response.send_message("Invalid color code.", ephemeral=True)

		# [Create embed]
		embed = discord.Embed(
			title=self.titleInput.value,
			description=self.descInput.value,
			color=color,
			timestamp=interaction.created_at
		)
		await interaction.response.send_message(embed=embed)

		# [Fetch message object]
		bot_msg = await interaction.original_response()

		# [Emoji-role mapping service]
		# Parse emoji:role pairs
		mapping: dict[str, int] = {}
		# Recall that the colon is used to define type. We're expecting a dictionary with string keys and integer vals.
		for pairs in self.emojiInput.value.split(","):
			emoji, roleName = pairs.split("|")
			role = discord.utils.get(interaction.guild.roles, name=roleName.strip())
			if role:
				mapping[emoji.strip()] = role.id
			else:
				await interaction.response.send_message(f"Role '{roleName.strip()}' not found...", ephemeral=True)
				return

		# [Add rxns]
		for emoji in mapping:
			await bot_msg.add_reaction(emoji)

		# [Store mapping]
		self.cog.mapping[bot_msg.id] = mapping


# finally instantiate and register our cog:
async def setup(Bot: commands.Bot):
    await Bot.add_cog(ReactionRoles(Bot))