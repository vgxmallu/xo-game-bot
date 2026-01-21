import os
import time
import asyncio
from data import *
from pyrogram import Client, filters, enums
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, CallbackQuery, Message
from os import environ, getenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

OWNER_ID = 784589736
# --- Init ---
mongo_client = AsyncIOMotorClient("DB_URL")
db = mongo_client["xoxo_broadcast_db"]
users_collection = db["users"]

app = Client("XOGame",
             api_id=os.environ.get("API_ID"),
             api_hash=os.environ.get("API_HASH"),
             bot_token=os.environ.get("BOT_TOKEN")
             )
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001997285269"))

def mention(name: str, id: int) -> str:
    return "[{}](tg://user?id={})".format(name, id)


CONTACT_KEYS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            emojis.cat + "Telegram",
            url="http://t.me/TicTacToe_Xbot"
        ),
        InlineKeyboardButton(
            emojis.id + " Telegram",
            url="http://t.me/TicTacToe_Xbot"
        )
    ],
    [
        InlineKeyboardButton(
            emojis.mail + " Email",
            json.dumps({
                "type": "C",
                "action": "email"
            })
        )
    ]
])



MP = """
 **LOG PINGGGG ALERT** 

📛**Triggered Command** : /ping
👤**Name** : {}
👾**Username** : @{}
💾**DC** : {}
♐**ID** : `{}`
🤖**BOT** : @tictactoe_xbot
❌⭕❌⭕
"""

StartTime = time.time()
def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time
    
@app.on_message(filters.command("ping"))
async def ping_bot(bot, message):
    start_time = time.time()
    n = await message.reply_chat_action(enums.ChatAction.TYPING)
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    uptime = get_readable_time((time.time() - StartTime))
    await message.reply_text(f"**🏓 Ping:** `{ping_time} ms`\n**🆙 Time:** `{uptime}`")
    await p4.delete()
    await message.delete()
    await bot.send_message(LOG_CHANNEL, MP.format(message.from_user.mention, message.from_user.username, message.from_user.dc_id, message.from_user.id))
    #await asyncio.sleep(3200)
    #await p.delete()




SPO = """
➡️ **☠️LOG TICTAC** ⬅️

📛**Triggered Command** : /start
👤**Name** : {}
👾**Username** : @{}
💾**DC** : {}
♐**ID** : `{}`
🤖**BOT** : @tictactoe_xbot
❌⭕❌⭕❌⭕❌⭕❌⭕❌⭕❌
"""
text="""
Hi **{}** [👋](https://telegra.ph/file/3f8ca31c69dcf369e3ecc.jpg)\n\nTo begin, start a message 
with @tictactoe_xbot in any group chats you want, or click on the **Play** button 
and select a chat you want to play Tic Tac Toe mini game 🕹️.
"""

g_button = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("➕Add to Group!", switch_inline_query=emojis.game)
            
        ],
    ]
) 


# --- Broadcast command ---
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def ggbroadcast(client, message):
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message (text/photo/video/document) with `/broadcast`")
        return

    total = await users_collection.count_documents({})
    sent = 0
    failed = 0
    removed = 0

    status_msg = await message.reply_text(f"📢 Broadcasting to {total} users...")

    async for user in users_collection.find({}):
        user_id = user["_id"]
        try:
            await message.reply_to_message.copy(chat_id=user_id)
            sent += 1
            await asyncio.sleep(0.05)  # prevent flood
        except (UserIsBlocked, PeerIdInvalid, ChatWriteForbidden):
            # Remove dead/blocked users
            await users_collection.delete_one({"_id": user_id})
            removed += 1
            failed += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ Broadcast finished!\n\n"
        f"👥 Total Users Before: {total}\n"
        f"📩 Sent: {sent}\n"
        f"⚠️ Failed: {failed}\n"
        f"🗑️ Removed from DB: {removed}\n"
        f"📊 Active Users Now: {await users_collection.count_documents({})}"
    )


# --- Status command ---
@app.on_message(filters.command("status") & filters.user(OWNER_ID))
async def ggstatus(client, message):
    total = await users_collection.count_documents({})
    await message.reply_text(f"📊 Total registered users: **{total}**")


# --- Save user on /start ---
@app.on_message(filters.command("start") & filters.private)
async def start_game(client, message):
    user = message.from_user
    user_id = user.id
    user_n = user.username
    # Insert if not exists
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"_id": user_id, "name": user.first_name}},
        upsert=True
    )
    #await client.send_message(LOG_CHANNEL, STR.format(message.from_user.mention, message.from_user.username, message.from_user.dc_id, message.from_user.id))
    await client.send_message(LOG_CHANNEL, SPO.format(message.from_user.mention, message.from_user.username, message.from_user.dc_id, message.from_user.id))
    await message.reply_photo(
        photo="https://telegra.ph/file/3f8ca31c69dcf369e3ecc.jpg",
        caption=text.format(message.from_user.first_name),
        reply_markup=g_button,
    )
    #await message.reply_audio("AwACAgUAAxkBAANYaLk0cu3EU-vGP2_ZTn2T9-E9ajQAAtcXAAK8T8hVy8L_8RGZVXoeBA")
    #message_effect_id=5104841245755180586,
    # If it's a new user, log them
    if result.upserted_id is not None:
        mention = f"[User_Link](tg://user?id={user_id})"
        first_name = f"{user.first_name}"
        await client.send_message(
            LOG_CHANNEL,
            f"🆕 **New member started the ❌⭕❌⭕ game bot! #xoxo**\n\n👤First name: {first_name}\n⛓️‍💥 User Link: {mention}\n©️ User Name: @{user_n}\n🆔 User ID: `{user_id}`"
        )

