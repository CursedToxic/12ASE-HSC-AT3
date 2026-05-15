import customtkinter as ctk
from event_planner import PURPLE, PURPLE_HOVER, primary_btn, danger_btn, scrollable
import animations


class NotesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.notes = []
        self.selected = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Notes",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 4), sticky="w")

        # Left sidebar
        left = ctk.CTkFrame(self, fg_color=("gray88", "gray17"), corner_radius=12)
        left.grid(row=1, column=0, padx=(20, 6), pady=(0, 16), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)
        left.configure(width=170)

        new_note_btn = primary_btn(left, "+ New Note", self.new_note)
        new_note_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        animations.click_pulse(new_note_btn)

        self.note_list = scrollable(left)
        self.note_list.grid(row=1, column=0, padx=6, pady=(0, 10), sticky="nsew")
        self.note_list.grid_columnconfigure(0, weight=1)

        # Right editor
        right = ctk.CTkFrame(self, fg_color=("gray88", "gray17"), corner_radius=12)
        right.grid(row=1, column=1, padx=(0, 20), pady=(0, 16), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self.title_entry = ctk.CTkEntry(
            right, placeholder_text="Note title…",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=36, fg_color="transparent", border_width=0)
        self.title_entry.grid(row=0, column=0, padx=14, pady=(12, 0), sticky="ew")

        self.content_box = ctk.CTkTextbox(
            right, wrap="word", font=ctk.CTkFont(size=13), fg_color="transparent")
        self.content_box.grid(row=1, column=0, padx=10, pady=4, sticky="nsew")

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        save_btn = primary_btn(btn_row, "Save", self.save_note)
        save_btn.grid(row=0, column=0, sticky="w")
        animations.click_pulse(save_btn)
        self.delete_btn = danger_btn(btn_row, "Delete Note", self.delete_selected, width=90)
        self.delete_btn.grid(row=0, column=1)
        animations.click_pulse(self.delete_btn)

        self._set_editor_state("disabled")
        self.render_note_list()

    def _set_editor_state(self, state):
        self.title_entry.configure(state=state)
        self.content_box.configure(state=state)
        self.delete_btn.configure(state=state)

    def new_note(self):
        self.notes.append({"title": "Untitled Note", "content": ""})
        self.selected = len(self.notes) - 1
        self.render_note_list()
        self.load_note(self.selected)

    def select_note(self, idx):
        self.selected = idx
        self.render_note_list()
        self.load_note(idx)

    def load_note(self, idx):
        self._set_editor_state("normal")
        note = self.notes[idx]
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note["title"])
        self.content_box.delete("1.0", "end")
        self.content_box.insert("1.0", note["content"])

    def save_note(self):
        if self.selected is None:
            return
        title = self.title_entry.get().strip() or "Untitled Note"
        self.notes[self.selected]["title"] = title
        self.notes[self.selected]["content"] = self.content_box.get("1.0", "end-1c")
        self.render_note_list()

    def delete_selected(self):
        if self.selected is None:
            return
        self.notes.pop(self.selected)
        self.selected = None
        self._set_editor_state("normal")
        self.title_entry.delete(0, "end")
        self.content_box.delete("1.0", "end")
        self._set_editor_state("disabled")
        self.render_note_list()

    def render_note_list(self):
        for w in self.note_list.winfo_children():
            w.destroy()
        if not self.notes:
            ctk.CTkLabel(self.note_list, text="No notes yet",
                         text_color=("gray60", "gray50"),
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, pady=10)
            return
        for i, note in enumerate(self.notes):
            is_sel = i == self.selected
            btn = ctk.CTkButton(
                self.note_list,
                text=note["title"] or "Untitled Note",
                anchor="w",
                fg_color=PURPLE if is_sel else "transparent",
                hover_color=PURPLE_HOVER if is_sel else ("gray80", "gray30"),
                text_color="white" if is_sel else ("gray10", "gray90"),
                font=ctk.CTkFont(size=12),
                command=lambda idx=i: self.select_note(idx)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=1)
            animations.click_pulse(btn)
