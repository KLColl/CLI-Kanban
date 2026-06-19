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
    LIGHT_GRAY = "\033[97m"
    BRIGHT_GRAY = "\033[37m"
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
        header = colorize(f"{tm.STATUS_LABELS[status]}", Color.BLUE + Color.BOLD)
        count = colorize(f"({len(column_tasks)})", Color.BRIGHT_GRAY)
        print(f"\n=== {header} {count} ===")
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

    task_id = colorize(f"#{task['id']}", Color.BRIGHT_GRAY)
    title = colorize(task["title"], Color.BOLD)

    deadline_part = f", дедлайн: {task['deadline']}" if task.get("deadline") else ""
    tags = task.get("tags") or []
    tags_part = f", теги: {', '.join(tags)}" if tags else ""

    done, total = tm.get_subtask_progress(task)
    progress_part = f", підзадачі: {colorize(f'{done}/{total}', Color.BLUE)}" if total > 0 else ""

    if tm.is_overdue(task):
        overdue_mark = " " + colorize("[!] ПРОСТРОЧЕНО", Color.RED + Color.BOLD)
    else:
        overdue_mark = ""

    return (
        f"{task_id} {title} "
        f"(пріоритет: {priority_part}{deadline_part}{tags_part}{progress_part}){overdue_mark}"
    )


def print_task_details(task: dict):
    """Виводить повну інформацію про одну задачу, разом з підзадачами та історією."""
    tags = task.get("tags") or []
    print(f"\n{colorize('ID:', Color.BOLD)} {task['id']}")
    print(f"{colorize('Назва:', Color.BOLD)} {task['title']}")
    print(f"{colorize('Опис:', Color.BOLD)} {task['description'] or '(немає)'}")
    print(f"{colorize('Статус:', Color.BOLD)} {tm.STATUS_LABELS.get(task['status'], task['status'])}")

    priority_color = PRIORITY_COLORS.get(task["priority"], Color.RESET)
    priority_text = tm.PRIORITY_LABELS.get(task["priority"], task["priority"])
    print(f"{colorize('Пріоритет:', Color.BOLD)} {colorize(priority_text, priority_color)}")

    print(f"{colorize('Дедлайн:', Color.BOLD)} {task['deadline'] or '(немає)'}")
    print(f"{colorize('Теги:', Color.BOLD)} {', '.join(tags) if tags else '(немає)'}")
    print(f"{colorize('Створено:', Color.BOLD)} {task['created_at']}")
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
        icon = colorize("✓", Color.GREEN + Color.BOLD) if s["done"] else colorize("✗", Color.RED + Color.BOLD)
        subtask_id = colorize(f"#{s['id']}", Color.BRIGHT_GRAY)
        print(f"  {icon} {subtask_id} {s['title']}")


def print_task_history(task):
    """Виводить історію змін задачі."""
    history = task.get("history") or []
    print("\nІсторія змін:")
    if not history:
        print("  (немає записів)")
        return
    for entry in history:
        ts = colorize(entry["timestamp"], Color.BRIGHT_GRAY)
        action = colorize(entry["action"], Color.BLUE)
        print(f"  [{ts}] {action}")


def print_overdue(tasks: list):
    """Виводить список прострочених задач."""
    overdue = tm.get_overdue_tasks(tasks)
    title = colorize(f"=== Прострочені задачі ({len(overdue)}) ===", Color.RED + Color.BOLD)
    print(f"\n{title}")
    if not overdue:
        print("  Прострочених задач немає.")
        return
    for task in overdue:
        print("  " + format_task_line(task))


def print_task_list(tasks: list, title: str):
    """Виводить довільний список задач під заданим заголовком."""
    print(colorize(f"\n=== {title} ({len(tasks)}) ===", Color.BLUE + Color.BOLD))
    if not tasks:
        print("  Немає задач.")
        return
    for task in tasks:
        print("  " + format_task_line(task))


def print_statistics(stats):
    """Виводить статистику дошки у зручному форматі."""
    print(colorize("\n=== Статистика дошки ===", Color.BLUE + Color.BOLD))
    print(f"Усього задач: {colorize(str(stats['total']), Color.BOLD)}")

    if stats["total"] == 0:
        print("Дошка порожня.")
        return

    print("\nЗа статусом:")
    for status in tm.STATUSES:
        count = stats["by_status"][status]
        print(f"  {tm.STATUS_LABELS[status]}: {colorize(str(count), Color.BLUE)}")

    print("\nЗа пріоритетом:")
    for priority in tm.PRIORITIES:
        count = stats["by_priority"][priority]
        color = PRIORITY_COLORS.get(priority, Color.RESET)
        print(f"  {colorize(tm.PRIORITY_LABELS[priority], color)}: {count}")

    print(f"\nПрострочених задач: {colorize(str(stats['overdue_count']), Color.RED + Color.BOLD)}")
    completion = f"{stats['completion_rate']:.1f}%"
    print(f"Відсоток виконання (Done): {colorize(completion, Color.GREEN)}")


def ask_status(prompt: str):
    raw = ask(prompt).lower()
    if raw not in tm.STATUSES:
        print(colorize(f"[!] Невідомий статус. Доступні варіанти: {', '.join(tm.STATUSES)}.", Color.RED + Color.BOLD))
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
        print(colorize(f"[!] «{raw}» не є цілим числом.", Color.RED + Color.BOLD))
        return None