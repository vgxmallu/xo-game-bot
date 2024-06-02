import os

from data import *
from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, CallbackQuery, Message


app = Client("XOGame",
             api_id=os.environ.get("API_ID"),
             api_hash=os.environ.get("API_HASH"),
             bot_token=os.environ.get("BOT_TOKEN")
             )

LOG_CHANNEL_ID = int(os.environ.get("-1001997285269"))

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


@app.on_message(filters.private & filters.text)
def message_handler(bot: Client, message: Message):
    if message.text == "/start":
        bot.send_message(LOG_CHANNEL_ID, SPO.format(message.from_user.mention, message.from_user.username, message.from_user.dc_id, message.from_user.id))
        bot.send_message(
            message.from_user.id,
            f"Hi **{message.from_user.first_name}** [👋](https://telegra.ph/file/3f8ca31c69dcf369e3ecc.jpg)\n\nTo begin, start a message "
            "with @tictactoe_xbot in any chat you want or click on the **Play** button "
            "and select a chat to play in groups.",
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


@app.on_inline_query()
def inline_query_handler(_, query: InlineQuery):
    query.answer(
        results=[InlineQueryResultArticle(
            title="Tic-Tac-Toe",
            input_message_content=InputTextMessageContent(
                f"⚔️ **{query.from_user.first_name}** challenged you in XO❌⭕!"
            ),
            description="Tap here to challenge your friends in XO!",
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
