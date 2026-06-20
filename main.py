"""
Kanban-менеджер задач — точка входу.
"""
import exporter
import storage
import task_manager as tm
import ui

MAIN_MENU = """
========== KANBAN-МЕНЕДЖЕР ЗАДАЧ ==========
1. Дошка та задачі
2. Пошук і фільтри
3. Статистика
4. Експорт
0. Вийти
=============================================
"""

BOARD_MENU = """
----- ДОШКА ТА ЗАДАЧІ -----
1. Показати дошку
2. Додати задачу
3. Видалити задачу
4. Переглянути деталі задачі
5. Перемістити задачу
6. Редагувати задачу (пріоритет/дедлайн/теги)
7. Архівувати виконані задачі (Done)
8. Переглянути архів
9. Додати підзадачу
10. Позначити підзадачу виконаною/невиконаною
0. Назад до головного меню
----------------------------
"""

SEARCH_MENU = """
----- ПОШУК І ФІЛЬТРИ -----
1. Показати прострочені задачі
2. Фільтрувати за пріоритетом
3. Сортувати всі задачі за дедлайном
4. Пошук задач за текстом
5. Фільтрувати за тегом
0. Назад до головного меню
----------------------------
"""

STATS_MENU = """
----- СТАТИСТИКА -----
1. Показати статистику дошки
0. Назад до головного меню
----------------------------
"""

EXPORT_MENU = """
----- ЕКСПОРТ -----
1. Експортувати у CSV
2. Експортувати у Markdown
0. Назад до головного меню
----------------------------
"""


def action_add(tasks: list):
    title = ui.ask("Назва задачі: ")
    description = ui.ask("Опис (можна залишити порожнім): ")
    priority = ui.ask(f"Пріоритет [{'/'.join(tm.PRIORITIES)}] (Enter = medium): ").lower()
    if priority == "":
        priority = "medium"
    deadline = ui.ask("Дедлайн ДД.ММ.РРРР (Enter, якщо немає): ")
    deadline = deadline if deadline else None
    tags = ui.ask("Теги через кому (Enter, якщо немає): ")

    try:
        task = tm.add_task(tasks, title, description, priority, deadline, tags)
        print(ui.colorize(f"Задачу #{task['id']} «{task['title']}» додано в Todo.", ui.Color.GREEN))
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_delete(tasks: list):
    task_id = ui.ask_int("ID задачі для видалення: ")
    if task_id is None:
        return

    task = tm.find_task(tasks, task_id)
    if task is None:
        print(ui.colorize(f"[!] Задачу з ID {task_id} не знайдено.", ui.Color.RED + ui.Color.BOLD))
        return

    ui.print_task_details(task)
    confirm = ui.ask(f"Видалити задачу «{task['title']}»? (y/n): ").lower()
    if confirm != "y":
        print(ui.colorize("Видалення скасовано.", ui.Color.YELLOW))
        return

    try:
        tm.delete_task(tasks, task_id)
        print(ui.colorize(f"Задачу #{task_id} видалено.", ui.Color.GREEN))
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_view_details(tasks: list):
    task_id = ui.ask_int("ID задачі для перегляду: ")
    if task_id is None:
        return

    task = tm.find_task(tasks, task_id)
    if task is None:
        print(ui.colorize(f"[!] Задачу з ідентифікатором {task_id} не знайдено.", ui.Color.RED + ui.Color.BOLD))
        return

    ui.print_task_details(task)


