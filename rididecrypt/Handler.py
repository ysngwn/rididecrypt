from .common import *
from .Store import *
from .utils import *


def decrypt_book(book, dst_dir):
    unzip_dir = dst_dir / f"{book.title}.d"
    if zipfile.is_zipfile(book.path):
        unzip(book.path, unzip_dir)
        clean_comic(unzip_dir)
        decrypt_files(book.key, unzip_dir)
    else:
        tmp_epub = dst_dir / f'_{book.path.name}'
        cp(book.path, tmp_epub)
        decrypt_file(book.key, tmp_epub)
        unzip(tmp_epub, unzip_dir)
        rm(tmp_epub)
    return unzip_dir


def decrypt_pdf(book, dst_dir):
    dst_path = dst_dir / f"{book.title}.pdf"
    cp(book.path, dst_path)
    decrypt_file(dst_dir)
    return dst_path


def clean_epub(epub_dir):
    clean_xmls(epub_dir)


def clean_comic(comic_dir):
    rm(comic_dir / "zzzzzzzzzz")


def make_epub(book, unzip_dir):
    dst_path = unzip_dir.parent / f"{book.title}.epub"

    mime_path = unzip_dir / "mimetype"
    meta_path = unzip_dir / "META-INF"
    oebps_path = unzip_dir / "OEBPS"

    rm(dst_path)

    with zipfile.ZipFile(dst_path, "a") as zipf:
        zipf.write(mime_path, "mimetype")
        zip_add(zipf, unzip_dir, meta_path)
        zip_add(zipf, unzip_dir, oebps_path)
    rm(unzip_dir)
    return dst_path


def make_comic(book, unzip_dir):
    title = book.title
    volume = str(book.properties["series"]["volume"])
    if volume not in title:
        title = f"{title} - v{volume}"
    dst_path = unzip_dir.parent / f"{title}.zip"

    rm(dst_path)

    with zipfile.ZipFile(dst_path, "a") as zipf:
        zip_add(zipf, unzip_dir, unzip_dir)
    rm(unzip_dir)
    return dst_path


def process_epub(book, dst_dir):
    unzip_dir = decrypt_book(book, dst_dir)
    clean_epub(dst_dir)
    return make_epub(book, unzip_dir)


def process_comic(book, dst_dir):
    unzip_dir = decrypt_book(book, dst_dir)
    clean_comic(dst_dir)
    return make_comic(book, unzip_dir)


def process_pdf(book, dst_dir):
    return decrypt_pdf(book, dst_dir)


fns = {
    "epub": process_epub,
    "comic": process_comic,
    "pdf": process_pdf,
}


def process(book, dst_dir):
    log_out(f"Decrypting: {book.title}")
    decrypt = fns[book.book_format]
    dst = decrypt(book, dst_dir)
    log_out(f"Decrypted file: {dst.resolve()}")
