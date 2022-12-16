import requests
from config import API_KEY


# api_key = "AIzaSyB_piLDoqb9WZ5lx78fHzX8OimhKgBYDFE"
api_url = "https://www.googleapis.com/books/v1/volumes"


class Book:
    def __init__(self,
                 title: str,
                 authors: str,
                 rating: str,
                 description: str = ""):
        self.title = title
        self.authors = authors
        self.rating = rating
        self.description = description

    def stringify(self):
        s = f"""Book title: {self.title if self.title else 'Неизвестно'}
Book authors: {' '.join(self.authors) if self.authors else 'Неизвестно'}
Book rating: {self.rating if self.rating else "Незивестно"}
        """
        return s

    def __str__(self):
        return self.stringify()

    def __repr__(self):
        return self.__str__()

    def get_attrs_list(self):
        return [
            self.title,
            ", ".join(self.authors),
            self.rating,
            self.description,
                ]


def get_book(title: str, author: str = None):
    req = requests.get(api_url, _form_payload(title, author))
    if req.status_code == 200:

        js = req.json()
        book_found = False
        book = js['items'][0]['volumeInfo']
        try:
            book_title = book['title']
        except KeyError:
            book_title = None

        try:
            authors = book['authors']
        except KeyError:
            authors = None

        try:
            rating = int(book['rating'])
        except KeyError:
            rating = None

        book = Book(book_title, authors, rating)
        return book


def _form_payload(title: str, author: str):
    q = title
    if author:
        q += ":" + author

    payload = {
        'q': q,
        'maxResults': 1,
        'key': API_KEY,
    }
    return payload


if __name__ == "__main__":
    json = get_book('Анна Каренина')
