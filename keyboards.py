from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add("Все новости", "Последние новости").add("Режим свежих новостей", "Сохраненные новости")
kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
kb2.add("Все новости", "Последние новости").add("Отключить рассылку новостей", "Сохраненные новости")
ikb = InlineKeyboardMarkup(row_width=2)
ikb2 = InlineKeyboardButton("Не интересно", callback_data="dislike")
ikb3 = InlineKeyboardButton("Сохранить новость", callback_data="save")
ikb.add(ikb3, ikb2)
del_saved_ikb = InlineKeyboardMarkup(row_width=1)
button = InlineKeyboardButton("Да", callback_data="delete")
button2 = InlineKeyboardButton("Нет", callback_data="no")
del_saved_ikb.add(button, button2)
