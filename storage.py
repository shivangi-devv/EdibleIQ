
import json
import os

DATA_FOLDER = "user_data"


def _user_file(user_id, filename):
    if not user_id:
        raise ValueError("A valid user_id is required.")

    user_folder = os.path.join(DATA_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    return os.path.join(user_folder, filename)


def _load_list(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_list(path, items):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(items, file, indent=4)


def load_data(user_id):
    return _load_list(
        _user_file(user_id, "food_data.json")
    )


def save_data(food_items, user_id):
    _save_list(
        _user_file(user_id, "food_data.json"),
        food_items
    )


def load_activity(user_id):
    return _load_list(
        _user_file(user_id, "activity_data.json")
    )


def save_activity(activities, user_id):
    _save_list(
        _user_file(user_id, "activity_data.json"),
        activities
    )
