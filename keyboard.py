from aiogram import types
from Locations import list_of_locations

locations_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)


for item in list_of_locations:
    locations_markup.add(types.KeyboardButton(text=item, callback_data=item))

main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
commands = ['Пошли дальше', 'Закончить экскурсию', 'О боте']
for item in commands:
    main_markup.add(types.KeyboardButton(text=item, callback_data=item))


new_journey_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
menu = ['Начать новую экскурсию', 'О боте']
for item in menu:
    new_journey_markup.add(types.KeyboardButton(text=item, callback_data=item))

in_journey_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
menu = ['Я дошел до точки', 'Закончить экскурсию']
for item in menu:
    in_journey_markup.add(types.KeyboardButton(text=item, callback_data=item))

story_type_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
menu = ['Давай в голосовом формате', 'Давай в текстовом формате']
for item in menu:
    story_type_markup.add(types.KeyboardButton(text=item, callback_data=item))

is_start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
menu = ['Да, конечно!']
for item in menu:
    is_start_markup.add(types.KeyboardButton(text=item, callback_data=item))

