import sys, os, keyring, hashlib
from nodejs import node
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Cipher import AES
import json
from pathlib import Path
from .common import *


def get_password(setting_name):
    sys.stderr = open(os.devnull, "w")
    key = keyring.get_password(f"com.ridi.books/{setting_name}", setting_name)
    sys.stderr = sys.__stderr__
    return key


def get_global_key(encoding="utf-16le"):
    setting_name = "global"
    key = get_password(setting_name)
    key = key.encode(encoding).decode('utf8')
    hex_key = tr_key(key)
    byte_key = bytes.fromhex(hex_key)
    byte_key = pad(byte_key, 16)
    return byte_key


def get_key(config_name, uid):
    keystr = f"{config_name}-{uid}"
    keyhash = hashlib.sha1(keystr.encode("utf8")).hexdigest()
    key = keyhash[2:18]
    hexkey = bytearray(key, "utf8").hex()
    return hexkey


# This nodejs code seemingly just base64 decrypts the input and prints the utf8 representation
# However, handling of non-ascii characters could not be consistently replicated in python
def tr_key(k):
    cmd = f"""
    e = Buffer.from('{k}', "base64").toString("utf8")
    process.stdout.write(Buffer.from(e).toString("hex"))
    """
    node_output = node.run(["-e", cmd], capture_output=True)
    hexkey = node_output.stdout.decode("utf8")
    return hexkey


def decrypt(key, file_path):
    # secret_key can be bytes or string
    if isinstance(key, str):
        key = bytes.fromhex(key)
    with open(file_path, "rb") as infile:
        ciphertext = infile.read()
    ciphertext = ciphertext[256:]
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    try:
        plaintext = unpad(plaintext, 16)
    except:
        pass
    plaintext = plaintext.decode("utf8")
    return plaintext


class Store:
    def __init__(self, path):
        self.path = Path(str(path))
        self.config_name = path.name
        if self.config_name == "Settings":
            self.key = get_global_key()
        else:
            self.key = get_key(self.config_name, USER_ID)
        self.data = self.parse()

    def parse(self):
        try:
            jsontext = decrypt(self.key, self.path)
            data = json.loads(jsontext)
        except:
            if self.config_name == "Settings":
                self.key = get_global_key("utf8")
                jsontext = decrypt(self.key, self.path)
                data = json.loads(jsontext)
        return data["data"]


def get_device_id():
    settings_path = RIDI_HOME / "datastores" / "global" / "Settings"
    settings_data = Store(settings_path).data
    return settings_data["device"]["deviceId"]


DEVICE_ID = get_device_id()
