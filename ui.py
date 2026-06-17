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


def ask(prompt):
    return input(prompt).strip()