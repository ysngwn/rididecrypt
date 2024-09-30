import zipfile
from Cryptodome.Util.Padding import pad
from Cryptodome.Cipher import AES
import shutil
from bs4 import BeautifulSoup
from .common import *


def list_files(path):
    return [item for item in path.rglob("*") if item.is_file()]


def unzip(zip_file, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    with zipfile.ZipFile(zip_file, "r") as zf:
        zf.extractall(dst_dir)


def zip_add(zipf, base_path, src_dir):
    file_paths = list_files(src_dir)
    for src_path in file_paths:
        target = src_path.relative_to(base_path)
        zipf.write(src_path, target)


def cp(src, dst):
    shutil.copy(src, dst)


def rm(path):
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    Path.unlink(path, missing_ok=True)


def find_ext(dir_path, ext):
    dir_content = list_files(dir_path)
    found = [item for item in dir_content if str(item).endswith(ext)]
    if len(found) == 1:
        return found[0]
    if len(found) == 0:
        log_err(f"No file with extension {ext} found in {dir_path}")
    elif len(found) > 1:
        log_err(f"Multiple files with extension {ext} found in {dir_path}")
    log_err(dir_content)


def decrypt_file(key, src_path):
    with open(src_path, "rb") as infile:
        iv = infile.read(16)
        ciphertext = infile.read()

    cipher = AES.new(key, AES.MODE_CBC, bytes(iv))
    plaintext = cipher.decrypt(pad(ciphertext, 16))

    with open(f'{src_path}', "wb") as outfile:
        outfile.write(plaintext)


def decrypt_files(key, src_path):
    file_list = list_files(src_path)
    for src in file_list:
        decrypt_file(key, src)


def clean_xmls(dst_dir):
    files = list_files(dst_dir)
    for f in files:
        ext = str(f).split(".")
        if ext in [".xhtml", ".opf", ".ncx"]:
            clean_xml(f)


def clean_xml(xml_path):
    with open(xml_path, errors="ignore", encoding="utf-8") as rf:
        content = rf.read()
    soup = BeautifulSoup(content, features="xml")
    with open(xml_path, "w", errors="ignore", encoding="utf-8") as wf:
        content = wf.write(soup.prettify())
