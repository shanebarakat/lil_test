"""
A simple CLI To-Do application.

This module provides a small set of business functions for managing a task list
and a command-line interface for interacting with the tasks. Business logic is
separated from I/O: functions that manipulate tasks operate on Python data
structures and raise exceptions on invalid input; input()/print() are only used
in the CLI entrypoint and menu.

Tasks are persisted to a JSON file (default: "tasks.json"). Each task is a
dictionary with the following structure:
    {
        "title": "<task title>",
        "done": <bool>
    }

Public functions:
- load_tasks(file_path: str = 'tasks.json') -> list
- save_tasks(tasks: list, file_path: str = 'tasks.json') -> None
- add_task(tasks: list, title: str) -> None
- view_tasks(tasks: list) -> list
- remove_task(tasks: list, index: int) -> None
- mark_task(tasks: list, index: int) -> None
- clear_tasks(tasks: list) -> None

Run this module directly to launch the interactive CLI.
"""

from typing import List, Dict
import json
import logging
import os
import tempfile
import sys

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_tasks(file_path: str = 'tasks.json') -> list:
    """
    Load tasks from a JSON file.

    If the file does not exist, returns an empty list. If the file exists but
    is malformed, logs an error and returns an empty list.

    Args:
        file_path: Path to the JSON file storing tasks.

    Returns:
        A list of task dictionaries, each with 'title' (str) and 'done' (bool).
    """
    if not os.path.exists(file_path):
        logging.info("Tasks file '%s' does not exist. Starting with empty task list.", file_path)
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Validate basic structure
        if not isinstance(data, list):
            logging.error("Tasks file '%s' does not contain a list. Ignoring contents.", file_path)
            return []
        sanitized: List[Dict] = []
        for item in data:
            if not isinstance(item, dict):
                logging.warning("Skipping malformed task entry: %r", item)
                continue
            title = item.get('title')
            done = item.get('done', False)
            if not isinstance(title, str):
                logging.warning("Skipping task with invalid title: %r", item)
                continue
            sanitized.append({'title': title, 'done': bool(done)})
        return sanitized
    except (json.JSONDecodeError, OSError) as exc:
        logging.error("Failed to load tasks from '%s': %s", file_path, exc)
        return []


def save_tasks(tasks: list, file_path: str = 'tasks.json') -> None:
    """
    Save tasks to a JSON file in a safe (atomic) manner.

    Writes to a temporary file in the same directory and replaces the target file.
    Raises IOError if writing fails.

    Args:
        tasks: List of task dictionaries to save.
        file_path: Path to the JSON file where tasks should be saved.

    Raises:
        IOError: If saving fails due to an OS-level error.
    """
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")

    directory = os.path.dirname(os.path.abspath(file_path)) or '.'
    try:
        with tempfile.NamedTemporaryFile('w', delete=False, dir=directory, encoding='utf-8') as tmp:
            json.dump(tasks, tmp, indent=2, ensure_ascii=False)
            tmp_path = tmp.name
        # Atomic replace
        os.replace(tmp_path, file_path)
        logging.info("Tasks successfully saved to '%s'.", file_path)
    except OSError as exc:
        logging.error("Failed to save tasks to '%s': %s", file_path, exc)
        # Attempt to clean up temp file if it exists
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise IOError(f"Failed to save tasks: {exc}") from exc


def add_task(tasks: list, title: str) -> None:
    """
    Add a new task to the tasks list.

    The function modifies the provided tasks list in place.

    Args:
        tasks: List of current tasks.
        title: Title of the new task. Must be a non-empty string.

    Raises:
        ValueError: If the title is empty or not a string.
        TypeError: If tasks is not a list.
    """
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    task = {'title': title.strip(), 'done': False}
    tasks.append(task)
    logging.info("Added task: %s", task['title'])


def view_tasks(tasks: list) -> list:
    """
    Return a shallow copy of the tasks list for viewing.

    Args:
        tasks: List of current tasks.

    Returns:
        A list of task dictionaries (copies) so callers can inspect without mutating.
    """
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    # Return copies to protect internal structure
    return [{'title': t.get('title', ''), 'done': bool(t.get('done', False))} for t in tasks]


def remove_task(tasks: list, index: int) -> None:
    """
    Remove a task at the given index from the tasks list.

    Args:
        tasks: List of current tasks.
        index: Zero-based index of the task to remove.

    Raises:
        IndexError: If index is out of range.
        TypeError: If tasks is not a list or index is not an int.
    """
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    if not isinstance(index, int):
        raise TypeError("index must be an int")
    if index < 0 or index >= len(tasks):
        raise IndexError("task index out of range")
    removed = tasks.pop(index)
    logging.info("Removed task at index %d: %s", index, removed.get('title'))


def mark_task(tasks: list, index: int) -> None:
    """
    Mark the task at the given index as done.

    Args:
        tasks: List of current tasks.
        index: Zero-based index of the task to mark as done.

    Raises:
        IndexError: If index is out of range.
        TypeError: If tasks is not a list or index is not an int.
    """
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    if not isinstance(index, int):
        raise TypeError("index must be an int")
    if index < 0 or index >= len(tasks):
        raise IndexError("task index out of range")
    tasks[index]['done'] = True
    logging.info("Marked task at index %d as done: %s", index, tasks[index].get('title'))


