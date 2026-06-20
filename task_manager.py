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


def _now_str():
    """Повертає поточну дату й час у вигляді рядка для запису в історію."""
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def _log_history(task, action):
    """Додає запис у історію змін задачі."""
    if "history" not in task:
        task["history"] = []
    task["history"].append({"timestamp": _now_str(), "action": action})


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
        deadline: str | None = None,
        tags: str | None = None
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

    parsed_tags = parse_tags(tags) if tags else []

    task = {
        "id": _next_id(tasks),
        "title": title,
        "description": (description or "").strip(),
        "status": "todo",
        "priority": priority,
        "deadline": deadline,
        "created_at": _today_str(),
        "tags": parsed_tags,
        "history": [],
        "subtasks": [],
    }
    _log_history(task, "Задачу створено зі статусом Todo")
    tasks.append(task)
    storage.save_tasks(tasks)
    return task

def parse_tags(raw_tags: str):
    """
    Перетворює рядок тегів через кому ('робота, важливо') у список
    нормалізованих тегів без пробілів і дублікатів.
    """
    if isinstance(raw_tags, list):
        candidates = raw_tags
    else:
        candidates = (raw_tags or "").split(",")

    seen = []
    for tag in candidates:
        tag = tag.strip().lower()
        if tag and tag not in seen:
            seen.append(tag)
    return seen


def filter_by_tag(tasks: list, tag: str):
    """Повертає задачі, що містять вказаний тег."""
    tag = (tag or "").strip().lower()
    if not tag:
        raise TaskError("Тег для фільтра не може бути порожнім.")
    return [t for t in tasks if tag in t.get("tags", [])]


def delete_task(tasks: list, task_id: int) -> dict:
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    tasks.remove(task)
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

    old_status = task["status"]
    if old_status == new_status:
        raise TaskError(f"Задача вже має статус «{STATUS_LABELS[new_status]}».")

    task["status"] = new_status
    _log_history(task, f"Статус змінено: {STATUS_LABELS[old_status]} → {STATUS_LABELS[new_status]}")
    storage.save_tasks(tasks)
    return task


def edit_task(
        tasks: list,
        task_id: int,
        priority: str | None = None,
        deadline: str | None = None,
        tags: str | None = None
) -> dict:
    """
    Редагує пріоритет, дедлайн та/або теги задачі.
    Якщо параметр None - відповідне поле не змінюється.
    Щоб очистити дедлайн, передайте порожній рядок "".
    """
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    changes = []

    if priority is not None:
        if priority not in PRIORITIES:
            raise TaskError(
                f"Невідомий пріоритет «{priority}». Доступні варіанти: {', '.join(PRIORITIES)}."
            )
        if priority != task["priority"]:
            changes.append(f"пріоритет → {PRIORITY_LABELS[priority]}")
        task["priority"] = priority

    if deadline is not None:
        if deadline == "":
            task["deadline"] = None
            changes.append("дедлайн очищено")
        else:
            task["deadline"] = validate_date(deadline.strip())
            changes.append(f"дедлайн → {task['deadline']}")

    if tags is not None:
        task["tags"] = parse_tags(tags)
        changes.append("теги оновлено")

    if changes:
        _log_history(task, "Редагування: " + "; ".join(changes))

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


def search_tasks(tasks: list, query: str) -> list:
    """
    Шукає задачі, у назві або описі яких міститься query (без урахування регістру).
    """
    query = (query or "").strip().lower()
    if not query:
        raise TaskError("Пошуковий запит не може бути порожнім.")

    result = []
    for task in tasks:
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()
        if query in title or query in description:
            result.append(task)
    return result


def get_statistics(tasks: list):
    """
    Рахує статистику дошки: кількість задач у кожному статусі,
    розподіл за пріоритетами, кількість прострочених, % виконання.
    """
    total = len(tasks)

    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}

    for task in tasks:
        by_status[task["status"]] += 1
        by_priority[task["priority"]] += 1

    overdue_count = len(get_overdue_tasks(tasks))
    done_count = by_status["done"]
    completion_rate = (done_count / total * 100) if total > 0 else 0.0

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "overdue_count": overdue_count,
        "completion_rate": completion_rate,
    }


def add_subtask(tasks: list, task_id: int, title: str):
    """Додає підзадачу (чекліст-пункт) до задачі."""
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    title = (title or "").strip()
    if not title:
        raise TaskError("Назва підзадачі не може бути порожньою.")

    if "subtasks" not in task:
        task["subtasks"] = []

    subtask_id = len(task["subtasks"]) + 1
    subtask = {"id": subtask_id, "title": title, "done": False}
    task["subtasks"].append(subtask)
    _log_history(task, f"Додано підзадачу: {title}")
    storage.save_tasks(tasks)
    return subtask


def toggle_subtask(tasks, task_id, subtask_id):
    """Перемикає статус виконання підзадачі (done/не done)."""
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    subtasks = task.get("subtasks", [])
    subtask = next((s for s in subtasks if s["id"] == subtask_id), None)
    if subtask is None:
        raise TaskError(f"Підзадачу з ідентифікатором {subtask_id} не знайдено.")

    subtask["done"] = not subtask["done"]
    state = "виконано" if subtask["done"] else "знято позначку"
    _log_history(task, f"Підзадача «{subtask['title']}»: {state}")
    storage.save_tasks(tasks)
    return subtask


def get_subtask_progress(task: dict) -> tuple[int, int]:
    """Повертає (виконано, всього) для підзадач задачі."""
    subtasks = task.get("subtasks", [])
    if not subtasks:
        return 0, 0
    done = sum(1 for s in subtasks if s["done"])
    return done, len(subtasks)


def get_subtask(tasks, task_id, subtask_id):
    task = find_task(tasks, task_id)
    if task is None:
        raise TaskError(f"Задачу з ідентифікатором {task_id} не знайдено.")

    subtask = next(
        (s for s in task.get("subtasks", []) if s["id"] == subtask_id),
        None
    )

    if subtask is None:
        raise TaskError(f"Підзадачу з ідентифікатором {subtask_id} не знайдено.")

    return subtask


def archive_done_tasks(tasks):
    """
    Переносить усі задачі зі статусом 'done' у окремий список архіву
    та видаляє їх з активної дошки. Повертає список архівованих задач.
    """
    done_tasks = [t for t in tasks if t["status"] == "done"]
    if not done_tasks:
        return []

    archived = storage.load_archive()
    archived.extend(done_tasks)
    storage.save_archive(archived)

    for task in done_tasks:
        tasks.remove(task)
    storage.save_tasks(tasks)

    return done_tasks


def get_archived_tasks():
    """Повертає список архівованих задач."""
    return storage.load_archive()


def is_approaching_deadline(task: dict, days: int = 3) -> bool:
    """Перевіряє, чи дедлайн настає у найближчі `days` днів (і задача не виконана)."""
    deadline_str = task.get("deadline")


    if not deadline_str or task.get("status") == "done":
        return False

    try:
        deadline_date = datetime.strptime(deadline_str, "%d.%m.%Y").date()
        today = datetime.now().date()
        delta = (deadline_date - today).days

        return 0 <= delta <= days
    except ValueError:
        return False