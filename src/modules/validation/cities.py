import pathlib
path = pathlib.Path(__file__).parent.resolve()

with open(f'{path}/cities.txt', 'r') as f:
    cities = f.read().split('\n')


def is_valid_city(city: str):
    return city in cities
