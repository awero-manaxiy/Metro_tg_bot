import asyncio
import os
from dotenv import load_dotenv
import logging
from graph import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


START_STATION, END_STATION = map(chr, range(6, 8))

(
    START_LINE_INPUT,
    START_STATION_INPUT,
    END_LINE_INPUT,
    END_STATION_INPUT,
    ROUTE_REVEAL

) = map(chr, range(5))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""

    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [
            InlineKeyboardButton("Построить маршрут", callback_data=str(1)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите действие", reply_markup=reply_markup)

    return START_LINE_INPUT


async def start_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(str(x), callback_data=str(x))]
        for x in list(stations_labels.keys())
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f'Выберите начальную линию метро', reply_markup=reply_markup)

    return START_STATION_INPUT


async def start_station(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    line = query.data

    keyboard = [
        [InlineKeyboardButton(str(x[0]), callback_data=str(x[1]))]
        for x in stations_labels[line].items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f'Выберите начальную станцию метро', reply_markup=reply_markup)

    return END_LINE_INPUT


async def end_line(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    user_data = context.user_data

    user_data[START_STATION] = query.data

    keyboard = [
        [InlineKeyboardButton(str(x), callback_data=str(x))]
        for x in list(stations_labels.keys())
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f'Выберите конечную линию метро', reply_markup=reply_markup)

    return END_STATION_INPUT


async def end_station(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    line = query.data

    keyboard = [
        [InlineKeyboardButton(str(x[0]), callback_data=str(x[1]))]
        for x in stations_labels[line].items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f'Выберите конченую станцию метро', reply_markup=reply_markup)

    return ROUTE_REVEAL


async def route_builder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    user_data = context.user_data

    beginning, end = user_data[START_STATION], query.data

    output = find_shortest_path(MetroGraph, stations_labels, line_labels, beginning, end)

    await query.edit_message_text(text=output)

    return START_LINE_INPUT


def main() -> None:
    """Run the bot."""

    application = Application.builder().token(TOKEN).build()

    route_building = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            START_LINE_INPUT: [CallbackQueryHandler(start_line)],
            START_STATION_INPUT: [CallbackQueryHandler(start_station)],
            END_LINE_INPUT: [CallbackQueryHandler(end_line)],
            END_STATION_INPUT: [CallbackQueryHandler(end_station)],
            ROUTE_REVEAL: [CallbackQueryHandler(route_builder)]
        },

        fallbacks=[(CommandHandler('start', start))]
    )

    application.add_handler(route_building)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.environ['TOKEN']
    MetroGraph, stations_labels, line_labels = init_graph()
    main()
