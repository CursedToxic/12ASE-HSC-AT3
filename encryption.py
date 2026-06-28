import json
import hashlib
from pathlib import Path
from json import JSONDecodeError

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists() or path.stat().st_size == 0:
        path.write_text('{"users": {}}')

    try:
        with open(path, "r") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            return data
    except JSONDecodeError:
        return {"users": {}}


def save_users(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)