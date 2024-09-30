import sys, os
from pathlib import Path
import argparse
from rididecrypt import *


def print_all_books():
    log_out("book id", "title", "path")
    path_list = [item for item in LIBRARY_PATH.iterdir() if item.is_dir()]
    for path in path_list:
        book_id = path.name
        book = Book(book_id)
        title = book.title
        log_out(f"{book_id}, {title}, {path}")


def process_all_books(dst_dir):
    path_list = [item for item in LIBRARY_PATH.iterdir() if item.is_dir()]
    total = len(path_list)
    for i, path in enumerate(path_list):
        log_out(f"Progress: {i}/{total}")
        book_id = path.name
        book = Book(book_id)
        process(book, dst_dir)


def check_sanity():
    if not LIBRARY_PATH.is_dir():
        log_err('Library not found. Please make sure you have ran the Ridibooks application and downnloaded the books')
        quit()

def main():
    cwd = Path(sys.argv[0]).parent
    dst_dir = cwd / "books"

    parser = argparse.ArgumentParser(description="Remove DRM from downloaded books")
    parser.add_argument("book", help="Book id or full path to the book directory", nargs="?")
    parser.add_argument("-o", "--out", help=f"Output directory for decrypted books. Defaults to {dst_dir.resolve()}", default=dst_dir, metavar="destination")
    parser.add_argument("-l", "--list", action="store_true", help="List title and id of all downloaded books")
    parser.add_argument("-a", "--all", action="store_true", help="Decrypt all books")
    args = parser.parse_args()
    dst_dir = args.out

    check_sanity()

    if args.list:
        print_all_books()
        quit()

    if not args.book and not args.all:
        log_out("Please specify a book or --all")
        parser.print_help()
        quit()
    try:
        os.makedirs(dst_dir)
    except:
        pass

    if args.all:
        process_all_books(dst_dir)
        quit()

    book_id = str(Path(args.book).name)
    book = Book(book_id)
    process(book, dst_dir)


if __name__ == "__main__":
    main()
