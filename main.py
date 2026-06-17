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
4. Опис задачі
0. Вийти
=============================================
"""


def action_add(tasks):
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


def action_delete(tasks):
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


def action_view_details(tasks):
    task_id = ui.ask_int("ID задачі для перегляду: ")
    if task_id is None:
        return

    task = tm.find_task(tasks, task_id)
    if task is None:
        print(f"[!] Задачу з ідентифікатором {task_id} не знайдено.")
        return

    ui.print_task_details(task)


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
        elif choice == "0":
            print("До побачення!")
            break
        else:
            print(f"[!] Невідомий пункт меню: «{choice}». Спробуйте ще раз.")


if __name__ == "__main__":
    main()