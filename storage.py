# -*- coding: utf-8 -*-
"""
Модуль роботи з даними.
Відповідає лише за читання та запис задач у файл board.json.
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board.json")
ARCHIVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive.json")


def load_tasks():
    """Завантажує список задач з board.json. Якщо файлу немає або він пошкоджений — повертає []."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        print("[!] Увага: файл board.json пошкоджено або недоступний. Починаємо з порожньої дошки.")
        return []


def save_tasks(tasks: list):
    """Зберігає список задач у board.json."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"[!] Не вдалося зберегти дані: {e}")
        return False


def load_archive():
    """Завантажує архівні задачі з archive.json."""
    if not os.path.exists(ARCHIVE_FILE):
        return []
    try:
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        print("[!] Увага: файл archive.json пошкоджено або недоступний.")
        return []


def save_archive(archived_tasks):
    """Зберігає архівні задачі у archive.json."""
    try:
        with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
            json.dump(archived_tasks, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"[!] Не вдалося зберегти архів: {e}")
        return False