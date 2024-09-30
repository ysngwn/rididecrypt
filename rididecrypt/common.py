from pathlib import Path
import os
import traceback

def log_err(s):
    print(s)
    print(traceback.format_exc())

def log_out(s):
    print(s)

def get_user_id():
    users_dir = RIDI_HOME / "datastores" / "user"
    user_list = [item for item in users_dir.iterdir() if item.is_dir()]
    if len(user_list) == 0:
        log_err("No users found. Please ensure that you have logged in to the Ridibooks app")
        quit()
    elif len(user_list) > 1:
        log_err(f"Multiple users found. Please remove all unused directories in {users_dir}")
        quit()
    return user_list[0].name[1:]


RIDI_HOME = Path(os.getenv("APPDATA")) / "Ridibooks"
USER_ID = get_user_id()
STORE_PATH = RIDI_HOME / "datastores" / "user" / f"_{USER_ID}"
LIBRARY_PATH = RIDI_HOME / "library" / f"_{USER_ID}"
