import motor.motor_asyncio
from info import (
    DATABASE_NAME,
    DATABASE_URL,
    IMDB_TEMPLATE,
    WELCOME_TEXT,
    AUTH_CHANNEL,
    LINK_MODE,
    TUTORIAL,
    SHORTLINK_URL,
    SHORTLINK_API,
    SHORTLINK,
    FILE_CAPTION,
    IMDB,
    WELCOME,
    SPELL_CHECK,
    PROTECT_CONTENT,
    AUTO_FILTER,
    AUTO_DELETE
)

class Database:
    # Default settings for users and groups
    default_setgs = {
        'auto_filter': AUTO_FILTER,
        'file_secure': PROTECT_CONTENT,
        'imdb': IMDB,
        'spell_check': SPELL_CHECK,
        'auto_delete': AUTO_DELETE,
        'welcome': WELCOME,
        'welcome_text': WELCOME_TEXT,
        'template': IMDB_TEMPLATE,
        'caption': FILE_CAPTION,
        'url': SHORTLINK_URL,
        'api': SHORTLINK_API,
        'shortlink': SHORTLINK,
        'tutorial': TUTORIAL,
        'links': LINK_MODE,
        'fsub': AUTH_CHANNEL
    }
    
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
        self.db = self._client[DATABASE_NAME]
        self.col = self.db.Users
        self.grp = self.db.Groups

    def new_user(self, id, name):
        """Create a new user document."""
        return {
            'id': id,
            'name': name,
            'ban_status': {
                'is_banned': False,
                'ban_reason': ""
            }
        }

    def new_group(self, id, title):
        """Create a new group document."""
        return {
            'id': id,
            'title': title,
            'chat_status': {
                'is_disabled': False,
                'reason': ""
            },
            'settings': self.default_setgs
        }
    
    async def add_user(self, id, name):
        """Add a new user to the database."""
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        """Check if a user exists in the database."""
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        """Get the total count of users."""
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        """Remove ban status for a user."""
        await self.col.update_one({'id': id}, {'$set': {'ban_status': {'is_banned': False, 'ban_reason': ''}}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        """Ban a user with an optional reason."""
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': {'is_banned': True, 'ban_reason': ban_reason}}})

    async def get_ban_status(self, id):
        """Get the ban status of a user."""
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return {'is_banned': False, 'ban_reason': ''}
        return user.get('ban_status', {'is_banned': False, 'ban_reason': ''})

    async def get_all_users(self):
        """Retrieve all users."""
        return self.col.find({})
    
    async def delete_user(self, user_id):
        """Delete a user from the database."""
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, grp_id):
        """Delete a chat from the database."""
        await self.grp.delete_many({'id': int(grp_id)})

    async def get_banned(self):
        """Get lists of banned users and disabled chats."""
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        """Add a new chat to the database."""
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat):
        """Retrieve chat status by chat ID."""
        chat = await self.grp.find_one({'id': int(chat)})
        return False if not chat else chat.get('chat_status')
    
    async def re_enable_chat(self, id):
        """Re-enable a disabled chat."""
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': {'is_disabled': False, 'reason': ""}}})
        
    async def update_settings(self, id, settings):
        """Update chat settings."""
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    async def get_settings(self, id):
        """Get chat settings."""
        chat = await self.grp.find_one({'id': int(id)})
        if chat:
            return chat.get('settings')
        return self.default_setgs
    
    async def disable_chat(self, chat, reason="No Reason"):
        """Disable a chat."""
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': {'is_disabled': True, 'reason': reason}}})
    
    async def total_chat_count(self):
        """Get the total count of chats."""
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        """Retrieve all chats."""
        return self.grp.find({})

    async def get_db_size(self):
        """Get the database size."""
        return (await self.db.command("dbstats"))['dataSize']
        
# Instance of the Database class
db = Database()
