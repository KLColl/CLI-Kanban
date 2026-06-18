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


def _next_id(tasks: list) -> int:
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def _today_str() -> str:
    return datetime.now().strftime(DATE_FORMAT)


def validate_date(date_str: str) -> str:
    """Перевіряє формат ДД.ММ.РРРР, кидає TaskError якщо невалідно."""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return date_str
    except ValueError:
        raise TaskError(
            f"Некоректна дата «{date_str}». Очікується формат ДД.ММ.РРРР, наприклад 25.12.2026."
        )


def add_task(
        tasks: list,
        title: str,
        description: str = "",
        priority: str = "medium",
        deadline: str | None = None
) -> dict:
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


def delete_task(tasks: list, task_id: int) -> dict:
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    tasks.remove(task_id)
    storage.save_tasks(tasks)
    return task


def move_task(tasks: list, task_id: int, new_status: str) -> dict:
    """Переміщує задачу у вказаний статус."""
    if new_status not in STATUSES:
        raise TaskError(
            f"Невідомий статус «{new_status}». Доступні варіанти: {', '.join(STATUSES)}."
        )

    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    task["status"] = new_status
    storage.save_tasks(tasks)
    return task


def edit_task(
        tasks: list,
        task_id: int,
        priority: str | None = None,
        deadline: str | None = None
) -> dict:
    """
    Редагує пріоритет та/або дедлайн задачі.
    Якщо параметр None - відповідне поле не змінюється.
    Щоб очистити дедлайн, передайте порожній рядок "".
    """
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    if priority is not None:
        if priority not in PRIORITIES:
            raise TaskError(
                f"Невідомий пріоритет «{priority}». Доступні варіанти: {', '.join(PRIORITIES)}."
            )
        task["priority"] = priority

    if deadline is not None:
        if deadline == "":
            task["deadline"] = None
        else:
            task["deadline"] = validate_date(deadline.strip())

    storage.save_tasks(tasks)
    return task


def is_overdue(task: dict) -> bool:
    """Перевіряє, чи задача прострочена: дедлайн минув, статус не 'done'."""
    if not task.get("deadline") or task["status"] == "done":
        return False
    try:
        deadline_date = datetime.strptime(task["deadline"], DATE_FORMAT)
    except ValueError:
        return False
    return deadline_date.date() < datetime.now().date()


def get_overdue_tasks(tasks: list) -> list:
    """Повертає прострочені задачі, відсортовані за дедлайном (від найдавнішого)."""
    overdue = [t for t in tasks if is_overdue(t)]
    overdue.sort(key=lambda t: datetime.strptime(t["deadline"], DATE_FORMAT))
    return overdue


def filter_by_priority(tasks: list, priority: str) -> list:
    """Повертає задачі з вказаним пріоритетом."""
    if priority not in PRIORITIES:
        raise TaskError(
            f"Невідомий пріоритет «{priority}». Доступні варіанти: {', '.join(PRIORITIES)}."
        )
    return [t for t in tasks if t["priority"] == priority]


def sort_by_deadline(tasks: list) -> list:
    """Сортує задачі за дедлайном; задачі без дедлайну йдуть в кінець."""
    with_deadline = [t for t in tasks if t.get("deadline")]
    without_deadline = [t for t in tasks if not t.get("deadline")]
    with_deadline.sort(key=lambda t: datetime.strptime(t["deadline"], DATE_FORMAT))
    return with_deadline + without_deadline


def find_task(tasks: list, task_id: int) -> dict | None:
    """Знаходить задачу за id. Повертає None, якщо не знайдено."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None