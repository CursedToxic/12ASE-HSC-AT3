import os
import sys
import json
import uuid
from pathlib import Path
import customtkinter as ctk
from datetime import datetime

# Global Variables:
# Main Colour
PURPLE = "#534AB7"
# Hoever Colour
PURPLE_HOVER = "#3C3489"
# Background for Cards
BG_CARD = ("#0a0a0a", "#0a0a0a")
# Sidebar Width
SIDEBAR_W = 200
# Note Preview Length in Gallery
PREVIEW_CHARS = 120
# Wrap width for labels
WRAP = 160

# Followed ChatGPT's instructions
# Notes folder directory
notes_folder = Path(__file__).parent / "files" / "notes"
# Create directory if not exists
notes_folder.mkdir(parents=True, exist_ok=True)

# Note database file
SAVE_FILE = "files/notes/notes.json"

# Important Note: Emojis were from the original code from Claude. I've left them in because I like how they look :)

# Frame for Notes
class NotesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        # Configure Rows and Columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Load saved notes from disk: Instructed by ChatGPT
        self.load_pages()
        # Currently selected note index
        self.current = None
        # Set view mode when app is opened
        self.view = "gallery"
        # List for storing cards
        self.gallery_cards = []

        # Run functions to create UI
        self.build_sidebar()
        self.build_main()
        self.refresh_sidebar()
        self.show_gallery()

        # Keybinds after UI is loaded: Instructions from Claude
        self.after(0, self.bind_keys)

    # Keybind Setup: Claude instructed me on how to do this
    def bind_keys(self):
        # Returns the root window
        root = self.winfo_toplevel()
        # New Note
        self.kb_new = root.bind("<Control-n>", lambda _: self.new_page(), add="+")
        # Delete Note
        self.kb_del = root.bind("<Control-d>", lambda _: self.delete_page(), add="+")\
        # For MacOS
        if sys.platform == "darwin":
            self._kb_new_mac = root.bind("<Command-n>", lambda _: self.new_page(), add="+")
            self._kb_del_mac = root.bind("<Command-d>", lambda _: self.delete_page(), add="+")
        # Remove keybinds when closed
        self.bind("<Destroy>", self.unbind_keys)

    def unbind_keys(self, e):
        # Ensure we are unbinding from notes and not calendar, for example
        if e.widget is not self:
            return
        root = self.winfo_toplevel()

        # Undind Hotkeys
        root.unbind("<Control-n>", self.kb_new)
        root.unbind("<Control-d>", self.kb_del)
        # For MacOS
        if sys.platform == "darwin":
            root.unbind("<Command-n>", self._kb_new_mac)
            root.unbind("<Command-d>", self._kb_del_mac)

    # Build the mainframe (actually just creates a frame for everything, but 'build the mainframe' sounded cooler)
    def build_main(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        
        # Configure row and columns
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        
        # Place the mainframe
        self.main.grid(row=0, column=1, sticky="nsew")

    # Create Sidebar
    def build_sidebar(self):
        # Establish Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_W, corner_radius=0, fg_color=("white", "black"))
        # Display Sidebar on the left
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        # Lock Sidebar Width: This was instructed by Claude, so that the interface stayed clean
        self.sidebar.grid_propagate(False)

        # Configure rows and columns
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Create frame for header, configure its position, then finally place the frame
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid_columnconfigure(0, weight=1)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 6))
        
        # Notes Title
        ctk.CTkLabel(header, text="Notes", font=ctk.CTkFont(size=18, weight="bold"), text_color=("black", "white")).grid(row=0, column=0, padx=10, pady=3, sticky="w")
        ctk.CTkButton(header, text="+", width=28, height=28, corner_radius=8, fg_color=PURPLE, hover_color=PURPLE_HOVER, command=self.new_page).grid(row=0, column=1)

        # Create a Scrollable Frame to view all note in Gallery Mode
        self.page_list = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0)\
        # Configure position
        self.page_list.grid_columnconfigure(0, weight=1)
        # Place the frame
        self.page_list.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        
        # Same for view switcher frame
        toggle = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        toggle.grid_columnconfigure((0, 1), weight=1)
        toggle.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 10))
        
        # Gallery View Button
        self.gallery_btn = ctk.CTkButton(toggle, text="⊞ Gallery", height=28, corner_radius=8, fg_color=PURPLE, hover_color=PURPLE_HOVER, font=ctk.CTkFont(size=12), command=self.show_gallery)
        self.gallery_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        
        # Editor View Button: After the command kwarg: I followed Claude's instructions open the page
        self.editor_btn = ctk.CTkButton(toggle, text="✎ Editor", height=28, corner_radius=8, fg_color="transparent", hover_color=("gray80", "gray25"), font=ctk.CTkFont(size=12),
            command=lambda: self.open_page(self.current) if self.current is not None else None)
        self.editor_btn.grid(row=0, column=1, padx=(3, 0), sticky="ew")

    # Create the editor view
    def build_editor_view(self):
        # Clear the mainframe
        self.clear_main()
        # Switch the view to editor
        self.view = "editor"
        # Update the state of the toggle buttons (highlights editor)
        self.update_toggle_buttons()

        # Configure rows
        self.main.grid_rowconfigure(0, weight=0)
        self.main.grid_rowconfigure(1, weight=0)
        self.main.grid_rowconfigure(2, weight=1)

        # Create toolbar
        toolbar = ctk.CTkFrame(self.main, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        toolbar.grid_columnconfigure(0, weight=1)

        # Create spot to insert title
        self.title_entry = ctk.CTkEntry(toolbar, font=ctk.CTkFont(size=16, weight="bold"), height=36)
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        # Claude instructed me to do this: update title on every keystroke
        self.title_entry.bind("<KeyRelease>", self.on_title_change)
        
        # Create and display a 'delete' button
        ctk.CTkButton(toolbar, text="🗑 Delete", width=88, height=36, fg_color="transparent", border_width=1, border_color=("gray70", "gray35"), text_color=("#A32D2D", "#F09595"),
                      hover_color=("gray85", "gray20"), command=self.delete_page).grid(row=0, column=2)

        # Create label space to display note information
        self.data_label = ctk.CTkLabel(self.main, text="", anchor="w", font=ctk.CTkFont(size=11), text_color=("gray40", "gray65"))
        self.data_label.grid(row=1, column=0, sticky="ew", padx=18, pady=(4, 6))

        # Instructed from Claude: Use CTkTextbox to create a textbox, this acts as the note.
        self.body_box = ctk.CTkTextbox(self.main, font=ctk.CTkFont(family="Helvetica", size=14), corner_radius=10, wrap="word", activate_scrollbars=True)
        self.body_box.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.body_box.bind("<KeyRelease>", self.on_body_change)

    # Refresh sidebar to ensure responsive UI
    def refresh_sidebar(self):
        # Destroy everything
        for w in self.page_list.winfo_children():
            w.destroy()

        # If no notes have been created, insert generic text to indicate there are no notes
        if not self.notes:
            ctk.CTkLabel(self.page_list, text="No notes yet", text_color=("gray70", "gray60"), font=ctk.CTkFont(size=12)).grid(row=0, column=0, pady=20)
            return

        # Create and display a button in the sidebar for each individual note: Claude helped me with the theming.
        for i, page in enumerate(self.notes):
            active = i == self.current and self.view == "editor"
            ctk.CTkButton(self.page_list, text=page["title"] or "Untitled", anchor="w", font=ctk.CTkFont(size=13, weight="bold" if active else "normal"),
                          fg_color=PURPLE if active else "transparent", hover_color=PURPLE_HOVER if active else ("gray80", "gray25"), text_color="white" if active else ("gray75", "gray75"),
                          corner_radius=8, command=lambda idx=i: self.open_page(idx)).grid(row=i, column=0, sticky="ew", padx=4, pady=2)

    # Clear the mainframe (actually just clears the frame when the view is switched)
    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()
        # Reconfigure rows
        for r in range(5):
            self.main.grid_rowconfigure(r, weight=0)

    # Show the gallery view
    def show_gallery(self):
        # Save current note
        self.save_current()
        # Switch View
        self.view = "gallery"
        # Update toggle buttons
        self.update_toggle_buttons()
        # Clear mainframe
        self.clear_main()

        # Reconfigure rows
        self.main.grid_rowconfigure(0, weight=0)
        self.main.grid_rowconfigure(1, weight=1)

        # Configure a topbar, then display it
        topbar = ctk.CTkFrame(self.main, fg_color="transparent")
        topbar.grid_columnconfigure(0, weight=1)
        topbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        
        # Create an 'All Notes' label
        ctk.CTkLabel(topbar, text="All Notes", font=ctk.CTkFont(size=18, weight="bold"), text_color=("black", "white")).grid(row=0, column=0, sticky="w")
        # Add new note
        ctk.CTkButton(topbar, text="+ New Note", width=100, height=32, corner_radius=8, fg_color=PURPLE, hover_color=PURPLE_HOVER, command=self.new_page).grid(row=0, column=1)

        # If no notes, create a label for the user to create a note
        if not self.notes:
            ctk.CTkLabel(self.main, text="No notes yet — hit '+ New Note' to get started", text_color=("gray40", "gray65")).grid(row=1, column=0, pady=60)
            return

        # Scrollable container that holds all gallery cards
        notes_scoll = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        notes_scoll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        COLS = 3
        # Give each column equal weight so cards stretch to fill the width
        for c in range(COLS):
            notes_scoll.grid_columnconfigure(c, weight=1)

        # Build one card widget per note and store references for later updates
        self.gallery_cards = [
            self.make_card(notes_scoll, i, page, COLS)
            for i, page in enumerate(self.notes)
        ]

    def make_card(self, parent, i, page, cols):
        # Dark card frame; pointer cursor signals it is clickable
        # Purple border on the currently selected card, none otherwise
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                            cursor="hand2",
                            border_width=2 if i == self.current else 0,
                            border_color=PURPLE)
        # Place card in the correct row/column using integer division and modulo
        card.grid(row=i // cols, column=i % cols, padx=6, pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        # Prevent rows from growing taller than their content
        parent.grid_rowconfigure(i // cols, weight=0)

        # Truncate the body to the preview character limit
        preview = page["body"][:PREVIEW_CHARS].strip() or "Empty page"
        # Add an ellipsis if the body was cut short
        if len(page["body"]) > PREVIEW_CHARS:
            preview += "…"
        # Count words only when the body has non-whitespace content
        words = len(page["body"].split()) if page["body"].strip() else 0

        # Each entry is (display text, label keyword args including a custom pady key)
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
            # Pop pady before passing kw to CTkLabel (it is not a valid CTkLabel param)
            pady = kw.pop("pady")
            ctk.CTkLabel(card, text=text, wraplength=WRAP, **kw).grid(
                row=row, column=0, padx=12, pady=pady, sticky="ew")

        # Bind clicks on the card frame and all its child labels
        for w in [card] + list(card.winfo_children()):
            # Single click selects the card (highlights border)
            w.bind("<Button-1>",        lambda _, idx=i: self.select_card(idx))
            # Double click opens the note in the editor
            w.bind("<Double-Button-1>", lambda _, idx=i: self.open_page(idx))

        return card

    def select_card(self, idx):
        # Track which card is selected
        self.current = idx
        # Redraw all card borders: only the selected one gets a purple outline
        for j, card in enumerate(self.gallery_cards):
            card.configure(border_width=2 if j == idx else 0)
        self.refresh_sidebar()

    # ChatGPT instructed me for this function: it loads the page
    def load_pages(self):
        # If note exists, load note, otherwise, create blank note
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                self.notes = json.load(f)
        else:
            self.notes = []

    def new_page(self):
        # Timestamp string shown in the editor footer
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")

        # Append a blank note with a unique ID and the current timestamp
        self.notes.append({
            "id": str(uuid.uuid4()),
            "title": "Untitled",
            "body": "",
            "created": now
        })

        # Persist so the new note survives a crash before editing begins
        self.save_pages()
        # Open the note that was just added (last in the list)
        self.open_page(len(self.notes) - 1)

    def open_page(self, idx):
        # Flush any unsaved edits from the previously open note
        self.save_current()
        # Track which note is currently being edited
        self.current = idx
        # Switch the right panel to editor layout
        self.build_editor_view()
        page = self.notes[idx]
        # Clear stale content before inserting the new note's title
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, page["title"])
        # Clear stale content before inserting the new note's body
        self.body_box.delete("0.0", "end")
        self.body_box.insert("0.0", page["body"])
        # Refresh the word count and created-date footer
        self.update_data()
        # Highlight the active note in the sidebar
        self.refresh_sidebar()

    def delete_page(self):
        # Nothing to delete if no note is open
        if self.current is None:
            return

        self.notes.pop(self.current)
        self.save_pages()

        # No note is open after deletion
        self.current = None
        self.refresh_sidebar()
        # Return to the gallery so the user sees the remaining notes
        self.show_gallery()

    def on_title_change(self, _=None):
        # Ignore keystrokes that fire before a note is open
        if self.current is None:
            return

        # Fall back to "Untitled" if the field is cleared
        self.notes[self.current]["title"] = (self.title_entry.get().strip() or "Untitled")

        # Update the sidebar card to reflect the new title immediately
        self.refresh_sidebar()
        self.save_pages()

    def on_body_change(self, _=None):
        if self.current is None:
            return
        # Strip the trailing newline that CTkTextbox always appends
        self.notes[self.current]["body"] = (self.body_box.get("0.0", "end").rstrip("\n"))
        # Recalculate word count shown in the footer
        self.update_data()
        self.save_pages()

    def update_data(self):
        if self.current is None:
            return
        page  = self.notes[self.current]
        # Derive the .txt filename from the note title
        filename = f"{page['title']}.txt"
        note_file = notes_folder / filename
        # Mirror the body to a plain-text file for external access
        note_file.write_text(page["body"])
        # Avoid counting whitespace-only content as words
        words = len(page["body"].split()) if page["body"].strip() else 0
        # Update footer label with creation date and live word count
        self.data_label.configure(text=f"Created {page['created']}  •  " f"{words} word{'s' if words != 1 else ''}")

    def update_toggle_buttons(self):
        # Highlight the active view button and reset the inactive one
        if self.view == "gallery":
            self.gallery_btn.configure(fg_color=PURPLE, hover_color=PURPLE_HOVER)
            self.editor_btn.configure(fg_color="transparent")
        else:
            self.editor_btn.configure(fg_color=PURPLE, hover_color=PURPLE_HOVER)
            self.gallery_btn.configure(fg_color="transparent")

    def save_pages(self):
        # Overwrite the JSON file with the current in-memory notes list
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, indent=2)

    def save_current(self):
            # Nothing to save if no note is open or the list has shrunk
            if self.current is None or self.current >= len(self.notes):
                return
            # Only read the widgets if the editor view has been built
            if self.view == "editor" and hasattr(self, "title_entry"):
                self.notes[self.current]["title"] = (
                    self.title_entry.get().strip() or "Untitled")
                self.notes[self.current]["body"] = (
                    self.body_box.get("0.0", "end").rstrip("\n"))