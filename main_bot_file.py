import json
import asyncio
import logging
import os
from aiogram.utils.exceptions import BotBlocked
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
from main import check_new_content
from keyboards import kb, kb2, ikb, del_saved_ikb


logging.basicConfig(level=logging.INFO, filename="errors.log", filemode="a", encoding="utf-8")
bot = Bot(token="6297024039:AAGL5sim2qRaQ_6Ds9oGzZgZMXAvKVeNoAU"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
USERS = {}  # словарь для хранения данных пользователей
USER = os.getenv(key="USER")
HELP = """Я - новостной бот игровой индустрии🔥! Я умею выполнять 4 функции:\n\n1.Прислать список <i>всех новостей</i>📄
2.Выслать список <i>последних новостей</i>💬\n3.Включить режим <i>рассылки свежих новостей</i>⏱\n4.Выслать список твоих
<i>сохранённых новостей</i>📚\n\nКаждую новость ты можешь сохранить, чтобы вернуться к ней позже, либо же
скрыть её!"""


async def on_startup(_):
    print("Бот запустился")


@dp.message_handler(commands=["start"])  # ф-ция обработчик на команду /start
async def process_start(message: types.Message):
    USERS[message.from_user.id] = {
        "saved_news": [],  # сохраненные новости пользователя
        "fresh_news": False  # режим отправки свежих новостей
    }
    await message.answer(
        f"Приветствую, {message.from_user.username if message.from_user.username is not None else 'дорогой пользователь'}! Если возникнут вопросы по функционалу, пиши /help \nА так, выбирай интересующую категорию:",
        reply_markup=kb)


@dp.message_handler(commands=["help"])  # ф-ция обработчик на команду /help
async def help_process(message: types.Message):
    await message.answer(HELP)


@dp.message_handler(lambda x: x.text and x.text.lower() in ("все новости", "все", "пришли все"))
async def send_all_news(message: types.Message):
    with open("game_news.json", "r", encoding="utf-8") as nf:
        all_news = json.load(nf)

    for key, value in sorted(all_news.items())[-30:]:
        news_content = f"{hlink(value['description'], value['url'])}\n\n" \
                       f"Дата публикации: {hbold(value['date'])}\n\n" \
                       f"Перейти к обсуждению: '{value['comments']}\n\n"

        await message.answer(news_content, reply_markup=ikb)


@dp.message_handler(lambda y: y.text and y.text.lower() in ("последние новости", "недавние", "последние"))
async def send_10_news(message: types.Message):
    with open("game_news.json", "r", encoding="utf-8") as nf:
        all_news = json.load(nf)

    for key, value in sorted(all_news.items())[-10:]:
        news_content = f"{hlink(value['description'], value['url'])}\n\n" \
                       f"Дата публикации: {hbold(value['date'])}\n\n" \
                       f"Перейти к обсуждению: '{value['comments']}"

        await message.answer(news_content, reply_markup=ikb)


@dp.message_handler(Text(equals="Сохраненные новости"))
async def send_saved_news(message: types.Message):
    saved_news = ""
    if len(USERS[message.from_user.id]["saved_news"]) > 0:
        for index, v in enumerate(USERS[message.from_user.id]["saved_news"], start=1):
            for search in v.split():
                if "http" in search:
                    saved_news += f"Новость {index} - {search[1:-9]}\n\n"
        await message.answer(saved_news, disable_web_page_preview=True)
        await message.answer("Желаете очистить список сохраненных новостей?", reply_markup=del_saved_ikb)
    else:
        await message.reply("У вас нет сохраненных новостей...")


@dp.message_handler(Text(equals="Режим свежих новостей"))
async def send_fresh_news(message: types.Message):
    USERS[message.from_user.id]["fresh_news"] = True
    await message.answer("Включён режим свежих новостей. Как только появятся свежие новости, я пришлю их сюда!", reply_markup=kb2)
    while True:
        if USERS[message.from_user.id]["fresh_news"]:
            fresh_news = check_new_content()
            if len(fresh_news) >= 1:
                for key, value in sorted(fresh_news.items())[-10:]:
                    news_content = f"{hlink(value['description'], value['url'])}\n\n" \
                                   f"Дата публикации: {hbold(value['date'])}\n\n" \
                                   f"Перейти к обсуждению: '{value['comments']}"

                    await message.answer(news_content, reply_markup=ikb, parse_mode='HTML')
            else:
                continue
        else:
            break

        await asyncio.sleep(300)


@dp.message_handler(Text(equals="Отключить рассылку новостей"))
async def cancel_fresh_news(message: types.Message):
    if USERS[message.from_user.id]["fresh_news"]:
        USERS[message.from_user.id]["fresh_news"] = False
        await message.answer("Режим был успешно выключен", reply_markup=kb)
    else:
        await message.answer("Режим не был включен, чтобы его отключать!", reply_markup=kb)


@dp.message_handler()
async def empty_case(message: types.Message):
    if message.from_user.id in USERS:
        await message.reply("Я вас не понимаю. Воспользуйтесь приведённой ниже клавиатурой", reply_markup=kb)
    else:
        await message.reply("Добро пожаловать! Пиши /start для начала работы.")


@dp.callback_query_handler()
async def process_callback(call: types.CallbackQuery):
    if call.data == "save":
        if call.message.text not in USERS[call.from_user.id]["saved_news"]:
            await call.answer("Новость сохранена!")
            await call.message.edit_text(call.message.text)
            USERS[call.from_user.id]["saved_news"].append(call.message.text)
        else:
            await call.message.answer("Новость уже была сохранена!")
    elif call.data == "dislike":
        await call.answer("Новость скрыта")
        await call.message.delete()
    elif call.data == "delete":
        USERS[call.from_user.id]["saved_news"] = []
        await call.message.delete()
        await call.answer("Ваш список был успешно очищен!")
    else:
        await call.message.delete()


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(send_fresh_news(USER))
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except BotBlocked as err:
        logging.error(f"Пользователь заблокировал бота", exc_info=True)
