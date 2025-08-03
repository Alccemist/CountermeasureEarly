import discord, os
from database import save_mapping, load_mapping
from discord.ext import commands
from discord import app_commands

# Cogs are a way to organize commands and events in Discord.py.
# They allow us to group related commands and events together, making our code cleaner and more manageable

# An important note: an interaction only has "one" response slot. If we call interaction.response two or more times,
	# then it'll raise an error.
	# This means that we need to validate everything, early exit on errors (must RETURN await interaction.response.send...)
	# and then finally, if all is well, await interaction.response.send_ ...!

class ReactionRoles(commands.Cog):
	def __init__(self, bot: commands.Bot):
		# recall we're defining an __init__ method to initialize the extension of cog, including its parameters.
		self.bot = bot 
		# self.mapping: dict[int, dict[str, int]] = {} 
			# ^ This is no longer used, because we've gone from memory-based to persistent mapping. Good!
		self.GUILD_ID = bot.GUILD_ID

		# register the slash command for this guild only:
		self.bot.tree.add_command(
			self.create_reaction_roles,
			guild=discord.Object(id=self.GUILD_ID)
		)

	# [Reaction Events]
		# We are using Commands.Cog.listener in place of @Bot.event.
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent): 
	# A raw reaction is a reaction that is not cached. Useful for persistence.
	# A note on functions within classes: they become instance methods. 
		# Instance methods always take "self" as the first parameter.

 		# We've replaced the old memory-based method with a solution from our database.py module.
		try:
			mapping = await load_mapping(self.bot.db, payload.message_id)
		except Exception as e:
			return print(f"Mapping error: {e}")
		role_id = mapping.get(str(payload.emoji))
		if not role_id:
			return
		guild = self.bot.get_guild(payload.guild_id) # Get the guild (server) where the reaction was added.
			# This comes from the bot, not just our cog....
		member = guild.get_member(payload.user_id) # Get the member who added the reaction.
		if member:
			await member.add_roles(guild.get_role(role_id)) # Add the role to the member.

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent):
		# Applies the same logic as above, but for removing rxns instead.
		mapping = await load_mapping(self.bot.db, payload.message_id)
		role_id = mapping.get(str(payload.emoji))
		if not role_id:
			return
		guild = self.bot.get_guild(payload.guild_id) # Get the guild (server) where the reaction was added.
			# This comes from the bot, not just our cog....
		member = guild.get_member(payload.user_id) # Get the member who added the reaction.
		if member:
			await member.remove_roles(guild.get_role(role_id)) # Add the role to the member.
		
	# [Create Reaction Roles Command]
	# This uses a modal due to its complexity. For simpler input-based commands, we can do @app_commands.describe().
	@app_commands.command(name="create_reaction_roles", description="Create a reaction roles embed.")
	async def create_reaction_roles(self, interaction:discord.Interaction):
		modal = ReactionRolesModal()
		modal.bot = self.bot
		if interaction.guild_id != self.GUILD_ID or not interaction.user.guild_permissions.administrator:
			return await interaction.response.send_message("You do not have permission...", ephemeral=True)
		await interaction.response.send_modal(modal)

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
		# [Color validation service]
		if self.colInput.value:
			try:
				color=discord.Color.from_str(self.colInput.value)
			except ValueError: # interaction.response 1: Error via invalid color
				return await interaction.response.send_message("Invalid color code...", ephemeral=True)
		else:
			color=discord.Color.default()

		# [Emoji-role mapping service] - Now persistent!
		# Parse emoji:role pairs
		mapping: dict[str, int] = {}
		for chunk in self.emojiInput.value.split(","):
			emoji, roleName = chunk.split("|")
			role = discord.utils.get(interaction.guild.roles, name=roleName.strip())
			if not role: # interaction.response 2: Error via missing role
				return await interaction.response.send_message(
					f"Role '{roleName.strip()}' not found...", ephemeral=True
			)
			mapping[emoji.strip()] = role.id

		# If we've made it to here, then there are no errors. Let's build our embed and do our one-and-only send_message.
		embed = discord.Embed(
			title=self.titleInput.value,
			description=self.descInput.value,
			color=color,
			timestamp=interaction.created_at
		)
		
		await interaction.response.send_message(embed=embed)
		# Fetch message object
		bot_msg = await interaction.original_response()

		for emoji in mapping:
			await bot_msg.add_reaction(emoji)
		# [Store mapping] - Now persistent!
		for emoji, role_id in mapping.items():
			try:
				await save_mapping(self.bot.db, bot_msg.id, emoji, role_id)
			except Exception as e:
				return print(f"Save_mapping error: {e}")

# finally instantiate and register our cog:
async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))