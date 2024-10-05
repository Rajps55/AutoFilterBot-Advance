from pyrogram import enums, Client




async def is_owner(client: Client, chat_id: int, user_id: int):
    async for x in client.get_chat_members(chat_id):
        if x.status == enums.ChatMemberStatus.OWNER and x.user.id == user_id:
            return True
    return False

async def is_admin(client: Client, chat_id: int, user_id: int):
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        return admin.privileges is not None
    except Exception:
        return False

async def can_ban_members(client: Client, chat_id: int, user_id: int):
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        return admin.privileges.can_restrict_members if admin.privileges else False
    except Exception:
        return False

async def can_pin_messages(client: Client, chat_id: int, user_id: int):
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        return admin.privileges.can_pin_messages if admin.privileges else False
    except Exception:
        return False

async def can_delete_messages(client: Client, chat_id: int, user_id: int):
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        return admin.privileges.can_delete_messages if admin.privileges else False
    except Exception:
        return False

async def can_promote_members(client: Client, chat_id: int, user_id: int):
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        return admin.privileges.can_promote_members if admin.privileges else False
    except Exception:
        return False

async def can_change_info(client: Client, chat_id: int, user_id: int):
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        return admin.privileges.can_change_info if admin.privileges else False
    except Exception:
        return False