def action_move(tasks: list):
    task_id = ui.ask_int("ID задачі для переміщення: ")
    if task_id is None:
        return
    new_status = ui.ask_status(f"Новий статус [{'/'.join(tm.STATUSES)}]: ")
    if new_status is None:
        return
    try:
        task = tm.move_task(tasks, task_id, new_status)
        print(ui.colorize(f"Задачу #{task['id']} перенесено в «{tm.STATUS_LABELS[new_status]}».", ui.Color.GREEN))
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_edit(tasks: list):
    task_id = ui.ask_int("ID задачі для редагування: ")
    if task_id is None:
        return
    task = tm.find_task(tasks, task_id)
    if task is None:
        print(ui.colorize(f"[!] Задачу з ідентифікатором {task_id} не знайдено.", ui.Color.RED + ui.Color.BOLD))
        return

    ui.print_task_details(task)
    priority = ui.ask(f"Новий пріоритет [{'/'.join(tm.PRIORITIES)}] (Enter = не змінювати): ").lower()
    deadline = ui.ask("Новий дедлайн ДД.ММ.РРРР, або 'очистити', або Enter = не змінювати: ")
    tags = ui.ask("Нові теги через кому (Enter = не змінювати): ")

    priority_arg = priority if priority else None
    if deadline == "":
        deadline_arg = None
    elif deadline.lower() == "очистити":
        deadline_arg = ""
    else:
        deadline_arg = deadline
    tags_arg = tags if tags else None

    try:
        tm.edit_task(tasks, task_id, priority=priority_arg, deadline=deadline_arg, tags=tags_arg)
        print(ui.colorize(f"Задачу #{task_id} оновлено.", ui.Color.GREEN))
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_filter_by_priority(tasks: list):
    priority = ui.ask(f"Пріоритет для фільтра [{'/'.join(tm.PRIORITIES)}]: ").lower()
    try:
        filtered = tm.filter_by_priority(tasks, priority)
        ui.print_task_list(filtered, f"Задачі з пріоритетом «{tm.PRIORITY_LABELS.get(priority, priority)}»")
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_sort_by_deadline(tasks: list):
    sorted_tasks = tm.sort_by_deadline(tasks)
    ui.print_task_list(sorted_tasks, "Усі задачі за дедлайном")


def action_search(tasks: list):
    query = ui.ask("Текст для пошуку: ")
    try:
        found = tm.search_tasks(tasks, query)
        ui.print_task_list(found, f"Результати пошуку «{query}»")
    except tm.TaskError as e:
        print(f"[!] {e}")


def action_statistics(tasks: list):
    stats = tm.get_statistics(tasks)
    ui.print_statistics(stats)


def action_filter_by_tag(tasks: list):
    tag = ui.ask("Тег для фільтра: ")
    try:
        filtered = tm.filter_by_tag(tasks, tag)
        ui.print_task_list(filtered, f"Задачі з тегом «{tag.strip().lower()}»")
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_archive_done(tasks: list):
    confirm = ui.ask("Архівувати всі задачі зі статусом Done? (y/n): ").lower()
    if confirm != "y":
        print(ui.colorize("Архівування скасовано.", ui.Color.YELLOW))
        return
    archived = tm.archive_done_tasks(tasks)
    print(ui.colorize(f"Архівовано задач: {len(archived)}.", ui.Color.GREEN))


def action_view_archive():
    archived = tm.get_archived_tasks()
    ui.print_task_list(archived, "Архів виконаних задач")


def action_add_subtask(tasks: list):
    task_id = ui.ask_int("ID задачі: ")
    if task_id is None:
        return
    title = ui.ask("Назва підзадачі: ")
    try:
        subtask = tm.add_subtask(tasks, task_id, title)
        print(ui.colorize(f"Підзадачу #{subtask['id']} «{subtask['title']}» додано.", ui.Color.GREEN))
    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_toggle_subtask(tasks: list):
    task_id = ui.ask_int("ID задачі: ")
    if task_id is None:
        return

    subtask_id = ui.ask_int("ID підзадачі: ")
    if subtask_id is None:
        return

    try:
        subtask = tm.get_subtask(tasks, task_id, subtask_id)
        new_state = "виконано" if not subtask["done"] else "не виконано"

        confirm = ui.ask(
            f"Підтвердити зміну статусу підзадачі «{subtask['title']}» на {new_state}? (y/n): "
        )

        if confirm.lower() == "y":
            subtask = tm.toggle_subtask(tasks, task_id, subtask_id)
            state_text = ui.colorize("виконано", ui.Color.GREEN) if subtask["done"] else ui.colorize("не виконано", ui.Color.RED)
            print(f"Підзадача «{subtask['title']}» тепер: {state_text}.")
        else:
            print(f"Зміна статусу «{subtask['title']}» відхилена")


    except tm.TaskError as e:
        print(ui.colorize(f"[!] {e}", ui.Color.RED + ui.Color.BOLD))


def action_export_board_csv(tasks: list):
    filename = ui.ask("Ім'я файлу (Enter = board_export.csv): ")
    filename = filename if filename else "board_export.csv"
    if exporter.export_board_csv(tasks, filename):
        print(ui.colorize(f"Дошку успішно експортовано у «{filename}».", ui.Color.GREEN))


def action_export_board_md(tasks: list):
    filename = ui.ask("Ім'я файлу (Enter = board_export.md): ")
    filename = filename if filename else "board_export.md"
    if exporter.export_board_markdown(tasks, filename):
        print(ui.colorize(f"Дошку успішно експортовано у «{filename}».", ui.Color.GREEN))


