import sys
import json
from pathlib import Path
import customtkinter as ctk
from datetime import datetime

PURPLE        = "#534AB7"
PURPLE_HOVER  = "#3C3489"
BG_CARD       = ("#0a0a0a", "#0a0a0a")
SIDEBAR_W     = 200
PREVIEW_CHARS = 120
WRAP          = 160

notes_folder = Path(__file__).parent / "files" / "notes"
notes_folder.mkdir(parents=True, exist_ok=True)

SAVE_FILE = "files/notes/notes.json"

class NotesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.pages         = []
        self.current       = None
        self.view          = "gallery"
        self.gallery_cards = []

        self.load_pages()
        self.build_sidebar()
        self.build_main()
        self.refresh_sidebar()
        self.show_gallery()
        self.after(0, self.bind_keys)

    def bind_keys(self):
        root = self.winfo_toplevel()
        self.kb_new = root.bind("<Control-n>", lambda _: self.new_page(), add="+")
        self.kb_del = root.bind("<Control-d>", lambda _: self.delete_page(), add="+")
        if sys.platform == "darwin":
            self._kb_new_mac = root.bind("<Command-n>", lambda _: self.new_page(), add="+")
            self._kb_del_mac = root.bind("<Command-d>", lambda _: self.delete_page(), add="+")
        self.bind("<Destroy>", self.unbind_keys)

    def unbind_keys(self, e):
        if e.widget is not self:
            return
        root = self.winfo_toplevel()
        root.unbind("<Control-n>", self.kb_new)
        root.unbind("<Control-d>", self.kb_del)
        if sys.platform == "darwin":
            root.unbind("<Command-n>", self._kb_new_mac)
            root.unbind("<Command-d>", self._kb_del_mac)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_W, corner_radius=0,
                                    fg_color=("white", "black"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 6))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hdr, text="Notes",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=("black", "white")).grid(
            row=0, column=0, padx=10, pady=3, sticky="w")
        ctk.CTkButton(hdr, text="+", width=28, height=28, corner_radius=8,
                      fg_color=PURPLE, hover_color=PURPLE_HOVER,
                      command=self.new_page).grid(row=0, column=1)

        self.page_list = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", corner_radius=0)
        self.page_list.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.page_list.grid_columnconfigure(0, weight=1)

        toggle = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        toggle.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 10))
        toggle.grid_columnconfigure((0, 1), weight=1)

        self.gallery_btn = ctk.CTkButton(
            toggle, text="⊞ Gallery", height=28, corner_radius=8,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=12), command=self.show_gallery)
        self.gallery_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.editor_btn = ctk.CTkButton(
            toggle, text="✎ Editor", height=28, corner_radius=8,
            fg_color="transparent", hover_color=("gray80", "gray25"),
            font=ctk.CTkFont(size=12),
            command=lambda: self.open_page(self.current) if self.current is not None else None)
        self.editor_btn.grid(row=0, column=1, padx=(3, 0), sticky="ew")

    def refresh_sidebar(self):
        for w in self.page_list.winfo_children():
            w.destroy()

        if not self.pages:
            ctk.CTkLabel(self.page_list, text="No pages yet",
                         text_color=("gray70", "gray60"),
                         font=ctk.CTkFont(size=12)).grid(row=0, column=0, pady=20)
            return

        for i, page in enumerate(self.pages):
            active = i == self.current and self.view == "editor"
            ctk.CTkButton(
                self.page_list,
                text=page["title"] or "Untitled",
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold" if active else "normal"),
                fg_color=PURPLE if active else "transparent",
                hover_color=PURPLE_HOVER if active else ("gray80", "gray25"),
                text_color="white" if active else ("gray75", "gray75"),
                corner_radius=8,
                command=lambda idx=i: self.open_page(idx)
            ).grid(row=i, column=0, sticky="ew", padx=4, pady=2)

    # ── Main area ─────────────────────────────────────────────────────────────

    def build_main(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()
        for r in range(5):
            self.main.grid_rowconfigure(r, weight=0)

    # ── Gallery view ──────────────────────────────────────────────────────────

    def load_pages(self):
        try:
            with open(SAVE_FILE, "r") as f:
                self.pages = json.load(f)
        except FileNotFoundError:
            self.pages = []

    def show_gallery(self):
        self.save_current()
        self.view = "gallery"
        self.update_toggle_buttons()
        self.clear_main()

        self.main.grid_rowconfigure(0, weight=0)
        self.main.grid_rowconfigure(1, weight=1)

        topbar = ctk.CTkFrame(self.main, fg_color="transparent")
        topbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(topbar, text="All Notes",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=("black", "white")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(topbar, text="+ New Note", width=100, height=32,
                      corner_radius=8, fg_color=PURPLE, hover_color=PURPLE_HOVER,
                      command=self.new_page).grid(row=0, column=1)

        if not self.pages:
            ctk.CTkLabel(self.main,
                         text="No notes yet — hit '+ New Note' to get started",
                         text_color=("gray40", "gray65")).grid(row=1, column=0, pady=60)
            return

        scroll = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        COLS = 3
        for c in range(COLS):
            scroll.grid_columnconfigure(c, weight=1)

        self.gallery_cards = [
            self.make_card(scroll, i, page, COLS)
            for i, page in enumerate(self.pages)
        ]

    def make_card(self, parent, i, page, cols):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                            cursor="hand2",
                            border_width=2 if i == self.current else 0,
                            border_color=PURPLE)
        card.grid(row=i // cols, column=i % cols, padx=6, pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(i // cols, weight=0)

        preview = page["body"][:PREVIEW_CHARS].strip() or "Empty page"
        if len(page["body"]) > PREVIEW_CHARS:
            preview += "…"
        words = len(page["body"].split()) if page["body"].strip() else 0

        rows = [
            (page["title"] or "Untitled",
             dict(font=ctk.CTkFont(size=13, weight="bold"),
                  text_color="white", anchor="w", pady=(12, 4))),
            (preview,
             dict(font=ctk.CTkFont(size=11),
                  text_color=("gray70", "gray60"),
                  anchor="nw", justify="left", pady=(0, 6))),
            (f"{page['created']}  •  {words}w",
             dict(font=ctk.CTkFont(size=10),
                  text_color=("gray65", "gray55"), anchor="w", pady=(0, 10))),
        ]
        for row, (text, kw) in enumerate(rows):
            pady = kw.pop("pady")
            ctk.CTkLabel(card, text=text, wraplength=WRAP, **kw).grid(
                row=row, column=0, padx=12, pady=pady, sticky="ew")

        for w in [card] + list(card.winfo_children()):
            w.bind("<Button-1>",        lambda _, idx=i: self.select_card(idx))
            w.bind("<Double-Button-1>", lambda _, idx=i: self.open_page(idx))

        return card

    def select_card(self, idx):
        self.current = idx
        for j, card in enumerate(self.gallery_cards):
            card.configure(border_width=2 if j == idx else 0)
        self.refresh_sidebar()

    # ── Editor view ───────────────────────────────────────────────────────────

    def build_editor_view(self):
        self.clear_main()
        self.view = "editor"
        self.update_toggle_buttons()

        self.main.grid_rowconfigure(0, weight=0)
        self.main.grid_rowconfigure(1, weight=0)
        self.main.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(self.main, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        toolbar.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(
            toolbar, placeholder_text="Page title…",
            font=ctk.CTkFont(size=16, weight="bold"), height=36)
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.title_entry.bind("<KeyRelease>", self.on_title_change)

        ctk.CTkButton(toolbar, text="🗑 Delete", width=88, height=36, fg_color="transparent",
                      border_width=1, border_color=("gray70", "gray35"), text_color=("#A32D2D", "#F09595"),
                      hover_color=("gray85", "gray20"), command=self.delete_page).grid(row=0, column=2)

        self.meta_label = ctk.CTkLabel(
            self.main, text="", anchor="w",
            font=ctk.CTkFont(size=11), text_color=("gray40", "gray65"))
        self.meta_label.grid(row=1, column=0, sticky="ew", padx=18, pady=(4, 6))

        self.body_box = ctk.CTkTextbox(
            self.main, font=ctk.CTkFont(family="Helvetica", size=14),
            corner_radius=10, wrap="word", activate_scrollbars=True)
        self.body_box.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.body_box.bind("<KeyRelease>", self.on_body_change)

    # ── Page actions ──────────────────────────────────────────────────────────

    def new_page(self):
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.pages.append({"title": "Untitled", "body": "", "created": now})
        self.open_page(len(self.pages) - 1)
        self.save_all()

    def open_page(self, idx):
        self.save_current()
        self.current = idx
        self.build_editor_view()
        page = self.pages[idx]
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, page["title"])
        self.body_box.delete("0.0", "end")
        self.body_box.insert("0.0", page["body"])
        self.update_meta()
        self.refresh_sidebar()

    def save_current(self):
        if self.current is None or self.current >= len(self.pages):
            return
        if self.view == "editor" and hasattr(self, "title_entry"):
            self.pages[self.current]["title"] = (
                self.title_entry.get().strip() or "Untitled")
            self.pages[self.current]["body"] = (
                self.body_box.get("0.0", "end").rstrip("\n"))

    def delete_page(self):
        if self.current is None:
            return
        self.pages.pop(self.current)
        self.current = None
        self.refresh_sidebar()
        self.show_gallery()
        self.save_all()

    def on_title_change(self, _=None):
        if self.current is None:
            return
        self.pages[self.current]["title"] = (
            self.title_entry.get().strip() or "Untitled")
        self.refresh_sidebar()
        self.save_all()

    def on_body_change(self, _=None):
        if self.current is None:
            return
        self.pages[self.current]["body"] = (
            self.body_box.get("0.0", "end").rstrip("\n"))
        self.update_meta()
        self.save_all()

    def update_meta(self):
        if self.current is None:
            return
        page  = self.pages[self.current]
        filename = f"{page['title']}.txt"
        note_file = notes_folder / filename
        note_file.write_text(page["body"])
        words = len(page["body"].split()) if page["body"].strip() else 0
        self.meta_label.configure(
            text=f"Created {page['created']}  •  "
                 f"{words} word{'s' if words != 1 else ''}")

    def update_toggle_buttons(self):
        if self.view == "gallery":
            self.gallery_btn.configure(fg_color=PURPLE, hover_color=PURPLE_HOVER)
            self.editor_btn.configure(fg_color="transparent")
        else:
            self.editor_btn.configure(fg_color=PURPLE, hover_color=PURPLE_HOVER)
            self.gallery_btn.configure(fg_color="transparent")

    # Define a function to save the note
    def save_all(self):
        with open(SAVE_FILE, "w") as f:
            json.dump(self.pages, f, indent=2)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Notes")
    root.geometry("860x580")
    root.minsize(680, 420)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    NotesFrame(root).grid(row=0, column=0, sticky="nsew")
    root.mainloop()