#@app.on_message(filters.private & filters.text)
def message_handler(bot: Client, message: Message):
    if message.text == "/start":
        bot.send_message(LOG_CHANNEL, SPO.format(message.from_user.mention, message.from_user.username, message.from_user.dc_id, message.from_user.id))
        bot.send_message(
            message.from_user.id,
            f"Hi **{message.from_user.first_name}** [👋](https://telegra.ph/file/3f8ca31c69dcf369e3ecc.jpg)\n\nTo begin, start a message "
            "with @tictactoe_xbot in any group chats you want, or click on the **Play** button "
            "and select a chat you want to play Tic Tac Toe mini game 🕹️.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    emojis.game + " Play",
                    switch_inline_query=emojis.game
                )]
            ])
        )
    elif message.text == "/contact":
        bot.send_message(
            message.from_user.id,
            "Feel free to share your thoughts on XO bot with me.",
            reply_markup=CONTACT_KEYS
        )
    elif message.text == "/xo":
        bot.send_message(
            message.from_user.id,
            "Play Xo Game.",
            reply_markup=PLAYXO
        )


@app.on_inline_query()
def inline_query_handler(_, query: InlineQuery):
    query.answer(
        results=[InlineQueryResultArticle(
            title="Tic-Tac-Toe",
            input_message_content=InputTextMessageContent(
                f"⚔️ **{query.from_user.first_name} challenged you in** ❌⭕❌⭕!"
            ),
            description="Tap here to challenge with your friends in XOXO game🕹️!",
            thumb_url="https://telegra.ph/file/3f8ca31c69dcf369e3ecc.jpg",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    emojis.swords + " Accept",
                    json.dumps(
                        {"type": "P",
                         "id": query.from_user.id,
                         "name": query.from_user.first_name
                         }
                    )
                )]]
            )
        )],
        cache_time=1
    )


@app.on_callback_query()
def callback_query_handler(bot: Client, query: CallbackQuery):
    data = json.loads(query.data)
    game = get_game(query.inline_message_id, data)
    if data["type"] == "P":  # Player
        if game.player1["id"] == query.from_user.id:
            bot.answer_callback_query(
                query.id,
                "Wait for opponent!",
                show_alert=True
            )
        elif game.player1["id"] != query.from_user.id:
            game.player2 = {"type": "P",
                            "id": query.from_user.id,
                            "name": query.from_user.first_name
                            }

            message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
                mention(game.player1["name"], game.player1["id"]),
                emojis.X,
                emojis.vs,
                mention(game.player2["name"], game.player2["id"]),
                emojis.O,
                emojis.game,
                mention(game.player1["name"], game.player1["id"]),
                emojis.X
            )

            bot.edit_inline_text(
                query.inline_message_id,
                message_text,
                reply_markup=InlineKeyboardMarkup(game.board_keys)
            )
    elif data["type"] == "K":  # Keyboard
        if data["end"]:
            bot.answer_callback_query(
                query.id,
                "Match has ended!",
                show_alert=True
            )

            return

        if (game.whose_turn and query.from_user.id != game.player1["id"]) \
                or (not game.whose_turn and query.from_user.id != game.player2["id"]):
            bot.answer_callback_query(
                query.id,
                "Not your turn!"
            )

            return

        if game.fill_board(query.from_user.id, data["coord"]):
            game.whose_turn = not game.whose_turn

            if game.check_winner():
                message_text = "{}({})  {}  {}({})\n\n{} **{} won!**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    emojis.X,
                    emojis.vs,
                    mention(game.player2["name"], game.player2["id"]),
                    emojis.O,
                    emojis.trophy,
                    mention(game.winner["name"], game.winner["id"])
                )
            elif game.is_draw():
                message_text = "{}({})  {}  {}({})\n\n{} **Draw!**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    emojis.X,
                    emojis.vs,
                    mention(game.player2["name"], game.player2["id"]),
                    emojis.O,
                    emojis.draw
                )
            else:
                message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    emojis.X,
                    emojis.vs,
                    mention(game.player2["name"], game.player2["id"]),
                    emojis.O,
                    emojis.game,
                    mention(game.player1["name"], game.player1["id"]) if game.whose_turn else
                    mention(game.player2["name"], game.player2["id"]),
                    emojis.X if game.whose_turn else emojis.O
                )

            bot.edit_inline_text(
                query.inline_message_id,
                message_text,
                reply_markup=InlineKeyboardMarkup(game.board_keys)
            )
        else:
            bot.answer_callback_query(
                query.id,
                "This one is already taken!"
            )
    elif data["type"] == "R":  # Reset
        game = reset_game(game)

        message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
            mention(game.player1["name"], game.player1["id"]),
            emojis.X,
            emojis.vs,
            mention(game.player2["name"], game.player2["id"]),
            emojis.O,
            emojis.game,
            mention(game.player1["name"], game.player1["id"]),
            emojis.X
        )

        bot.edit_inline_text(
            query.inline_message_id,
            message_text,
            reply_markup=InlineKeyboardMarkup(game.board_keys)
        )
    elif data["type"] == "C":  # Contact
        if data["action"] == "email":
            bot.edit_message_text(
                query.from_user.id,
                query.message.message_id,
                "reza.farja78@gmail.com",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        emojis.back + " Back",
                        json.dumps(
                            {"type": "C",
                             "action": "email-back"
                             }
                        )
                    )]]
                )
            )
        elif data["action"] == "email-back":
            bot.edit_message_text(
                query.from_user.id,
                query.message.message_id,
                "Feel free to share your thoughts on XO bot with me.",
                reply_markup=CONTACT_KEYS
            )


app.run()
