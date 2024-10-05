from info import DATABASE_URL  # Update this line
from pymongo import MongoClient
from pyrogram import filters, enums
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, UsernameNotOccupied, UsernameInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .helpers.fsub_helpers import is_admin, can_ban_members, can_change_info

# MongoDB connection
try:
    mongo = MongoClient(DATABASE_URL)
    mongodb = mongo.HANSAKA
    db = mongodb.FSUB
except Exception as e:
    print("Error connecting to MongoDB:", e)

def fsub_chats():
    return [x["chat_id"] for x in db.find()]

@Client.on_message(filters.incoming & filters.group)
async def ForceSub(client: Client, message):
    chat_id = message.chat.id
    bot_id = client.me.id
    if chat_id in fsub_chats():
        x = db.find_one({"chat_id": chat_id})
        force_sub_channel = x["channel"]
        user_id = message.from_user.id
        
        if not await is_admin(chat_id, bot_id):
            return await message.reply_text("Make Me Admin Baka!")
        elif not await can_ban_members(chat_id, bot_id):
            return await message.reply_text("Give Me Restrict right to mute who don't sub a channel!")
        
        try:
            await client.get_chat_member(force_sub_channel, user_id)
        except UserNotParticipant:
            link = (await client.get_chat(force_sub_channel)).invite_link
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            return await message.reply_text(
                "I have muted you. Join my force sub channel and click the button below!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel ✅", url=link),
                                                      InlineKeyboardButton("Unmute Me", callback_data=f"fsub_user:{user_id}")]])
            )

@Client.on_callback_query(filters.regex("fsub_user"))
async def unmute_fsubbed(client: Client, query):
    chat_id = query.message.chat.id
    user_id = int(query.data.split(":")[1])
    
    if user_id != query.from_user.id:
        return await query.answer("This button is not for you, Nimba!", show_alert=True)
    
    channel_info = db.find_one({"chat_id": chat_id})
    if channel_info is None:
        return await query.answer("No channel is set for force subscription!", show_alert=True)

    channel = channel_info["channel"]
    
    try:
        await client.get_chat_member(channel, user_id)
    except UserNotParticipant:
        return await query.answer("You must join the force channel to unmute yourself!", show_alert=True)
    
    await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
    await query.message.edit("Thanks for joining my channel. Now you can speak to members!")

@Client.on_message(filters.command("fsub"))
async def ForceSubscribe(client: Client, message):
    chat_id = message.chat.id
    bot_id = client.me.id
    user_id = message.from_user.id
    
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups!") 
    
    if not await is_admin(chat_id, user_id):
        return await message.reply_text("Only group admins can force subscribe a channel!")
    
    if not await can_change_info(chat_id, user_id): 
        return await message.reply_text("You don't have permission to change group info!")

    try:
        command_arg = message.text.split()[1]
    except IndexError:
        return await message.reply_text("Format: /fsub on/off")

    if command_arg == "on":
        ASK = await message.chat.ask(
            text="Okay, send me the Force Subscribe channel username.",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(selective=True)
        )
        
        try:
            force_sub_channel = ASK.text
            await client.get_chat_member(chat_id, force_sub_channel, bot_id)
        except UserNotParticipant:
            return await message.reply_text("Add me there and make sure I'm an admin!")
        except ChatAdminRequired:
            return await message.reply_text(f"I don't have rights to check if the user is a member in the channel. Please make sure I'm an admin in {force_sub_channel}.")
        except UsernameNotOccupied:
            return await message.reply_text("Double-check the channel username!")
        except UsernameInvalid:
            return await message.reply_text("Invalid username: {force_sub_channel}")

        fsub_chat = await client.get_chat(force_sub_channel)
        x = db.find_one({"chat_id": chat_id})

        if x:
            db.update_one({"chat_id": chat_id}, {"$set": {"channel": force_sub_channel}})
        else:
            db.insert_one({"chat_id": chat_id, "fsub": True, "channel": force_sub_channel})          
        
        return await message.reply_text(f"Thanks for using! I have now Force Subscribed this group to {fsub_chat.title}")

    elif command_arg == "off":
        x = db.find_one({"chat_id": chat_id})
        if x:
            db.delete_one(x)
            return await message.reply_text(f"Okay, removed {x['channel']} channel from Force Subscribe!")
        else:
            return await message.reply_text("It seems like this chat doesn't have any Force subscriptions set!")
    
    else:
        return await message.reply_text("Format: /fsub on/off")
