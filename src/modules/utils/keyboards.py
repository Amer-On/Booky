from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

_close_button = InlineKeyboardButton('Убрать клавиатуру', callback_data='remove_keyboard')

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("Выбрать книгу"),
    KeyboardButton("Разместить книгу")
)
menu.add(
    KeyboardButton("Редактировать профиль")
)

accept_terms_of_use = InlineKeyboardMarkup(resize_keyboard=True)
accept_terms_of_use.add(InlineKeyboardButton("Согласен с правилами использования сервиса",
                                             callback_data='accept_terms_of_use'))

profile = InlineKeyboardMarkup()
profile.add(InlineKeyboardButton("Изменить ФИО", callback_data='profile_change_name'))
profile.add(InlineKeyboardButton("Изменить номер телефона", callback_data='profile_change_phone'))
profile.add(InlineKeyboardButton("Изменить электронную почту", callback_data='profile_change_email'))
profile.add(InlineKeyboardButton("Изменить город", callback_data='profile_change_city'))
profile.add(_close_button)

approve_book = InlineKeyboardMarkup()
approve_book.add(
    InlineKeyboardButton("Да, это та книга", callback_data='approve_book'),
    InlineKeyboardButton("Нет, это не та книга", callback_data='disapprove_book'),
)

books_navigation = InlineKeyboardMarkup()
books_navigation.add(
    InlineKeyboardButton("⬅", callback_data='move_left'),
    InlineKeyboardButton("➡", callback_data='move_right'),
)
