"""
Автоматизовані тести для Kanban-менеджера задач.
Запуск: python -m pytest test_kanban.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
import task_manager as tm


# ---------------------------------------------------------------------------
# Фікстури
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_tasks():
    """Порожній список задач."""
    return []


@pytest.fixture
def sample_tasks():
    """Невеликий набір задач для тестів."""
    return [
        {
            "id": 1,
            "title": "Перша задача",
            "description": "Опис першої задачі",
            "status": "todo",
            "priority": "high",
            "deadline": "31.12.2030",
            "created_at": "01.01.2026",
            "tags": ["backend", "feature"],
            "history": [],
            "subtasks": [],
        },
        {
            "id": 2,
            "title": "Друга задача",
            "description": "Опис другої задачі",
            "status": "in_progress",
            "priority": "medium",
            "deadline": "15.07.2026",
            "created_at": "02.01.2026",
            "tags": ["ui"],
            "history": [],
            "subtasks": [
                {"id": 1, "title": "Підзадача А", "done": False},
                {"id": 2, "title": "Підзадача Б", "done": True},
            ],
        },
        {
            "id": 3,
            "title": "Виконана задача",
            "description": "",
            "status": "done",
            "priority": "low",
            "deadline": None,
            "created_at": "03.01.2026",
            "tags": [],
            "history": [],
            "subtasks": [],
        },
    ]


# ---------------------------------------------------------------------------
# Допоміжна функція: «мок» storage.save_tasks, щоб тести не писали на диск
# ---------------------------------------------------------------------------

def no_save(tasks):
    pass


# ---------------------------------------------------------------------------
# 1. add_task — додавання задачі
# ---------------------------------------------------------------------------

class TestAddTask:
    def test_add_basic(self, empty_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            task = tm.add_task(empty_tasks, "Нова задача")

        assert task["id"] == 1
        assert task["title"] == "Нова задача"
        assert task["status"] == "todo"
        assert task["priority"] == "medium"
        assert task in empty_tasks

    def test_add_with_all_fields(self, empty_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            task = tm.add_task(
                empty_tasks,
                title="Задача з тегами",
                description="Тест",
                priority="high",
                deadline="25.12.2030",
                tags="робота, важливо",
            )

        assert task["priority"] == "high"
        assert task["deadline"] == "25.12.2030"
        assert "робота" in task["tags"]
        assert "важливо" in task["tags"]

    def test_add_empty_title_raises(self, empty_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="порожньою"):
                tm.add_task(empty_tasks, "")

    def test_add_invalid_priority_raises(self, empty_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="пріоритет"):
                tm.add_task(empty_tasks, "Задача", priority="urgent")

    def test_add_invalid_deadline_raises(self, empty_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="дата"):
                tm.add_task(empty_tasks, "Задача", deadline="2030-12-31")

    def test_ids_are_unique(self, empty_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            t1 = tm.add_task(empty_tasks, "Задача 1")
            t2 = tm.add_task(empty_tasks, "Задача 2")
            t3 = tm.add_task(empty_tasks, "Задача 3")
        assert t1["id"] != t2["id"] != t3["id"]


# ---------------------------------------------------------------------------
# 2. move_task — переміщення між статусами
# ---------------------------------------------------------------------------

class TestMoveTask:
    def test_move_todo_to_in_progress(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            task = tm.move_task(sample_tasks, 1, "in_progress")
        assert task["status"] == "in_progress"

    def test_move_records_history(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            task = tm.move_task(sample_tasks, 1, "done")
        assert any("Todo → Done" in h["action"] for h in task["history"])

    def test_move_same_status_raises(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="вже має статус"):
                tm.move_task(sample_tasks, 1, "todo")

    def test_move_invalid_status_raises(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="статус"):
                tm.move_task(sample_tasks, 1, "cancelled")

    def test_move_nonexistent_task_raises(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="не знайдено"):
                tm.move_task(sample_tasks, 999, "done")


# ---------------------------------------------------------------------------
# 3. filter / search / sort
# ---------------------------------------------------------------------------

class TestFilterAndSearch:
    def test_filter_by_priority(self, sample_tasks):
        result = tm.filter_by_priority(sample_tasks, "high")
        assert all(t["priority"] == "high" for t in result)
        assert len(result) == 1

    def test_filter_by_priority_invalid_raises(self, sample_tasks):
        with pytest.raises(tm.TaskError):
            tm.filter_by_priority(sample_tasks, "критичний")

    def test_filter_by_tag(self, sample_tasks):
        result = tm.filter_by_tag(sample_tasks, "ui")
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_filter_by_tag_empty_raises(self, sample_tasks):
        with pytest.raises(tm.TaskError, match="порожнім"):
            tm.filter_by_tag(sample_tasks, "")

    def test_search_by_title(self, sample_tasks):
        result = tm.search_tasks(sample_tasks, "перша")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_search_case_insensitive(self, sample_tasks):
        result = tm.search_tasks(sample_tasks, "ПЕРША")
        assert len(result) == 1

    def test_search_empty_query_raises(self, sample_tasks):
        with pytest.raises(tm.TaskError, match="порожнім"):
            tm.search_tasks(sample_tasks, "")

    def test_sort_by_deadline_no_deadline_last(self, sample_tasks):
        sorted_tasks = tm.sort_by_deadline(sample_tasks)
        # Задача без дедлайну (#3) повинна бути останньою
        assert sorted_tasks[-1]["id"] == 3


# ---------------------------------------------------------------------------
# 4. is_overdue
# ---------------------------------------------------------------------------

class TestIsOverdue:
    def test_overdue_task(self):
        task = {
            "status": "todo",
            "deadline": "01.01.2020",  # давно минув
        }
        assert tm.is_overdue(task) is True

    def test_future_deadline_not_overdue(self):
        task = {
            "status": "todo",
            "deadline": "31.12.2099",
        }
        assert tm.is_overdue(task) is False

    def test_done_task_not_overdue(self):
        task = {
            "status": "done",
            "deadline": "01.01.2020",
        }
        assert tm.is_overdue(task) is False

    def test_no_deadline_not_overdue(self):
        task = {
            "status": "todo",
            "deadline": None,
        }
        assert tm.is_overdue(task) is False


# ---------------------------------------------------------------------------
# 5. subtasks
# ---------------------------------------------------------------------------

class TestSubtasks:
    def test_add_subtask(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            sub = tm.add_subtask(sample_tasks, 1, "Нова підзадача")
        assert sub["title"] == "Нова підзадача"
        assert sub["done"] is False

    def test_add_subtask_empty_title_raises(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            with pytest.raises(tm.TaskError, match="порожньою"):
                tm.add_subtask(sample_tasks, 1, "")

    def test_toggle_subtask(self, sample_tasks):
        # Підзадача 1 у задачі 2 починає як done=False
        with patch.object(tm.storage, "save_tasks", no_save):
            sub = tm.toggle_subtask(sample_tasks, 2, 1)
        assert sub["done"] is True

    def test_toggle_subtask_twice_restores(self, sample_tasks):
        with patch.object(tm.storage, "save_tasks", no_save):
            tm.toggle_subtask(sample_tasks, 2, 1)
            sub = tm.toggle_subtask(sample_tasks, 2, 1)
        assert sub["done"] is False

    def test_get_subtask_progress(self, sample_tasks):
        # Задача 2: підзадача 1 — False, підзадача 2 — True
        done, total = tm.get_subtask_progress(sample_tasks[1])
        assert done == 1
        assert total == 2


# ---------------------------------------------------------------------------
# 6. get_statistics
# ---------------------------------------------------------------------------

class TestStatistics:
    def test_statistics_counts(self, sample_tasks):
        stats = tm.get_statistics(sample_tasks)
        assert stats["total"] == 3
        assert stats["by_status"]["todo"] == 1
        assert stats["by_status"]["in_progress"] == 1
        assert stats["by_status"]["done"] == 1

    def test_statistics_completion_rate(self, sample_tasks):
        stats = tm.get_statistics(sample_tasks)
        # 1 done із 3 → 33.3%
        assert abs(stats["completion_rate"] - 100 / 3) < 0.1

    def test_statistics_empty_board(self, empty_tasks):
        stats = tm.get_statistics(empty_tasks)
        assert stats["total"] == 0
        assert stats["completion_rate"] == 0.0


# ---------------------------------------------------------------------------
# 7. parse_tags
# ---------------------------------------------------------------------------

class TestParseTags:
    def test_basic_parsing(self):
        assert tm.parse_tags("робота, важливо, ui") == ["робота", "важливо", "ui"]

    def test_deduplication(self):
        result = tm.parse_tags("тег, тег, ТЕГ")
        assert result.count("тег") == 1

    def test_list_input(self):
        assert tm.parse_tags(["a", "b"]) == ["a", "b"]

    def test_empty_string(self):
        assert tm.parse_tags("") == []