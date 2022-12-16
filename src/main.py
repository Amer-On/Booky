import logging
import asyncio
from contextlib import suppress

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from modules.db import users_db, books_db
from modules.utils import states
import modules.utils.keyboards as kb
from modules import validation
from modules.messages import ru
from modules.api.google_books_api import *

from config import TOKEN, ADMINS, MODERATORS

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# logging.basicConfig(filename='logs.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    if not users_db.is_user_in(message.from_user.id):
        await answer_with_several_messages(message, ru.start, remove_markup=True)

        await states.Registration.name.set()
    else:
        await general(message, state)


@dp.message_handler(commands='delete_db')
async def delete_db(message: types.Message):
    if message.from_user.id in ADMINS:
        users_db.clear_users_db()
        await message.answer("SUCCESSFULLY CLEARED USERS DATABASE")
    else:
        await general(message)


@dp.message_handler(commands='city')
async def reg_city(message: types.Message):
    await message.answer(users_db.get_user_city(message.from_user.id))


@dp.message_handler(state=states.Registration.name)
async def reg_name(message: types.Message, state: FSMContext):
    name = message.text.title()
    if validation.registration.is_valid_name(name):
        async with state.proxy() as data:
            data['name'] = name

        await message.answer(ru.reg_name_valid(name))
        await states.Registration.phone.set()
    else:
        await answer_with_several_messages(message, ru.reg_name_invalid)


@dp.message_handler(state=states.Registration.phone)
async def reg_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if validation.registration.is_valid_phone(phone):
        async with state.proxy() as data:
            data['phone'] = phone

        await answer_with_several_messages(message, ru.reg_phone_valid)

        await states.Registration.email.set()
    else:
        await answer_with_several_messages(message, ru.reg_phone_invalid)


@dp.message_handler(state=states.Registration.email)
async def reg_email(message: types.Message, state: FSMContext):
    email = message.text
    if validation.registration.is_valid_email(email):
        async with state.proxy() as data:
            data['email'] = email

        await answer_with_several_messages(message, ru.reg_email_valid)
        await states.Registration.city.set()
    else:
        await answer_with_several_messages(message, ru.reg_email_invalid)


@dp.message_handler(state=states.Registration.city)
async def reg_city(message: types.Message, state: FSMContext):
    city = message.text.title()
    if validation.cities.is_valid_city(city):
        async with state.proxy() as data:
            data['city'] = city

        await message.answer(ru.reg_city_valid[0])
        await message.answer(ru.reg_city_valid[1], reply_markup=kb.accept_terms_of_use)

    else:
        await answer_with_several_messages(message, ru.reg_city_invalid)


@dp.message_handler(state=states.BookAddition.title)
async def book_addition_title(message: types.Message, state: FSMContext):
    title = message.text
    book = get_book(title)
    async with state.proxy() as data:
        data['book'] = book

    await message.answer(book, reply_markup=kb.approve_book)
    await states.BookAddition.await_title.set()


@dp.message_handler(state=states.BookAddition.author)
async def book_addition_author(message: types.Message, state: FSMContext):
    authors = message.text.split(', ')
    async with state.proxy() as data:
        book = data['book']
        book.authors = authors
    await message.answer(ru.book_addition_author)
    await _approve_book(message, state)


async def _approve_book(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        book = data['book']

    if not book.authors:
        await message.answer(ru.book_addition_approve_book_author)
        await states.BookAddition.author.set()

    else:
        await message.answer(ru.book_addition_approve)
        await states.BookAddition.description.set()


@dp.message_handler(state=states.BookAddition.description)
async def book_addition_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        book = data['book']
        book.description = message.text

    await message.answer(ru.book_addition_description)

    user_id = message.from_user.id
    books_db.add_book(*book.get_attrs_list(), users_db.get_user_city(user_id), user_id)

    await message.answer(ru.book_addition_done)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'approve_book', state=states.BookAddition.await_title)
