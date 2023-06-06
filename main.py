import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import time
import urllib.parse
import soundfile as sf
import requests
import io
import html

import Locations
import config
import keyboard
from enum import Enum


class Direction(Enum):
    up = 'go up'
    down = 'go down'


logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)

location_ptr = 0
direction = 0  # направление, в котором мы идем. Вверх или вниз

cur_point = Locations.Location()  # Локация, в которой мы находимся в данный момент, экземпляр класса содержит название,


class Dialog(StatesGroup):
    spam = State()
    start_location = State()
    choose_direction = State()
    arrive = State()
    choose_story_type = State()
    start_story = State()


@dp.message_handler(commands=['start'])
async def show_admin_buttons(message: Message):
    """Функция, открывающая бота, выдает информацию о нем,
    показывает пользователю весь маршрут
    """
    await message.answer(
        text='Добро пожаловать в аудиогид по центральным московским корпусам ВШЭ! \n'
             'Отправляйся в увлекательное путешествие в мир истории и архитектуры, окруженный '
             'великолепием знаменитых корпусов. '
             'Доверься моим рассказам и открой для себя удивительные факты о каждом здании. \n'
             'Вперед, наслаждайся путешествием!\n'
             '(ознакомиться с маршрутом можно по ссылке ниже)\n'
             'https://www.google.com/maps/d/viewer?mid=1-Y--S0OsnLMnIXPRV1Caa3ByGpcd9R0&ll=55.75988559898732%2C37.64784719999998&z=15\n'
             'P.S. Мы были бы очень признательны, если бы ты заполнил форму обратной связи, '
             'которая будет доступна после прохождения экскурсии')
    time.sleep(3)
    await message.answer(text='Если ты готов, то выбирай локацию, откуда хочешь начать',
                         reply_markup=keyboard.locations_markup)
    await Dialog.start_location.set()


@dp.message_handler(state=Dialog.start_location)
async def choose_first_point(message: types.Message, state: FSMContext):
    """Здесь описан алгоритм выбора стартовой точки"""
    global location_ptr
    global direction
    global cur_point
    try:
        location_ptr = Locations.loc_map[message.text]
        cur_point = Locations.loc_dict[message.text]
    except:
        await message.answer("Не, надо нажать на кнопку", reply_markup=keyboard.locations_markup)
        await Dialog.start_location.set()
        return
    if location_ptr != 0 and location_ptr != 4:
        direction_markup = types.ReplyKeyboardMarkup()
        direction_markup.add(types.KeyboardButton(text='В сторону Басманной'))
        direction_markup.add(types.KeyboardButton(text='В сторону Мясницкой'))
        await message.answer('Хорошо, в какую сторону пойдем? В сторону Мясницкой или в сторону Басманной?',
                             reply_markup=direction_markup)
        await Dialog.choose_direction.set()

    elif location_ptr == 0:
        direction = Direction.down
        await message.answer('Супер, тогда начинаем?', reply_markup=keyboard.is_start_markup)
        await state.finish()
        await Dialog.choose_story_type.set()

    else:
        direction = Direction.up
        await message.answer('Супер, тогда начинаем?', reply_markup=keyboard.is_start_markup)
        await state.finish()
        await Dialog.choose_story_type.set()


@dp.message_handler(state=Dialog.choose_direction)
async def choose_direction(message: types.Message):
    """
    Выбираем направление и начинаем экскурсию
    :param message: Пользователь вводит направление, в котором хочет идти
    :param state:
    :return: void
    """
    global direction
    if message.text == "В сторону Мясницкой":
        direction = Direction.up
    elif message.text == 'В сторону Басманной':
        direction = Direction.down
    else:
        direction_markup = types.ReplyKeyboardMarkup()
        direction_markup.add(types.KeyboardButton(text='В сторону Басманной'))
        direction_markup.add(types.KeyboardButton(text='В сторону Мясницкой'))
        await message.answer("Не, надо нажать на кнопку", reply_markup=direction_markup)
        await Dialog.choose_direction.set()
        return
    await message.answer('Супер! Тогда давай начинать! Я готов рассказать тебе о первой локации',
                         reply_markup=types.ReplyKeyboardRemove())
    await choose_type(message)


