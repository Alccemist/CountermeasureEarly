# CountermeasureEarly
Learning how to write a Discord data-handling bot here.
I'm also learning Python with this — most of my experience is in C/C++ and LuaU.
Employing SQLite for data-keeping.

# Objectives:
- Understand basic Discord API syntax
- Learn and create basic commands (initially prefixed, now slash-based)
- Learn and apply Discord "View" UI system
- Create a customizable game-like "shop" and "inventory" with interactive commands such as "use", "give", "sell", etc...
- Create a configurable player-driven economy
	- First model to include customizable* time durations** per "collect", "research" actions
		- These actions are influenced by roles.
		- Collect generates currency to buy items. Certain items are required for "upgrades" to roles (i.e. better collect)
		- Research generates research points to access new items. This means that RP "unlocks" items.
	- *: Considering adding RNG as an option to these to model uncertainty / fluctuations per yield cycle.
	- **: Currently discussing whether to determine these features' parameters through a parent time-based "turn" system.
		- With just collect and research, all this would do is standardize the cycle for each action.
		- If we are to branch out from this into war turns or other time-based activities, there may be more benefit to it.
- Support player data persistence through SQLite databases
	- This means storing all messages, past and present, that include events for the bot to acknowledge.

# Requirements

To install requirements, enter this into a console within the project directory:
"pip install -r requirements.txt"

You will need to create a Discord bot for main.py's "TOKEN". A server ID is needed for "SERVER_ID".

This bot now only uses slash commands and no longer employs prefix commands.

# Documentation
## Creating Reaction Roles
In Discord: "/create_reaction_roles"

This function has a setup service that lets you title and describe your reaction role embed.
It also allows you to color the embed.

To create and assign emojis, we follow the " emoji | role " format, where an emoji is our key for our map, and the role is our value. It is best to do this first in a Discord chat, and then copy it into the modal whenever  we'reready. For example,
let's assign 4 emojis to 4 roles. We'll enter this in the setup's emoji|role section:

❤️‍🔥|role1,
💸|role2,
🪙|role3,
😿|role4

