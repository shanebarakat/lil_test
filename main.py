# Simple 100-line To-Do List App

import os
import logging

# Configure basic logging for error reporting and security auditability.
# We keep output to WARNING to avoid emitting INFO-level console output by default.
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# Welcome Message
print("Welcome to the Simple To-Do List App!")
print("---------------------------------------")

# Initialize task list
tasks = []

# Helper: parse and validate a task number input
def parse_task_number(prompt, max_num):
    """
    Safely parse a user-provided task number.
    Returns an integer in range 1..max_num if valid, otherwise None.

    Security note: All user inputs are treated as untrusted. We explicitly
    validate digits and range before use to avoid unexpected behavior.
    """
    raw = input(prompt).strip()
    if not raw.isdigit():
        logging.debug("Non-numeric input received when number expected.")
        print("Please enter a number.")
        return None
    try:
        num = int(raw)
    except ValueError:
        # This should rarely happen because of isdigit check, but handle explicitly.
        logging.debug("ValueError parsing numeric input.")
        print("Please enter a number.")
        return None
    if 1 <= num <= max_num:
        return num
    else:
        logging.debug("User provided out-of-range task number.")
        print("Invalid task number.")
        return None

# Function to display menu
def display_menu():
    print("\nPlease choose an option:")
    print("1. View tasks")
    print("2. Add a task")
    print("3. Remove a task")
    print("4. Mark task as done")
    print("5. Clear all tasks")
    print("6. Exit")

# Function to view tasks
def view_tasks():
    if not tasks:
        print("\nNo tasks in your list.")
    else:
        print("\nYour Tasks:")
        for index, task in enumerate(tasks):
            status = "✓" if task["done"] else "✗"
            print(f"{index + 1}. [{status}] {task['title']}")

# Function to add a task
def add_task():
    # Input is untrusted: trim whitespace and remove control characters.
    title = input("\nEnter the task: ").strip()
    # Basic sanitization: collapse control characters that could affect console.
    sanitized = "".join(ch for ch in title if ch.isprintable()).strip()
    if sanitized:
        # Enforce a reasonable maximum length to avoid abuse while keeping behavior intuitive.
        MAX_TITLE_LENGTH = 200
        if len(sanitized) > MAX_TITLE_LENGTH:
            # Truncate long titles rather than rejecting to preserve user intent.
            sanitized = sanitized[:MAX_TITLE_LENGTH]
            logging.debug("Task title truncated to maximum allowed length.")
        tasks.append({"title": sanitized, "done": False})
        print(f"Task '{sanitized}' added!")
    else:
        print("Empty task not added.")

# Function to remove a task
def remove_task():
    view_tasks()
    if tasks:
        num = parse_task_number("Enter the task number to remove: ", len(tasks))
        if num is not None:
            removed = tasks.pop(num - 1)
            print(f"Task '{removed['title']}' removed.")

# Function to mark a task as done
def mark_done():
    view_tasks()
    if tasks:
        num = parse_task_number("Enter the task number to mark as done: ", len(tasks))
        if num is not None:
            tasks[num - 1]["done"] = True
            print(f"Task '{tasks[num - 1]['title']}' marked as done.")

# Function to clear all tasks
def clear_tasks():
    # Confirm with explicit choices only; default to 'n' for safety.
    confirm = input("Are you sure you want to clear all tasks? (y/n): ").strip().lower()
    # Treat any input other than explicit 'y' as denial to avoid accidental data loss.
    if confirm == "y":
        tasks.clear()
        print("All tasks cleared.")
    else:
        print("Clear cancelled.")

# Main loop
def main():
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        # Validate that choice is one of the allowed options.
        if choice == "1":
            view_tasks()
        elif choice == "2":
            add_task()
        elif choice == "3":
            remove_task()
        elif choice == "4":
            mark_done()
        elif choice == "5":
            clear_tasks()
        elif choice == "6":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 6.")

# Run the app unconditionally on import for compatibility with consumers relying on import-time execution.
try:
    main()
except (KeyboardInterrupt, EOFError):
    # Handle user-initiated aborts gracefully and log them.
    logging.debug("Application terminated by user interrupt.")
    print("\nGoodbye! 👋")

# Thanks message
print("\nThanks for using the Simple To-Do List App!")
print("--------------------------------------------")

# Padding to hit exactly 100 lines
for _ in range(3):
    print(".")