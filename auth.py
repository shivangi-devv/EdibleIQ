
import json
import os
import hashlib
import secrets
import uuid

USER_FILE = "users.json"


def load_users():
    if not os.path.exists(USER_FILE):
        return []

    with open(USER_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        600000
    )

    return salt, hashed.hex()


def register_user(username, email, password):
    users = load_users()

    for user in users:
        if user["username"].lower() == username.lower():
            return False, "Username already exists."

        if user["email"].lower() == email.lower():
            return False, "Email already registered."

    salt, password_hash = hash_password(password)

    new_user = {
        "user_id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "salt": salt,
        "password_hash": password_hash
    }

    users.append(new_user)
    save_users(users)

    return True, "Account created successfully!"


def authenticate_user(username, password):
    users = load_users()

    for user in users:
        if user["username"].lower() == username.lower():

            _, entered_hash = hash_password(
                password,
                user["salt"]
            )

            if secrets.compare_digest(
                entered_hash,
                user["password_hash"]
            ):
                return user

    return None
