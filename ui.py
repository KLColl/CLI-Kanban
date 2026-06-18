# -*- coding: utf-8 -*-
"""
Модуль інтерфейсу користувача.
"""

import task_manager as tm


def print_board(tasks: list):
    """Виводить дошку у вигляді трьох колонок одна під одною."""
    for status in tm.STATUSES:
        column_tasks = [t for t in tasks if t["status"] == status]
        print(f"\n=== {tm.STATUS_LABELS[status]} ({len(column_tasks)}) ===")
        if not column_tasks:
            print("  (порожньо)")
            continue
        for task in column_tasks:
            print("  " + format_task_line(task))


def format_task_line(task: dict):
    """Формує один рядок опису задачі для виведення в списку."""
    deadline_part = f", дедлайн: {task['deadline']}" if task.get("deadline") else ""
    priority_label = tm.PRIORITY_LABELS.get(task["priority"], task["priority"])
    return f"#{task['id']} {task['title']} (пріоритет: {priority_label}{deadline_part})"


def print_task_details(task: dict):
    """Виводить повну інформацію про одну задачу."""
    print(f"\nID: {task['id']}")
    print(f"Назва: {task['title']}")
    print(f"Опис: {task['description'] or '(немає)'}")
    print(f"Статус: {tm.STATUS_LABELS.get(task['status'], task['status'])}")
    print(f"Пріоритет: {tm.PRIORITY_LABELS.get(task['priority'], task['priority'])}")
    print(f"Дедлайн: {task['deadline'] or '(немає)'}")
    print(f"Створено: {task['created_at']}")


def print_overdue(tasks: list):
    """Виводить список прострочених задач."""
    overdue = tm.get_overdue_tasks(tasks)
    print(f"\n=== Прострочені задачі ({len(overdue)}) ===")
    if not overdue:
        print("  Прострочених задач немає.")
        return
    for task in overdue:
        print("  " + format_task_line(task))


def print_task_list(tasks: list, title: str):
    """Виводить довільний список задач під заданим заголовком."""
    print(f"\n=== {title} ({len(tasks)}) ===")
    if not tasks:
        print("  Немає задач.")
        return
    for task in tasks:
        print("  " + format_task_line(task))


def ask_status(prompt: str):
    raw = ask(prompt).lower()
    if raw not in tm.STATUSES:
        print(f"[!] Невідомий статус. Доступні варіанти: {', '.join(tm.STATUSES)}.")
        return None
    return raw


def ask(prompt: str):
    return input(prompt).strip()


def ask_int(prompt: str):
    """Запитує ціле число. Повертає None, якщо введено не число."""
    raw = ask(prompt)
    try:
        return int(raw)
    except ValueError:
        print(f"[!] «{raw}» не є цілим числом.")
        return None