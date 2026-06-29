import json
import customtkinter as ctk
from pathlib import Path
from events import PURPLE, PURPLE_HOVER, BG_CARD, primary_button, danger_button, scrollable

# Create File Path to save tasks if there is not already one
# This was instructed by ChatGPT
TODO_DIR = Path("files/todo")
TODO_DIR.mkdir(exist_ok=True)

# Note: I implemented the emojis because I thought they looked cool

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        # Load the tasks from the existing file path
        self.load_tasks()

        # Configure Rows & Columns
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create & Display Title
        ctk.CTkLabel(self, text="To-Do", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        # Create an input frame to add and display to-dos
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="ew")
        
        # Create to-do entry field
        self.task_entry = ctk.CTkEntry(input_frame, placeholder_text="Add a task…", height=34)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.task_entry.bind("<Return>", lambda _: self.add_task())

        # Create an 'Add' button to add more to-dos
        add_btn = primary_button(input_frame, "+ Add", self.add_task, width=72)
        add_btn.grid(row=0, column=1)

        # Create a scrollable list area
        self.list_area = scrollable(self)
        self.list_area.grid_columnconfigure(0, weight=1)
        self.list_area.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="nsew")

        # Render Tasks
        self.render_tasks()

    # Create a function to add tasks
    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            return
        self.tasks.append({"text": text, "done": False})
        self.task_entry.delete(0, "end")
        self.save_tasks()
        self.render_tasks()

    # Create a function to check whether tasks have been complete
    def toggle_task(self, idx):
        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        self.save_tasks()
        self.render_tasks()

    # Create a function to delete tasks
    def delete_task(self, idx):
        self.tasks.pop(idx)
        self.save_tasks()
        self.render_tasks()

    # Create a function to render the tasks on the frame
    # This was mostly instructed by Claude
    def render_tasks(self):
        # Clear all previously rendered task widgets before rebuilding
        for w in self.list_area.winfo_children():
            w.destroy()

        # Show empty state message if there are no tasks
        if not self.tasks:
            ctk.CTkLabel(self.list_area, text="No tasks yet — add one above!", text_color=("gray60", "gray50")).grid(row=0, column=0, pady=20)
            return

        # Separate tasks into two groups for display
        pending = [t for t in self.tasks if not t["done"]]
        done = [t for t in self.tasks if t["done"]]

        # Track which grid row to place the next widget in
        row_index = 0
        # Iterate over both groups in order: pending first, then completed
        for group_label, group in [("Pending", pending), ("Completed", done)]:
            # Skip the group entirely if it has no tasks
            if not group:
                continue
            # Render the section header label (e.g. "PENDING" or "COMPLETED")
            ctk.CTkLabel(self.list_area, text=group_label.upper(), font=ctk.CTkFont(size=10), text_color="gray50").grid(row=row_index, column=0, sticky="w", padx=4, pady=(8, 2))
            # Advance to the next row after the section header
            row_index += 1
            for task in group:
                # Get the task's position in the original list for toggle/delete callbacks
                real_index = self.tasks.index(task)
                # Cache the done state to avoid repeated dict lookups
                done_flag = task["done"]
                # Card frame that wraps the toggle button, label, and delete button
                row = ctk.CTkFrame(self.list_area, fg_color=BG_CARD, corner_radius=8)
                row.grid(row=row_index, column=0, sticky="ew", pady=2)
                # Task label column stretches to fill remaining space
                row.grid_columnconfigure(1, weight=1)

                # Filled circle when done
                toggle_button = ctk.CTkButton(row, text="✓" if done_flag else "○", width=32, height=32, corner_radius=16, fg_color=PURPLE if done_flag else "transparent",
                                           hover_color=PURPLE_HOVER if done_flag else ("gray75", "gray35"), text_color="white" if done_flag else ("gray10", "gray90"),
                                           command=lambda i=real_index: self.toggle_task(i))
                # Left side of the row
                toggle_button.grid(row=0, column=0, padx=(8, 6), pady=6)

                # Task text; greyed out when completed
                ctk.CTkLabel(row, text=task["text"], anchor="w", font=ctk.CTkFont(size=13),
                             text_color=("gray55", "gray50") if done_flag else ("gray10", "gray90")).grid(row=0, column=1, pady=6, sticky="ew")

                # Trash icon button to permanently remove the task
                delete_button = danger_button(row, "🗑", lambda i=real_index: self.delete_task(i))
                # Right side of the row
                delete_button.grid(row=0, column=2, padx=(0, 6))
                # Advance to the next row for the next task card
                row_index += 1

    # This was instructed by ChatGPT
    # Write tasks to the .json file
    def save_tasks(self):
        file = TODO_DIR/"todo.json"

        with open(file, "w") as f:
            json.dump(self.tasks, f, indent=4)

    # Open the .json file and load tasks
    def load_tasks(self):
        file = TODO_DIR/"todo.json"
        if file.exists():
            with open(file) as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []