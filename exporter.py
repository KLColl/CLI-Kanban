"""
Модуль для експорту задач у різні формати (CSV, Markdown).
"""

import csv
import task_manager as tm


def _escape_markdown(text: str) -> str:
    if text is None:
        return ""
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def export_board_csv(tasks: list, filename: str = "board_export.csv") -> str:
    if not filename.strip():
        raise tm.TaskError("Ім'я файлу для CSV не може бути порожнім.")

    headers_mapping = {
        "id": "ID",
        "title": "Назва",
        "description": "Опис",
        "status": "Статус",
        "priority": "Пріоритет",
        "deadline": "Дедлайн",
        "is_overdue": "Прострочено",
        "created_at": "Створено",
        "tags": "Теги",
        "subtasks_done": "Виконано підзадач",
        "subtasks_total": "Всього підзадач",
        "history": "Історія",
    }

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers_mapping.keys())
        writer.writerow(headers_mapping)

        for task in tasks:
            done, total = tm.get_subtask_progress(task)
            is_overdue_str = "Так" if tm.is_overdue(task) else "Ні"

            writer.writerow({
                "id": task.get("id", ""),
                "title": task.get("title", ""),
                "description": task.get("description", ""),
                "status": tm.STATUS_LABELS.get(task.get("status", ""), task.get("status", "")),
                "priority": tm.PRIORITY_LABELS.get(task.get("priority", ""), task.get("priority", "")),
                "deadline": task.get("deadline") or "",
                "is_overdue": is_overdue_str,
                "created_at": task.get("created_at", ""),
                "tags": ", ".join(task.get("tags", [])),
                "subtasks_done": done,
                "subtasks_total": total,
                "history": "\n".join(
                    f"{h.get('timestamp', '')} — {h.get('action', '')}"
                    for h in task.get("history", [])
                ),
            })

    return filename


def export_board_markdown(tasks: list, filename: str = "board_export.md") -> str:
    if not filename.strip():
        raise tm.TaskError("Ім'я файлу для Markdown не може бути порожнім.")

    stats = tm.get_statistics(tasks)

    lines = [
        "# 📋 Kanban Board Export",
        "",
        "## 📊 Статистика дошки",
        f"- **Усього задач:** {stats['total']}",
        f"- **Відсоток виконання:** {stats['completion_rate']:.1f}%",
        f"- **Прострочених задач:** {stats['overdue_count']}",
        "",
        "---",
        ""
    ]

    for status in tm.STATUSES:
        status_tasks = [t for t in tasks if t.get("status") == status]
        lines.append(f"## {tm.STATUS_LABELS[status]} ({len(status_tasks)})")
        lines.append("")

        if not status_tasks:
            lines.append("_Немає задач._")
            lines.append("")
            continue


        lines.extend([
            "| ID | Назва | Опис | Пріоритет | Дедлайн | Теги | Підзадачі | Історія |",
            "|---:|---|---|---|---|---|---:|---|",
        ])

        for task in status_tasks:
            priority = tm.PRIORITY_LABELS.get(task.get("priority", ""), task.get("priority", ""))

            deadline = task.get("deadline") or "—"
            if tm.is_overdue(task):
                deadline = f"⚠️ **{deadline}**"
            else:
                deadline = _escape_markdown(deadline)

            raw_tags = task.get("tags", [])
            tags = " ".join([f"`{t}`" for t in raw_tags]) if raw_tags else "—"

            done, total = tm.get_subtask_progress(task)
            subtasks = f"{done}/{total}" if total else "—"

            desc = task.get("description", "") or "—"

            history_items = []
            for h in task.get("history", []):
                ts = _escape_markdown(h.get("timestamp", ""))
                act = _escape_markdown(h.get("action", ""))
                history_items.append(f"_{ts}_: {act}")
            history_md = "<br>".join(history_items) if history_items else "—"

            lines.append(
                f"| {task.get('id', '')} | "
                f"**{_escape_markdown(task.get('title', ''))}** | "
                f"{_escape_markdown(desc)} | "
                f"{_escape_markdown(priority)} | "
                f"{deadline} | "
                f"{tags} | "
                f"{subtasks} | "
                f"{history_md} |"
            )

        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    return filename