def board_menu_loop(tasks: list):
    """Підменю «Дошка та задачі»."""
    while True:
        print(BOARD_MENU)
        choice = ui.ask("Оберіть дію: ")

        if choice == "1":
            ui.print_board(tasks)
        elif choice == "2":
            action_add(tasks)
        elif choice == "3":
            action_delete(tasks)
        elif choice == "4":
            action_view_details(tasks)
        elif choice == "5":
            action_move(tasks)
        elif choice == "6":
            action_edit(tasks)
        elif choice == "7":
            action_archive_done(tasks)
        elif choice == "8":
            action_view_archive()
        elif choice == "9":
            action_add_subtask(tasks)
        elif choice == "10":
            action_toggle_subtask(tasks)
        elif choice == "0":
            return
        else:
            print(ui.colorize(f"[!] Невідомий пункт меню: «{choice}». Спробуйте ще раз.", ui.Color.RED + ui.Color.BOLD))


def search_menu_loop(tasks: list):
    """Підменю «Пошук і фільтри»."""
    while True:
        print(SEARCH_MENU)
        choice = ui.ask("Оберіть дію: ")

        if choice == "1":
            ui.print_overdue(tasks)
        elif choice == "2":
            action_filter_by_priority(tasks)
        elif choice == "3":
            action_sort_by_deadline(tasks)
        elif choice == "4":
            action_search(tasks)
        elif choice == "5":
            action_filter_by_tag(tasks)
        elif choice == "0":
            return
        else:
            print(ui.colorize(f"[!] Невідомий пункт меню: «{choice}». Спробуйте ще раз.", ui.Color.RED + ui.Color.BOLD))


def stats_menu_loop(tasks: list):
    """Підменю «Статистика»."""
    while True:
        print(STATS_MENU)
        choice = ui.ask("Оберіть дію: ")

        if choice == "1":
            action_statistics(tasks)
        elif choice == "0":
            return
        else:
            print(ui.colorize(f"[!] Невідомий пункт меню: «{choice}». Спробуйте ще раз.", ui.Color.RED + ui.Color.BOLD))


def export_menu_loop(tasks: list):
    """Підменю «Експорт»."""
    while True:
        print(EXPORT_MENU)
        choice = ui.ask("Оберіть формат: ")

        if choice == "1":
            action_export_board_csv(tasks)
        elif choice == "2":
            action_export_board_md(tasks)
        elif choice == "0":
            return
        else:
            print(ui.colorize("[!] Невідомий вибір. Спробуйте ще раз.", ui.Color.RED + ui.Color.BOLD))


def show_notifications(tasks: list):
    """Виводить банер з простроченими та близькими дедлайнами."""
    overdue = [t for t in tasks if tm.is_overdue(t) and t.get("status") != "done"]
    approaching = [t for t in tasks if tm.is_approaching_deadline(t, days=3)]

    if not overdue and not approaching:
        return

    print()
    print(ui.colorize("="*12 + " 🔔 ДЕДЛАЙНИ " + "="*12, ui.Color.BOLD + ui.Color.YELLOW))

    if overdue:
        print(ui.colorize(f"⚠️ Прострочено ({len(overdue)}):", ui.Color.RED + ui.Color.BOLD))
        for t in overdue:
            print(ui.colorize(f"   - [{t['id']}] {t['title']} (був {t['deadline']})", ui.Color.RED))
        print()

    if approaching:
        print(ui.colorize(f"⏳ Скоро завершуються ({len(approaching)}):", ui.Color.YELLOW + ui.Color.BOLD))
        for t in approaching:
            print(ui.colorize(f"   - [{t['id']}] {t['title']} (до {t['deadline']})", ui.Color.YELLOW))

    print(ui.colorize("="*46, ui.Color.BOLD + ui.Color.YELLOW))


def main():
    tasks = storage.load_tasks()
    show_notifications(tasks)

    while True:
        print(MAIN_MENU)
        choice = ui.ask("Оберіть дію: ")

        if choice == "1":
            board_menu_loop(tasks)
        elif choice == "2":
            search_menu_loop(tasks)
        elif choice == "3":
            stats_menu_loop(tasks)
        elif choice == "4":
            export_menu_loop(tasks)
        elif choice == "0":
            print("До побачення!")
            break
        else:
            print(ui.colorize(f"[!] Невідомий пункт меню: «{choice}». Спробуйте ще раз.", ui.Color.RED + ui.Color.BOLD))


if __name__ == "__main__":
    main()