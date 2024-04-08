from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from googletrans import Translator

import math
import datetime
from datetime import timezone, timedelta
import requests

BOT_TOKEN = '7143877690:AAGtv2o-4cewOCZJPQm0y8zNEEeN0RjLW7c'
OpenWeather_TOKEN = '9a5b786988890f430d5325e3d72b7a6c'
Geocoder_TOKEN = 'pk.605ebaf9f9d2ce2e84559af15a384ad1'

code_to_smile = {
    "Clear": "Ясно \U00002600",
    "Clouds": "Облачно \U00002601",
    "Rain": "Дождь \U00002614",
    "Drizzle": "Дождь \U00002614",
    "Thunderstorm": "Гроза \U000026A1",
    "Snow": "Снег \U0001F328",
    "Mist": "Туман \U0001F32B"
}

translator = Translator()
LANGUAGES = {
    'русского': 'ru', 'русский': 'ru',
    'английского': 'en', 'английский': 'en'
}

reply_keyboard_start = [['/help', '/translation']]
markup_start = ReplyKeyboardMarkup(reply_keyboard_start, one_time_keyboard=False)
reply_keyboard_stop = [['/stop']]
markup_stop = ReplyKeyboardMarkup(reply_keyboard_stop, one_time_keyboard=False)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот-помошник для путешествий...",
        reply_markup=markup_start
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать...")


def geocoder(latitude, longitude):
    global Geocoder_TOKEN
    headers = {"Accept-Language": "ru"}
    address = requests.get(
        f'https://eu1.locationiq.com/v1/reverse.php?key={Geocoder_TOKEN}&lat={latitude}&lon={longitude}&format=json',
        headers=headers).json()
    return f'Твое местоположение: {address.get("display_name")}'


async def echo(update, context):
    global translator, LANGUAGES, code_to_smile
    if 'Переведи' in update.message.text:
        try:
            src = LANGUAGES[update.message.text.split()[2]]
            dest = LANGUAGES[update.message.text.split()[4]]
            text = ' '.join(update.message.text.split()[5:])

            await update.message.reply_text(translator.translate(text, src=src, dest=dest).text)
        except Exception as error:
            print(error)
            await update.message.reply_text(
                "Соединение с сервером потеряно. Попробуйте ввести корректные названия языков или подождите немного")

    elif 'Погода в городе' in update.message.text:
        try:
            city = update.message.text.split('Погода в городе ')[-1]

            response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={OpenWeather_TOKEN}")
            data = response.json()
            city = data["name"]
            cur_temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]

            # продолжительность дня
            length_of_the_day = datetime.datetime.fromtimestamp(
                data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(data["sys"]["sunrise"])

            weather_description = data["weather"][0]["main"]

            time_zone = data["timezone"]

            tz = timezone(timedelta(seconds=time_zone))

            if weather_description in code_to_smile:
                wd = code_to_smile[weather_description]
            else:
                # если эмодзи для погоды нет, выводим другое сообщение
                wd = "Посмотри в окно, я не понимаю, что там за погода..."

            await update.message.reply_text(
                f"{datetime.datetime.now(tz).strftime('%d-%m-%Y %H:%M')}\nПогода в городе {city}:\n"
                f"Температура: {cur_temp}°C {wd}\nВлажность: {humidity}%\n"
                f"Давление: {math.ceil(pressure / 1.333)} мм.рт.ст\n"
                f"Ветер: {wind} м/с \n"
                f"Продолжительность дня: {length_of_the_day}")

        except Exception as error:
            print(error)
            await update.message.reply_text(
                "Соединение с сервером потеряно. Попробуйте ввести корректное название города или подождите немного.")


def main():
    # Запуск бота.
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация комманд.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
