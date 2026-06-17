# -*- coding: utf-8 -*-
"""
Модуль бізнес-логіки.
Відповідає за всі операції з задачами.
"""

from datetime import datetime
from os import remove

import storage

STATUSES = ["todo", "in_progress", "done"]
STATUS_LABELS = {
    "todo": "Todo",
    "in_progress": "In Progress",
    "done": "Done",
}

PRIORITIES = ["low", "medium", "high"]
PRIORITY_LABELS = {
    "low": "Низький",
    "medium": "Середній",
    "high": "Високий",
}

DATE_FORMAT = "%d.%m.%Y"


class TaskError(Exception):
    """Власний виняток для помилок бізнес-логіки."""
    pass


def _next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def _today_str():
    return datetime.now().strftime(DATE_FORMAT)


def validate_date(date_str):
    """Перевіряє формат ДД.ММ.РРРР, кидає TaskError якщо невалідно."""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return date_str
    except ValueError:
        raise TaskError(
            f"Некоректна дата «{date_str}». Очікується формат ДД.ММ.РРРР, наприклад 25.12.2026."
        )


def add_task(tasks, title, description="", priority="medium", deadline=None):
    """Додає нову задачу в колонку 'todo'."""
    title = (title or "").strip()
    if not title:
        raise TaskError("Назва задачі не може бути порожньою.")

    if priority not in PRIORITIES:
        raise TaskError(
            f"Невідомий пріоритет «{priority}». Доступні варіанти: {', '.join(PRIORITIES)}."
        )

    if deadline:
        deadline = validate_date(deadline.strip())
    else:
        deadline = None

    task = {
        "id": _next_id(tasks),
        "title": title,
        "description": (description or "").strip(),
        "status": "todo",
        "priority": priority,
        "deadline": deadline,
        "created_at": _today_str(),
    }
    tasks.append(task)
    storage.save_tasks(tasks)
    return task


def delete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    tasks.remove(task_id)
    storage.save_tasks(tasks)
    return task




def find_task(tasks, task_id):
    """Знаходить задачу за id. Повертає None, якщо не знайдено."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None