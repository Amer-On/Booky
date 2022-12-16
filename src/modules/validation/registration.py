import re


def is_valid_name(name: str):
	if name.count(" ") == 2 and name.replace(" ", "").isalpha():
		return True
	return False


def is_valid_phone(phone: str):
	pattern = r'^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
	return bool(re.match(pattern, phone))


def is_valid_email(email: str):
	pattern = r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$'
	return bool(re.match(pattern, email))


if __name__ == "__main__":
	print(is_valid_phone("8 (924) 730-51-77"))
	print(is_valid_phone("+7 (924) 730-51-77"))
	print(is_valid_phone("89247305177"))
	print(is_valid_phone("9247305177"))

	print()
	emails = [
		'a@ya.ru',
		"a.eras.@mail.ru",
		'a.eras@mail.rundle',
		'stable-numble@mail.ru',
	]
	for e in emails:
		print(is_valid_email(e))
