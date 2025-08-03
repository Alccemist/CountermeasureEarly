import aiosqlite

# This module is where our database is handled. Always a smart move to organize things, especially as we scale.
# Our database for this project is called game.db.

# This function verifies that the reaction roles table exists.
# It receives an aiosqlite connection argument, which is our database.
	# Also, formerly, I had it as: 
		# 		CREATE TABLE IF NOT EXISTS reaction_roles (
		#		message_id	INTEGER PRIMARY KEY,
		#		emoji	TEXT,
		#		role_id		INTEGER  
		# But that only lets us store one emoji|role per message... The message ID is our primary key here.
		# Our new version treats the pair of columns (message_id, emoji) together as the unique identifier for each row.
		# This means no two rows can have the same message ID and the same emoji.
			# And also, SQLite will automatically create a (multi-column) index on (message_id, emoji) for fast lookups.

async def ensure_reaction_roles_table(db:aiosqlite.Connection):
	await db.execute("""
		CREATE TABLE IF NOT EXISTS reaction_roles (
		message_id	INTEGER,
		emoji	TEXT,
		role_id		INTEGER,
		PRIMARY KEY (message_id, emoji)
		);
	""")
	await db.commit()


async def save_mapping(db, message_id: int, emoji:str, role_id: int):
	await db.execute(
		"INSERT OR REPLACE INTO reaction_roles (message_id, emoji, role_id) VALUES (?, ?, ?)",
		(message_id, emoji, role_id)
	)
	await db.commit()


async def load_mapping(db, message_id: int):
	cursor = await db.execute(
		"SELECT emoji, role_id FROM reaction_roles WHERE message_id = ?",
		(message_id,), # SQLite expects ..., for a single-item tuple. Without "," we iterate over an integer. That's evil.
	)
	rows = await cursor.fetchall()
	    # rows is a list of (emoji, role_id) tuples now. Thus, no more of:
			# return {row[0]: row[1] for row in await cursor.fetchall()}
	return {emoji: role_id for emoji, role_id in rows}
	