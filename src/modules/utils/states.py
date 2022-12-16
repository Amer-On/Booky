from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
	name = State()
	phone = State()
	email = State()
	city = State()


class BookAddition(StatesGroup):
	title = State()
	await_title = State()
	author = State()
	description = State()


class ProfileChanging(StatesGroup):
	name = State()
	phone = State()
	email = State()
	city = State()
