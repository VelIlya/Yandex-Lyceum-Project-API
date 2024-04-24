from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

TIMER = 0
TEXT = ""


def get_keyboard():
    reply_keyboard = KeyboardButton('/notification')
    my_keboard = ReplyKeyboardMarkup([[reply_keyboard]], resize_keyboard=True,
                                     one_time_keyboard=True)
    return my_keboard


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"👋👋👋Привет {user.mention_html()}! Я бот-помошник для путешествий...\n\n\n❓Чтобы подробнее узнать о моих "
        f"функциях используйте команду /help или нажмите на кнопку «Помошь»❓.",
        reply_markup=get_keyboard())


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'Напомниаю {TEXT}!')


async def notification(update, context):
    await update.message.reply_text("О чем вам напомнить?")
    return 1


async def first_response(update, context):
    context.user_data['time'] = update.message.text
    await update.message.reply_text(
        f'Через сколько секунд вам напомнить "{context.user_data["time"]}"?')
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]
    return 2


async def second_response(update, context):
    global TIMER, TEXT
    time = update.message.text
    logger.info(time)
    TIMER = int(time)
    TEXT = context.user_data['time']
    chat_id = update.effective_message.chat_id
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    text = f'Вернусь через {TIMER} c.!'
    await update.effective_message.reply_text(text)
    return ConversationHandler.END


async def stop(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Напоминание отменено! Всего доброго!' if job_removed else 'У вас нет активных напоминаний'
    context.user_data.clear()
    await update.message.reply_text(text)
    return ConversationHandler.END


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('notification', notification)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("close", close_keyboard))
    application.add_handler(CommandHandler('stop', stop))
    application.run_polling()


if __name__ == '__main__':
    main()
