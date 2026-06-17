# -*- coding: utf-8 -*-
"""
Модуль інтерфейсу користувача.
"""

import task_manager as tm


def print_board(tasks):
    """Виводить дошку у вигляді трьох колонок одна під одною."""
    for status in tm.STATUSES:
        column_tasks = [t for t in tasks if t["status"] == status]
        print(f"\n=== {tm.STATUS_LABELS[status]} ({len(column_tasks)}) ===")
        if not column_tasks:
            print("  (порожньо)")
            continue
        for task in column_tasks:
            print("  " + format_task_line(task))


def format_task_line(task):
    """Формує один рядок опису задачі для виведення в списку."""
    deadline_part = f", дедлайн: {task['deadline']}" if task.get("deadline") else ""
    priority_label = tm.PRIORITY_LABELS.get(task["priority"], task["priority"])
    return f"#{task['id']} {task['title']} (пріоритет: {priority_label}{deadline_part})"


def print_task_details(task):
    """Виводить повну інформацію про одну задачу."""
    print(f"\nID: {task['id']}")
    print(f"Назва: {task['title']}")
    print(f"Опис: {task['description'] or '(немає)'}")
    print(f"Статус: {tm.STATUS_LABELS.get(task['status'], task['status'])}")
    print(f"Пріоритет: {tm.PRIORITY_LABELS.get(task['priority'], task['priority'])}")
    print(f"Дедлайн: {task['deadline'] or '(немає)'}")
    print(f"Створено: {task['created_at']}")

def ask(prompt):
    return input(prompt).strip()


def ask_int(prompt):
    """Запитує ціле число. Повертає None, якщо введено не число."""
    raw = ask(prompt)
    try:
        return int(raw)
    except ValueError:
        print(f"[!] «{raw}» не є цілим числом.")
        return None