@dp.message_handler(text='Пошли дальше')
async def go_futher(message: types.Message):
    """
    Функция вызывается, когда заканчивается часть экскурсии на одной точке, и надо идти дальше
    :param message:
    :return: void
    """
    global direction
    global cur_point
    if direction == Direction.down and cur_point == Locations.Myasnickaya:
        await message.answer('А все, мы пришли, конец экскурсии, спасибо, что был с нами!\n'
                             'Вот форма обратной связи\n'
                             'https://forms.gle/p8Cy6wU8fvZpMhXs8',
                             reply_markup=keyboard.new_journey_markup)
    elif direction == Direction.up and cur_point == Locations.Basmach:
        await message.answer('А все, мы пришли, конец экскурсии, спасибо, что был с нами!\n'
                             'Вот форма обратной связи\n'
                             'https://forms.gle/p8Cy6wU8fvZpMhXs8',
                             reply_markup=keyboard.new_journey_markup)
    else:
        if direction == Direction.up:

            cur_point = Locations.locations[Locations.loc_map_2[cur_point] - 1]
        else:
            cur_point = Locations.locations[Locations.loc_map_2[cur_point] + 1]
        await message.answer(
            f'Да, конечно, вот ссылка на точку, вы можете простроить маршрут в Яндекс Картах\n {cur_point.url_to_route}'
        )

        await message.answer('Мы в пути!', reply_markup=keyboard.in_journey_markup)


@dp.message_handler(text='Я дошел до точки')
async def have_arrived(message: types.Message):
    """
    Переход от путешествия до начала рассказа
    :param message:
    :return:
    """

    await choose_type(message)


@dp.message_handler(state=Dialog.choose_story_type)
async def choose_type(message: types.Message):
    await message.answer('Отлично\n '
                         'Но сначала скажи, как ты хочешь получать информацию? Ушами или глазами?'
                         '(ну то есть голосовым или текстом?)',
                         reply_markup=keyboard.story_type_markup)

    await Dialog.start_story.set()


def parser(url: str):
    start = url.find('d/')
    end = url.find('/view')
    return url[start + 2:end]


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def download_file_from_google_drive(id: str):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    return response


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def convert_audio(response):
    data, samplerate = sf.read(io.BytesIO(response.content))
    output_file = io.BytesIO()
    sf.write(output_file, data, samplerate, format='WAV')
    output_file.seek(0)
    return output_file


def count_time(part):
    length = len(part.split())
    return length / 2.2


def get_duration(file: io.BytesIO):
    data, samplerate = sf.read(file)
    seconds = len(data) / samplerate
    return seconds


def make_link(picture_tuple: tuple):
    url = html.escape(picture_tuple[3])
    return f'<a href="{url}">{picture_tuple[2]}</a>'


