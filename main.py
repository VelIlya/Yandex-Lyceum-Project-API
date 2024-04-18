from telegram.ext import Application, MessageHandler, filters, CommandHandler
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


async def notification(update, context):
    await update.message.reply_text("Напоминания")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("notification", notification))
    application.run_polling()


if __name__ == '__main__':
    main()
