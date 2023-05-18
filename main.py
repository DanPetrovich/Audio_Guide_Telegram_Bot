from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import time
from PIL import Image
from pydub import AudioSegment

import telegram
import requests
import io

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
             'https://www.google.com/maps/d/edit?mid=1Ie31z96WMtxh4dVpF3doT38XzinYZlY&ll=55.756890538037254%2C37.64802607601318&z=15')
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
    location_ptr = Locations.loc_map[message.text]
    cur_point = Locations.loc_dict[message.text]
    if location_ptr != 0 and location_ptr != 5:
        direction_markup = types.ReplyKeyboardMarkup()
        direction_markup.add(types.KeyboardButton(text='Мясницкая'))
        direction_markup.add(types.KeyboardButton(text='Басмач'))
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
    if message.text == "Мясницкая":
        direction = Direction.up
    else:
        direction = Direction.up
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
        await message.answer('А все, мы пришли, конец экскурсии, спасибо, что был с нами!',
                             reply_markup=keyboard.new_journey_markup)
    elif direction == Direction.up and cur_point == Locations.Basmach:
        await message.answer('А все, мы пришли, конец экскурсии, спасибо, что был с нами!',
                             reply_markup=keyboard.new_journey_markup)
    else:
        if direction == Direction.up:
            cur_point = Locations.loc_dict[Locations.list_of_locations[Locations.loc_map[cur_point.name] - 1]]
        else:
            cur_point = Locations.loc_dict[Locations.list_of_locations[Locations.loc_map[cur_point.name] + 1]]

        await message.answer('Мы в пути!', reply_markup=keyboard.in_journey_markup)
        # TODO описать маршрут до следующей точки


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
    await message.answer('Супер\n '
                         'Но сначала скажи, как вы хочешь получать информацию? Ушами или глазами?'
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


def convert_audio(file: io.BytesIO):
    audio = AudioSegment.from_file(file, format="m4a")
    # Если необходимо, можно на этом этапе изменить параметры файла, например, битрейт:
    # audio = audio.set_frame_rate(16000).set_channels(1)

    output_file = io.BytesIO()
    audio.export(output_file, format="ogg", codec="libopus")

    # Возвращаемся в начало файла перед его отправкой
    output_file.seek(0)

    return output_file


@dp.message_handler(state=Dialog.start_story)
async def start_story(message: types.Message, state: FSMContext):
    """
    Тут мы непосредсвенно рассказываем, пересылаем сообщения из специального чата
    :param message: Пользователь написал, как хочет получить инфу - устно или текстом
    :param state:
    :return:
    """
    global cur_point
    await message.answer(f"Кайф, начинаю рассказ про корпус {cur_point.name}", reply_markup=types.ReplyKeyboardRemove())
    if message.text == 'Хочу устно':
        for i in range(len(cur_point.oral_messages_to_forward)):
            url = cur_point.oral_messages_to_forward[i][0]

            response = download_file_from_google_drive(parser(url))

            file = io.BytesIO(response.content)

            content_type = cur_point.oral_messages_to_forward[i][1]
            if 'audio' in content_type:
                # Это аудиофайл

                input_file = types.InputFile(convert_audio(file))
                await bot.send_audio(message.chat.id, input_file)
            elif 'photo' in content_type:
                # Это изображение
                file = io.BytesIO(response.content)

                await bot.send_photo(message.chat.id, file)

            # try:
            #     # Преобразование файла в AudioSegment
            #     audio = AudioSegment.from_file(byte_stream, format="m4a")
            # except Exception as e:
            #     print(f"Couldn't decode the file: {e}")
            #     return
            #
            # converted_byte_stream = io.BytesIO()
            # audio.export(converted_byte_stream, format="ogg", codec="opus")
            #
            # converted_byte_stream.seek(0)
            # voice = types.InputFile(byte_stream)
            #
            # await bot.send_voice(message.chat.id, voice)

            time.sleep(2)
    else:
        for i in range(len(cur_point.written_messages_to_forward)):
            url = cur_point.oral_messages_to_forward[i][0]
            response = requests.get(url)
            content_type = cur_point.oral_messages_to_forward[i][1]

            if 'text' in content_type:
                # Это текстовый файл
                input_file = types.InputFile(io.BytesIO(response.content))
                await bot.send_audio(message.chat.id, input_file)
            elif 'photo' in content_type:
                # Это изображение
                input_file = types.InputFile(io.BytesIO(response.content))
                await bot.send_photo(message.chat.id, input_file)

    await state.finish()

    await message.answer('Так, здесь все', reply_markup=keyboard.main_markup)


@dp.message_handler(text='Закончить экскурсию')
async def end_of_journey(message: types.Message):
    await message.answer('Надеюсь, тебе понравилась наша небольшая экскурсия! Тогда до новых встреч',
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
                         'проблем во время экскурсий возникнуть не должно.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