@dp.message_handler(state=Dialog.start_story)
async def start_story(message: types.Message, state: FSMContext):
    """
    Тут мы непосредсвенно рассказываем, пересылаем сообщения из специального чата
    :param message: Пользователь написал, как хочет получить инфу - устно или текстом
    :param state:
    :return:
    """
    global cur_point
    await message.answer(f"Хорошо, тогда начинаю рассказ про корпус на {cur_point.name}",
                         reply_markup=types.ReplyKeyboardRemove())
    if message.text == 'Давай в голосовом формате':
        delay = 0
        for i in range(len(cur_point.oral_messages_to_forward)):

            url = cur_point.oral_messages_to_forward[i][0]

            response = download_file_from_google_drive(parser(url))

            content_type = cur_point.oral_messages_to_forward[i][1]

            if 'audio' in content_type:
                try:

                    await asyncio.sleep(delay)

                    output_file = convert_audio(response)

                    output_file.seek(0)

                    audio_input_file = types.InputFile(output_file)

                    output_file.seek(0)

                    delay = get_duration(output_file)

                    output_file.seek(0)

                    await bot.send_audio(message.chat.id, audio_input_file)
                except:
                    await bot.send_message(message.chat.id,
                                           'Упс, гугл ругается, потому что наш бот только что стал популярнее гугл драйва\n '
                                           'Возможно, придется немного подождать, мы тут не можем ничего сделать(')
                    print(cur_point.oral_messages_to_forward[i])
                    print(cur_point.name)

            elif 'photo' in content_type:

                try:

                    file = io.BytesIO(response.content)

                    if len(cur_point.oral_messages_to_forward[i]) == 4:
                        caption = make_link(cur_point.oral_messages_to_forward[i])
                        print(caption)
                        await bot.send_photo(message.chat.id, file, caption, parse_mode='HTML')
                    else:
                        caption = cur_point.oral_messages_to_forward[i][2]
                        await bot.send_photo(message.chat.id, file, caption)

                    await asyncio.sleep(2)
                except:
                    await bot.send_message(message.chat.id,
                                           'Упс, гугл ругается, потому что наш бот только что стал популярнее гугл драйва\n '
                                           'Возможно, придется немного подождать, мы тут не можем ничего сделать(')
                    print(cur_point.oral_messages_to_forward[i])
                    print(cur_point.name)

    elif message.text == 'Давай в текстовом формате':
        written_messages = cur_point.written_messages_to_forward
        url_text, file_type_text = written_messages[0]

        response = download_file_from_google_drive(parser(url_text))
        text_content = response.content.decode('utf-8')
        text_parts = text_content.split('- - - - -')

        for index in range(1, len(written_messages)):
            if type(written_messages[index]) is tuple:
                url = cur_point.written_messages_to_forward[index][0]

                response = download_file_from_google_drive(parser(url))

                try:
                    file = io.BytesIO(response.content)

                    if len(cur_point.written_messages_to_forward[index]) == 4:
                        caption = make_link(cur_point.written_messages_to_forward[index])
                        await bot.send_photo(message.chat.id, file, caption, parse_mode='HTML')
                    else:
                        caption = cur_point.written_messages_to_forward[index][2]
                        await bot.send_photo(message.chat.id, file, caption)
                    await asyncio.sleep(2)
                except:
                    await bot.send_message(message.chat.id,
                                           'Упс, гугл ругается, потому что наш бот только что стал популярнее гугл драйва\n '
                                           'Возможно, придется немного подождать, мы тут не можем ничего сделать(')
                    print(print(cur_point.written_messages_to_forward[index]))
            else:
                part = text_parts[written_messages[index]]

                if '<html>' in part:
                    await bot.send_message(message.chat.id,
                                           'Упс, гугл ругается, потому что наш бот только что стал популярнее гугл драйва\n '
                                           'Возможно, придется немного подождать, мы тут не можем ничего сделать(')
                    print(cur_point.written_messages_to_forward[index])
                    continue
                await bot.send_message(message.chat.id, part)

                await asyncio.sleep(count_time(part))

    else:
        await message.answer("Не, надо нажать на кнопку", reply_markup=keyboard.story_type_markup)
        await Dialog.start_story.set()

    await state.finish()

    await message.answer('Так, здесь все', reply_markup=keyboard.main_markup)


@dp.message_handler(text='Закончить экскурсию')
async def end_of_journey(message: types.Message):
    await message.answer('Надеюсь, тебе понравилась наша небольшая экскурсия! Тогда до новых встреч\n'
                         'Вот форма обратной связи\n'
                         'https://forms.gle/p8Cy6wU8fvZpMhXs8',
                         reply_markup=keyboard.new_journey_markup)


@dp.message_handler(text='Начать новую экскурсию')
async def new_excursion(message: types.Message):
    await message.answer(text='Я рад, что ты вернулся) Теперь выбери локацию, откуда хочешь начать',
                         reply_markup=keyboard.locations_markup)
    await Dialog.start_location.set()


@dp.message_handler(text='О боте')
async def info(message: types.Message):
    await message.answer('Добро пожаловать! Этот бот - аудиогид по центральным московским корпусам ВШЭ! \n'
                         'Наш бот поможет вам познакомиться с уникальной архитектурой и интересной историей зданий, '
                         'находящихся в центре Москвы. Просто следуйте инструкциям и наслаждайтесь '
                         'увлекательным путешествием!\n'
                         'Несмотря на то, что это аудиогид, вы можете получать информацию и в виде '
                         'текста, а еще будут картинки)\n'
                         'Как пользоваться ботом? Мы его сделали максимально понятным и интуитивным, так что уверены, '
                         'проблем во время экскурсий возникнуть не должно.\n'
                         'Вот авторы проекта:\n'
                         '@Nekto22\n'
                         '@lizakapranova\n'
                         '@eleanorra')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
