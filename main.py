# -*- coding: utf-8 -*-
"""
Kanban-менеджер задач — точка входу.
"""

import storage
import task_manager as tm
import ui

MENU = """
========== KANBAN-МЕНЕДЖЕР ЗАДАЧ ==========
1. Показати дошку
2. Додати задачу
3. Видалити задачу
4. Переглянути деталі задачі
5. Перемістити задачу
6. Редагувати задачу (пріоритет/дедлайн)
7. Показати прострочені задачі
8. Фільтрувати за пріоритетом
9. Сортувати всі задачі за дедлайном
0. Вийти
=============================================
"""


def action_add(tasks: list):
    title = ui.ask("Назва задачі: ")
    description = ui.ask("Опис (можна залишити порожнім): ")
    priority = ui.ask(f"Пріоритет [{'/'.join(tm.PRIORITIES)}] (Enter = medium): ").lower()
    if priority == "":
        priority = "medium"
    deadline = ui.ask("Дедлайн ДД.ММ.РРРР (Enter, якщо немає): ")
    deadline = deadline if deadline else None

    try:
        task = tm.add_task(tasks, title, description, priority, deadline)
        print(f"Задачу #{task['id']} «{task['title']}» додано в Todo.")
    except tm.TaskError as e:
        print(f"[!] {e}")


def action_delete(tasks: list):
    task_id = ui.ask_int("ID задачі для видалення: ")
    if task_id is None:
        return

    task = tm.find_task(tasks, task_id)
    if task is None:
        print(f"[!] Задачу з ID {task_id} не знайдено.")
        return

    ui.print_task_details(task)
    confirm = ui.ask(f"Видалити задачу «{task['title']}»? (y/n): ").lower()
    if confirm != "y":
        print("Видалення скасовано.")
        return

    try:
        tm.delete_task(tasks, task_id)
        print(f"Задачу #{task_id} видалено.")
    except tm.TaskError as e:
        print(f"[!] {e}")


def action_view_details(tasks: list):
    task_id = ui.ask_int("ID задачі для перегляду: ")
    if task_id is None:
        return

    task = tm.find_task(tasks, task_id)
    if task is None:
        print(f"[!] Задачу з ідентифікатором {task_id} не знайдено.")
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
        print(f"Задачу #{task['id']} перенесено в «{tm.STATUS_LABELS[new_status]}».")
    except tm.TaskError as e:
        print(f"[!] {e}")


def action_edit(tasks: list):
    task_id = ui.ask_int("ID задачі для редагування: ")
    if task_id is None:
        return
    task = tm.find_task(tasks, task_id)
    if task is None:
        print(f"[!] Задачу з ідентифікатором {task_id} не знайдено.")
        return

    ui.print_task_details(task)
    priority = ui.ask(f"Новий пріоритет [{'/'.join(tm.PRIORITIES)}] (Enter = не змінювати): ").lower()
    deadline = ui.ask("Новий дедлайн ДД.ММ.РРРР, або 'очистити', або Enter = не змінювати: ")

    priority_arg = priority if priority else None
    if deadline == "":
        deadline_arg = None
    elif deadline.lower() == "очистити":
        deadline_arg = ""
    else:
        deadline_arg = deadline

    try:
        tm.edit_task(tasks, task_id, priority=priority_arg, deadline=deadline_arg)
        print(f"Задачу #{task_id} оновлено.")
    except tm.TaskError as e:
        print(f"[!] {e}")


def action_filter_by_priority(tasks: list):
    priority = ui.ask(f"Пріоритет для фільтра [{'/'.join(tm.PRIORITIES)}]: ").lower()
    try:
        filtered = tm.filter_by_priority(tasks, priority)
        ui.print_task_list(filtered, f"Задачі з пріоритетом «{tm.PRIORITY_LABELS.get(priority, priority)}»")
    except tm.TaskError as e:
        print(f"[!] {e}")


def action_sort_by_deadline(tasks: list):
    sorted_tasks = tm.sort_by_deadline(tasks)
    ui.print_task_list(sorted_tasks, "Усі задачі за дедлайном")


def main():
    tasks = storage.load_tasks()

    while True:
        print(MENU)
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
            ui.print_overdue(tasks)
        elif choice == "8":
            action_filter_by_priority(tasks)
        elif choice == "9":
            action_sort_by_deadline(tasks)
        elif choice == "0":
            print("До побачення!")
            break
        else:
            print(f"[!] Невідомий пункт меню: «{choice}». Спробуйте ще раз.")


if __name__ == "__main__":
    main()