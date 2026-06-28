import customtkinter as ctk
from calendar import PURPLE, PURPLE_HOVER, BG_CARD, primary_btn, danger_btn, scrollable
import animations


class TodoFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.tasks = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="To-Do List",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        inp = ctk.CTkFrame(self, fg_color="transparent")
        inp.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="ew")
        inp.grid_columnconfigure(0, weight=1)
        self.task_entry = ctk.CTkEntry(inp, placeholder_text="Add a task…", height=34)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.task_entry.bind("<Return>", lambda _: self.add_task())
        add_btn = primary_btn(inp, "+ Add", self.add_task, width=72)
        add_btn.grid(row=0, column=1)
        animations.click_pulse(add_btn)

        self.list_area = scrollable(self)
        self.list_area.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="nsew")
        self.list_area.grid_columnconfigure(0, weight=1)
        self.render_tasks()

    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            return
        self.tasks.append({"text": text, "done": False})
        self.task_entry.delete(0, "end")
        self.render_tasks()

    def toggle_task(self, idx):
        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        self.render_tasks()

    def delete_task(self, idx):
        self.tasks.pop(idx)
        self.render_tasks()

    def render_tasks(self):
        for w in self.list_area.winfo_children():
            w.destroy()

        if not self.tasks:
            ctk.CTkLabel(self.list_area, text="No tasks yet — add one above!",
                         text_color=("gray60", "gray50")).grid(row=0, column=0, pady=20)
            return

        pending = [t for t in self.tasks if not t["done"]]
        done    = [t for t in self.tasks if t["done"]]

        row_idx = 0
        for group_label, group in [("Pending", pending), ("Completed", done)]:
            if not group:
                continue
            ctk.CTkLabel(self.list_area, text=group_label.upper(),
                         font=ctk.CTkFont(size=10), text_color="gray50").grid(
                row=row_idx, column=0, sticky="w", padx=4, pady=(8, 2))
            row_idx += 1
            for task in group:
                real_idx = self.tasks.index(task)
                done_flag = task["done"]
                row = ctk.CTkFrame(self.list_area, fg_color=BG_CARD, corner_radius=8)
                row.grid(row=row_idx, column=0, sticky="ew", pady=2)
                row.grid_columnconfigure(1, weight=1)

                toggle_btn = ctk.CTkButton(
                    row,
                    text="✓" if done_flag else "○",
                    width=32, height=32, corner_radius=16,
                    fg_color=PURPLE if done_flag else "transparent",
                    hover_color=PURPLE_HOVER if done_flag else ("gray75", "gray35"),
                    text_color="white" if done_flag else ("gray10", "gray90"),
                    command=lambda i=real_idx: self.toggle_task(i)
                )
                toggle_btn.grid(row=0, column=0, padx=(8, 6), pady=6)
                animations.click_pulse(toggle_btn)

                ctk.CTkLabel(
                    row, text=task["text"], anchor="w",
                    font=ctk.CTkFont(size=13),
                    text_color=("gray55", "gray50") if done_flag else ("gray10", "gray90")
                ).grid(row=0, column=1, pady=6, sticky="ew")

                del_btn = danger_btn(row, "🗑", lambda i=real_idx: self.delete_task(i))
                del_btn.grid(row=0, column=2, padx=(0, 6))
                animations.click_pulse(del_btn)
                row_idx += 1