async def approve_book(callback: types.CallbackQuery, state: FSMContext):
    await _approve_book(callback.message, state)
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == 'disapprove_book', state=states.BookAddition.await_title)
async def disapprove_book(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(ru.book_addition_disapprove_book)
    await states.BookAddition.title.set()
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "accept_terms_of_use", state=states.Registration.city, )
async def confirm_terms_of_use(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(ru.registration_finished, reply_markup=kb.menu)
    async with state.proxy() as data:
        users_db.save_user(callback.from_user.id, data['name'], data['phone'], data['city'], data['email'])
        users_db.db_to_csv()
        logging.info(f"USER {callback.from_user.id} is saved to database")
    await state.finish()


async def profile(message: types.Message):
    profile_info = users_db.get_user(message.from_user.id)
    text = str(profile_info) + '\n' + ru.change_profile_data

    await message.answer(text, parse_mode='HTML', reply_markup=kb.profile)


def get_book_from_city(user_id, page):
    books = books_db.get_books_from_city(users_db.get_user_city(user_id))
    bk = books[page]
    book = Book(*bk[:-2])
    book.authors = book.authors.split(", ")
    return book


async def get_books_from_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'page' in data.keys():
            book = get_book_from_city(message.from_user.id, data['page'])
            await send_book_info(message, book)
        else:
            data['page'] = 0
            book = get_book_from_city(message.from_user.id, 0)
            await send_book_info(message, book)


def generate_book_info(book):
    text = f"""Название книги: <em>{book.title}</em>
Авторы книги: <em>{", ".join(book.authors)}</em>
Рейтинг книги: <em>{book.rating if book.rating else "Неизвестно"}</em>

<b><em>Описание книги от владельца:</em></b>
{book.description} 
"""
    return text


async def send_book_info(message: types.Message, book):
    text = generate_book_info(book)
    await message.answer(text, parse_mode='HTML', reply_markup=kb.books_navigation)


@dp.callback_query_handler(text_startswith='move')
async def move_pages(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "move_left":
        async with state.proxy() as data:
            data['page'] -= 1 if data['page'] > 0 else 0
        await update_text(callback.message, generate_book_info(
            get_book_from_city(callback.from_user.id, data['page'])),
                          keyboard=kb.books_navigation)
    else:
        async with state.proxy() as data:
            data['page'] += 1
            try:
                await update_text(callback.message, generate_book_info(
                    get_book_from_city(callback.from_user.id, data['page'])),
                                  keyboard=kb.books_navigation)
            except IndexError:
                data['page'] -= 1


@dp.message_handler(state=states.ProfileChanging.city)
async def change_city(message: types.Message, state: FSMContext):
    city = message.text
    if validation.cities.is_valid_city(city):
        users_db.set_city(message.from_user.id, city)
        await message.answer(ru.change_profile_city_successful)
        await state.finish()
    else:
        await answer_with_several_messages(message, ru.reg_city_invalid)


@dp.callback_query_handler(lambda c: c.data == "profile_change_city")
async def profile_change_city(callback: types.CallbackQuery):
    await callback.message.answer(ru.change_profile_city)
    await states.ProfileChanging.city.set()


@dp.message_handler()
async def general(message: types.Message, state: FSMContext):
    text = message.text
    if text == "Выбрать книгу":
        await message.answer(ru.book_choosing)
        await get_books_from_city(message, state)

    elif text == "Разместить книгу":
        await message.answer(ru.place_book)
        await states.BookAddition.title.set()
    elif text == "Редактировать профиль":
        await profile(message)
    else:
        await message.answer("YO MAN IDK", reply_markup=kb.menu)


async def remove_keyboard(message: types.Message):
    await update_text(message, message.text)


async def update_text(message: types.Message, text, keyboard=None):
    with suppress(MessageNotModified):
        await message.edit_text(text, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


async def answer_with_several_messages(message: types.Message, answer_messages_texts: tuple,
                                       remove_markup: bool = False, delay: int = 0):
    if remove_markup:
        await message.answer(answer_messages_texts[0], reply_markup=None)
        await answer_with_several_messages(message, answer_messages_texts[1:], delay=delay)
        return

    for message_text in answer_messages_texts:
        await message.answer(message_text)
        await asyncio.sleep(delay)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