def clear_tasks(tasks: list) -> None:
    """
    Remove all tasks from the list (in place).

    Args:
        tasks: List of current tasks.

    Raises:
        TypeError: If tasks is not a list.
    """
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    tasks.clear()
    logging.info("Cleared all tasks.")


def _print_menu() -> None:
    """
    Print the CLI menu. This is used only within the CLI (I/O allowed).
    """
    print("\nTo-Do CLI")
    print("---------")
    print("1) View tasks")
    print("2) Add task")
    print("3) Remove task")
    print("4) Mark task as done")
    print("5) Clear all tasks")
    print("6) Exit")


def _prompt_choice() -> str:
    """
    Prompt the user for a menu choice and return the raw input.
    """
    return input("Choose an option [1-6]: ").strip()


def _prompt_task_title() -> str:
    """
    Prompt the user for a task title and return it.
    """
    return input("Enter task title: ").strip()


def _prompt_index(num_tasks: int) -> int:
    """
    Prompt the user for a task index (1-based). Validates and returns zero-based index.

    Args:
        num_tasks: Number of tasks available.

    Returns:
        Zero-based index selected by the user.

    Raises:
        ValueError: If the input is not a valid integer or not in range.
    """
    raw = input(f"Enter task number (1-{num_tasks}): ").strip()
    if not raw:
        raise ValueError("No input provided for index")
    try:
        one_based = int(raw)
    except ValueError:
        raise ValueError("Invalid number")
    if one_based < 1 or one_based > num_tasks:
        raise ValueError("Index out of range")
    return one_based - 1


def main() -> None:
    """
    Launch the interactive CLI loop for the To-Do application.

    This function handles all user interaction (input/print) and orchestrates
    calls to the business logic functions defined above.
    """
    file_path = 'tasks.json'
    try:
        tasks = load_tasks(file_path)
    except Exception as exc:
        logging.error("Unexpected error loading tasks: %s", exc)
        tasks = []

    while True:
        _print_menu()
        choice = _prompt_choice()
        if choice == '1':
            current = view_tasks(tasks)
            if not current:
                print("\nNo tasks found.")
            else:
                print("\nTasks:")
                for i, task in enumerate(current, start=1):
                    status = '✓' if task.get('done') else ' '
                    print(f"{i}. [{status}] {task.get('title')}")
        elif choice == '2':
            title = _prompt_task_title()
            try:
                add_task(tasks, title)
            except (ValueError, TypeError) as exc:
                print(f"Error adding task: {exc}")
                continue
            try:
                save_tasks(tasks, file_path)
            except IOError as exc:
                print(f"Failed to save tasks: {exc}")
        elif choice == '3':
            if not tasks:
                print("\nNo tasks to remove.")
                continue
            for i, task in enumerate(tasks, start=1):
                status = '✓' if task.get('done') else ' '
                print(f"{i}. [{status}] {task.get('title')}")
            try:
                idx = _prompt_index(len(tasks))
                remove_task(tasks, idx)
                try:
                    save_tasks(tasks, file_path)
                except IOError as exc:
                    print(f"Failed to save tasks: {exc}")
            except ValueError as exc:
                print(f"Invalid selection: {exc}")
            except IndexError as exc:
                print(f"Error: {exc}")
        elif choice == '4':
            if not tasks:
                print("\nNo tasks to mark.")
                continue
            for i, task in enumerate(tasks, start=1):
                status = '✓' if task.get('done') else ' '
                print(f"{i}. [{status}] {task.get('title')}")
            try:
                idx = _prompt_index(len(tasks))
                mark_task(tasks, idx)
                try:
                    save_tasks(tasks, file_path)
                except IOError as exc:
                    print(f"Failed to save tasks: {exc}")
            except ValueError as exc:
                print(f"Invalid selection: {exc}")
            except IndexError as exc:
                print(f"Error: {exc}")
        elif choice == '5':
            confirm = input("Are you sure you want to clear all tasks? (y/N): ").strip().lower()
            if confirm == 'y':
                clear_tasks(tasks)
                try:
                    save_tasks(tasks, file_path)
                except IOError as exc:
                    print(f"Failed to save tasks: {exc}")
                print("All tasks cleared.")
            else:
                print("Clear cancelled.")
        elif choice == '6':
            print("Goodbye!")
            try:
                save_tasks(tasks, file_path)
            except IOError:
                # If saving on exit fails, we log and still exit.
                logging.error("Failed to save tasks on exit.")
            break
        else:
            print("Invalid choice. Please select a number between 1 and 6.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting on user interrupt.")
        try:
            # Attempt to save on interrupt
            # Load current tasks file to avoid raising if missing — no guarantee of latest state
            # No direct access to tasks variable here; just exit.
            pass
        finally:
            sys.exit(0)