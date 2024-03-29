from telegram.ext import Application, MessageHandler, filters, CommandHandler

# Вместо слова "TOKEN" надо разместить полученный от @BotFather токен.
BOT_TOKEN = 'TOKEN'


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот-помошник для путешествий...",
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать...")


def main():
    # Запуск бота.
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация комманд.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
