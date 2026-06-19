# -*- coding: utf-8 -*-
"""
Модуль інтерфейсу користувача.
"""

import task_manager as tm


class Color:
    """ANSI escape-коди для кольорового виводу в консоль."""
    RESET = "\033[0m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"


PRIORITY_COLORS = {
    "low": Color.GREEN,
    "medium": Color.YELLOW,
    "high": Color.RED,
}


def colorize(text, color):
    """Обгортає текст в ANSI-код кольору."""
    return f"{color}{text}{Color.RESET}"


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


def format_task_line(task):
    """Формує один рядок опису задачі для виведення в списку."""
    priority_color = PRIORITY_COLORS.get(task["priority"], Color.RESET)
    priority_label = tm.PRIORITY_LABELS.get(task["priority"], task["priority"])
    priority_part = colorize(priority_label, priority_color)

    deadline_part = f", дедлайн: {task['deadline']}" if task.get("deadline") else ""
    tags = task.get("tags") or []
    tags_part = f", теги: {', '.join(tags)}" if tags else ""

    done, total = tm.get_subtask_progress(task)
    progress_part = f", підзадачі: {done}/{total}" if total > 0 else ""

    if tm.is_overdue(task):
        overdue_mark = " " + colorize("[!] ПРОСТРОЧЕНО", Color.RED + Color.BOLD)
    else:
        overdue_mark = ""

    return (
        f"#{task['id']} {task['title']} "
        f"(пріоритет: {priority_part}{deadline_part}{tags_part}{progress_part}){overdue_mark}"
    )


def print_task_details(task: dict):
    """Виводить повну інформацію про одну задачу, разом з підзадачами та історією."""
    tags = task.get("tags") or []
    print(f"\nID: {task['id']}")
    print(f"Назва: {task['title']}")
    print(f"Опис: {task['description'] or '(немає)'}")
    print(f"Статус: {tm.STATUS_LABELS.get(task['status'], task['status'])}")
    priority_color = PRIORITY_COLORS.get(task["priority"], Color.RESET)
    print(f"Пріоритет: {colorize(tm.PRIORITY_LABELS.get(task['priority'], task['priority']), priority_color)}")
    print(f"Дедлайн: {task['deadline'] or '(немає)'}")
    print(f"Теги: {', '.join(tags) if tags else '(немає)'}")
    print(f"Створено: {task['created_at']}")
    print_subtasks(task)
    print_task_history(task)


def print_subtasks(task):
    """Виводить чекліст підзадач."""
    subtasks = task.get("subtasks") or []
    print("\nПідзадачі:")
    if not subtasks:
        print("  (немає підзадач)")
        return
    for s in subtasks:
        box = colorize("[x]", Color.GREEN) if s["done"] else "[ ]"
        print(f"  {box} #{s['id']} {s['title']}")


def print_task_history(task):
    """Виводить історію змін задачі."""
    history = task.get("history") or []
    print("\nІсторія змін:")
    if not history:
        print("  (немає записів)")
        return
    for entry in history:
        print(f"  [{entry['timestamp']}] {entry['action']}")


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


def print_statistics(stats):
    """Виводить статистику дошки у зручному форматі."""
    print("\n=== Статистика дошки ===")
    print(f"Усього задач: {stats['total']}")

    if stats["total"] == 0:
        print("Дошка порожня.")
        return

    print("\nЗа статусом:")
    for status in tm.STATUSES:
        count = stats["by_status"][status]
        print(f"  {tm.STATUS_LABELS[status]}: {count}")

    print("\nЗа пріоритетом:")
    for priority in tm.PRIORITIES:
        count = stats["by_priority"][priority]
        print(f"  {tm.PRIORITY_LABELS[priority]}: {count}")

    print(f"\nПрострочених задач: {stats['overdue_count']}")
    print(f"Відсоток виконання (Done): {stats['completion_rate']:.1f}%")


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