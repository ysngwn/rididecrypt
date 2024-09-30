from .common import *
from .Store import *
from .utils import *
import re


def query_book(book_id):
    try:
        store_path = STORE_PATH / "BOOK_META" / book_id
        book_data = Store(store_path).data
    except:
        log_err(f"Unable to read metadata from book_id: {book_id}")
    return book_data


def sanitize(text):
    illegal_chars = R'<>:"/\|?*'
    pattern_list = [re.escape(c) for c in illegal_chars]
    pattern = "|".join(pattern_list)
    text = re.sub(pattern, " ", text)
    text = re.sub(R"\s+", " ", text)
    return text


class Book:
    def __init__(self, book_id):
        self.book_id = str(book_id)
        self.book_dir = LIBRARY_PATH / self.book_id
        self.dat_file = find_ext(self.book_dir, ".dat")
        self.properties = query_book(self.book_id)
        self.book_format = self.book_format()
        self.key = self.get_key()
        self.title = self.get_title()
        self.path = self.get_path()

    def book_format(self):
        file_meta = self.properties["file"]

        if file_meta["format"] == "bom" and (file_meta["isComic"] or file_meta["isManga"]):
            return "comic"
        elif file_meta["format"] in ["epub" or "pdf"]:
            return file_meta["format"]

        log_err(f'Unsupported format: {file_meta["format"]}')

    def get_title(self):
        title = self.properties["title"]
        if isinstance(title, dict):
            title = title["main"]
        if not isinstance(title, str):
            title = self.book_id
        return sanitize(title)

    def get_key(self):
        if self.book_format == "comic":
            return self.get_comic_key()

        short_id = DEVICE_ID[:16]

        with open(self.dat_file, "rb") as rf:
            iv = rf.read(16)
            ciphertext = rf.read()

        cipher = AES.new(short_id.encode(), AES.MODE_CBC, bytes(iv))
        plaintext = cipher.decrypt(pad(ciphertext, 16))
        return plaintext[68:84]

    def get_path(self):
        if self.book_format == "comic":
            return find_ext(self.book_dir, ".zip")
        return find_ext(self.book_dir, f".{self.book_format}")

    def get_comic_key(self):
        return DEVICE_ID[2:18].encode()
