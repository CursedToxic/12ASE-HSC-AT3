import sys
import json
from pathlib import Path
import customtkinter as ctk
import calendar
from datetime import *

# Primary, Hover, Background Colours
PURPLE       = "#534AB7"
PURPLE_HOVER = "#3C3489"
BG_CARD      = ("gray85", "gray20")

# This was as instructed by ChatGPT
# Setup the directory where files are stored
EVENT_DIR = Path("files/events")
# Create it if it doesn't exist
EVENT_DIR.mkdir(exist_ok=True)

# This was as instructed from Claude
# Solid purple button used for primary actions (e.g. "+ Add")
def primary_btn(parent, text, command, width=100):
    return ctk.CTkButton(parent, text=text, command=command, fg_color=PURPLE, hover_color=PURPLE_HOVER, font=ctk.CTkFont(size=13), width=width)

# Transparent button with red text used for destructive actions (e.g. delete)
def danger_btn(parent, text, command, width=32):
    return ctk.CTkButton(parent, text=text, command=command, fg_color="transparent", hover_color=("gray80", "gray30"),
                        text_color=("#A32D2D", "#F09595"), font=ctk.CTkFont(size=12), width=width)

# Transparent scrollable frame used as a container for lists
def scrollable(parent):
    return ctk.CTkScrollableFrame(parent, fg_color="transparent")

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        # Stores events as {date_key: [event_strings]}
        self.events = {}
        # Populate self.events from disk on startup
        self.load_events()
        # The date the user has clicked; None until first click
        self.selected_date = None
        # Controls which month is displayed
        self.current_date = datetime.now()

        # Month label + navigation buttons
        self.build_header()
        # Calendar grid + events panel
        self.build_main()
        # Fill the grid with day numbers
        self.display_month()
        # Deferred so winfo_toplevel() is valid
        self.after(0, self.bind_keys)

    # This was instructed by Claude
    def bind_keys(self):
        # Get the top-level window to bind globally
        root = self.winfo_toplevel()
        # Previous month, next month, jump to today; add="+" preserves existing bindings
        self.left  = root.bind("<Left>",      lambda _: self.change_month(-1), add="+")
        self.right = root.bind("<Right>",     lambda _: self.change_month(1),  add="+")
        self.today = root.bind("<Control-t>", lambda _: self.go_to_today(),    add="+")

        # For MacOS
        if sys.platform == "darwin":
            self.today_mac = root.bind("<Command-t>", lambda _: self.go_to_today(), add="+")

        # Clean up when frame is removed
        self.bind("<Destroy>", self.unbind_keys)
    
    # Instructed by Claude: Undinding Keybinds
    def unbind_keys(self, e):
        # <Destroy> fires for every child widget; only act on the frame itself
        if e.widget is not self:
            return
        # Get root window to remove bindings from
        root = self.winfo_toplevel()
        # Remove left-arrow binding
        root.unbind("<Left>", self.left)
        # Remove right-arrow binding
        root.unbind("<Right>", self.right)
        # Remove today shortcut
        root.unbind("<Control-t>", self.today)
        # Remove macOS today shortcut
        if sys.platform == "darwin":
            root.unbind("<Command-t>", self.today_mac)

    def key(self, d=None):
        # Dict key format for events storage
        return (d or self.selected_date).strftime("%Y-%m-%d")

    def refresh(self):
        # Display Monty
        self.display_month()
        # Render Events
        self.render_events()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        # Span full width at the top
        header.pack(fill="x", padx=20, pady=(16, 8))
        # Month label takes all spare horizontal space
        header.grid_columnconfigure(1, weight=1)

        self.prev_button = ctk.CTkButton(header, text="◀", width=50, font=ctk.CTkFont(size=16, weight="bold"), command=lambda: self.change_month(-1),
                                      fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=12)
        # Place the previous button in the top left
        self.prev_button.grid(row=0, column=0, padx=(0, 10))

        self.month_year_label = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=20, weight="bold"))
        # Centred; text set in display_month()
        self.month_year_label.grid(row=0, column=1)

        # Outlined ghost button: Instructed by Claude
        ctk.CTkButton(header, text="Today", width=72, font=ctk.CTkFont(size=13), command=self.go_to_today, fg_color="transparent", hover_color=("gray80", "gray25"),
                      border_width=1, border_color=("gray60", "gray40"), corner_radius=12).grid(row=0, column=2, padx=(0, 8))

        self.next_button = ctk.CTkButton(header, text="▶", width=50, font=ctk.CTkFont(size=16, weight="bold"), command=lambda: self.change_month(1),
                                      fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=12)
        # Place next button in the top right
        self.next_button.grid(row=0, column=3, padx=(0, 0))

    def build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        # Create a frame to fill remaining window space
        main.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        
        # Single row expands vertically
        main.grid_rowconfigure(0, weight=1)
        # Configure Columns
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)

        # Frame for calendar
        self.calendar_frame = ctk.CTkFrame(main, fg_color="transparent")
        # Place Frame
        self.calendar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Configure Uniform Columns
        for c in range(7):
            self.calendar_frame.grid_columnconfigure(c, weight=1, uniform="days")
        # Configure Rows
        for r in range(7):
            self.calendar_frame.grid_rowconfigure(r, weight=1)

        # Display Day
        for col, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            ctk.CTkLabel(self.calendar_frame, text=day, font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray50", "gray55")).grid(row=0, column=col, padx=2, pady=4, sticky="ew")

        # Instructed by Claude: Create buttons for each day in calendar
        self.date_buttons = [
            [ctk.CTkButton(self.calendar_frame, text="", font=ctk.CTkFont(size=13), fg_color=BG_CARD, hover_color=PURPLE_HOVER, corner_radius=8, command=lambda: None) for _ in range(7)]
            for _ in range(6)]

        # Row+1 to leave row 0 for headers
        for r, week in enumerate(self.date_buttons):
            for c, btn in enumerate(week):
                btn.grid(row=r + 1, column=c, padx=2, pady=2, sticky="nsew")

        # Events panel (right)
        self.event_area = ctk.CTkFrame(main, fg_color="transparent")
        # Placed at column 2 (weight set above)
        self.event_area.grid(row=0, column=2, sticky="nsew")
        # Single column fills full width
        self.event_area.grid_columnconfigure(0, weight=1)
        # Row 2 (event list) expands vertically
        self.event_area.grid_rowconfigure(2, weight=1)

        # Build initial events panel before any date is selected
        self.render_events()

    def display_month(self):
        # Configure month text
        self.month_year_label.configure(text=self.current_date.strftime("%B %Y"))

        year = self.current_date.year
        month = self.current_date.month
        # Initialise Calendar
        cal = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
        # Obtain current datetime
        today = datetime.now()

        for week_idx in range(6):
            # Pad short months to always have 6 rows
            week = cal[week_idx] if week_idx < len(cal) else [0] * 7
            for day_idx, day in enumerate(week):
                btn = self.date_buttons[week_idx][day_idx]
                if day == 0:
                    # Empty cell for days outside the month
                    btn.configure(text="", state="disabled", fg_color="transparent", border_width=0)
                else:
                    # Full datetime for this cell
                    date_obj = datetime(year, month, day)
                    # "YYYY-MM-DD" string for dict lookup
                    key      = self.key(date_obj)
                    # True only for the actual current day
                    is_today = (day == today.day and month == today.month
                                and year == today.year)
                    # True if this cell matches the user's selection
                    selected   = (self.selected_date is not None
                                and self.key() == key)
                    # Colour priority: today > selected > normal
                    fg = PURPLE if is_today else (PURPLE_HOVER if selected else BG_CARD)
                    # Bullet dot indicates events exist; d=date_obj captures loop variable
                    btn.configure(text=f"{day}\n●" if self.events.get(key) else str(day), state="normal", fg_color=fg, border_width=2 if selected else 0, border_color=PURPLE,
                                  command=lambda d=date_obj: self.select_date(d))

    def change_month(self, delta):
        # Raw new month
        m = self.current_date.month + delta
        # Roll year forward/back on month overflow
        y = self.current_date.year + (m - 1) // 12
        # Wrap month into 1-12
        self.current_date = self.current_date.replace(year=y, month=(m - 1) % 12 + 1)
        # Persist before redrawing in case of crash
        self.save_events()
        # Redraw calendar and events panel
        self.refresh()

    def go_to_today(self):
        # Switch displayed month to the current one
        self.current_date = datetime.now()
        # Also select today so events panel opens immediately
        self.selected_date = self.current_date
        self.refresh()

    def select_date(self, date_obj):
        # Store the clicked date
        self.selected_date = date_obj
        # Update highlight and events panel
        self.refresh()

    def add_event(self):
        # Read and trim the entry field
        text = self.event_entry.get().strip()
        if not text or not self.selected_date:
            # Silently ignore if input is empty or no date selected
            return
        # Create list for date if it doesn't exist, then append
        self.events.setdefault(self.key(), []).append(text)
        # Clear the input field after adding
        self.event_entry.delete(0, "end")
        # Write to disk immediately
        self.save_events()
        # Redraw to show the new event
        self.refresh()

    def delete_event(self, key, idx):
        # Remove the event at the given index
        self.events[key].pop(idx)
        if not self.events[key]:
            # Remove the date entry entirely if no events remain
            del self.events[key]
        # Persist the deletion
        self.save_events()
        # Redraw to remove the deleted row
        self.refresh()

    def render_events(self):
        for w in self.event_area.winfo_children():
            # Clear previous widgets before rebuilding the panel
            w.destroy()

        # Show full date when selected
        header_text = (self.selected_date.strftime("Events — %B %d, %Y") if self.selected_date else "Events")
        ctk.CTkLabel(self.event_area, text=header_text, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))

        input = ctk.CTkFrame(self.event_area, fg_color="transparent")
        # Input row sits below the header
        input.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        # Entry field stretches; button stays fixed
        input.grid_columnconfigure(0, weight=1)

        # Controls placeholder text and disabled state
        has_day = bool(self.selected_date)
        self.event_entry = ctk.CTkEntry(input, height=34, placeholder_text="Add event…" if has_day else "Select a day first", state="normal" if has_day else "disabled")
        # Fills available width
        self.event_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        # Enter key submits the event
        self.event_entry.bind("<Return>", lambda _: self.add_event())

        add_btn = primary_btn(input, "+ Add", self.add_event, width=72)
        # Greyed out until a date is selected
        add_btn.configure(state="normal" if has_day else "disabled")
        add_btn.grid(row=0, column=1)

        if not has_day:
            # Placeholder when no date selected
            ctk.CTkLabel(self.event_area, text="Select a day to view events", text_color=("gray60", "gray50")).grid(row=2, column=0, pady=8)
            return

        # Fetch events for the selected date (empty list if none)
        evs = self.events.get(self.key(), [])
        if not evs:
            # Empty state message
            ctk.CTkLabel(self.event_area, text="No events for this day", text_color=("gray60", "gray50")).grid(row=2, column=0, pady=8)
            return

        # Scrollable container for the event rows
        event_list = scrollable(self.event_area)
        # Fills the remaining panel space
        event_list.grid(row=2, column=0, sticky="nsew")
        # Event label stretches; delete button stays fixed
        event_list.grid_columnconfigure(0, weight=1)
        # Snapshot key so lambda captures correct value
        key = self.key()
        for i, ev in enumerate(evs):
            # Card for each event
            row_frame = ctk.CTkFrame(event_list, fg_color=BG_CARD, corner_radius=8)
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)

            # Event text, left-aligned
            ctk.CTkLabel(row_frame, text=f"• {ev}", anchor="w", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=6, sticky="ew")
            # k=key, idx=i captures loop variables
            danger_btn(row_frame, "🗑", lambda k=key, idx=i: self.delete_event(k, idx)).grid(row=0, column=1, padx=(0, 6))

    def load_events(self):
        # Resolve path to the JSON file
        file = self.events_file()

        if file.exists():
            with open(file, "r") as f:
                # Load saved events into memory
                self.events = json.load(f)
        else:
            # Start fresh if no file exists yet
            self.events = {}

    def save_events(self):
        with open(self.events_file(), "w") as f:
            # Pretty-print JSON for readability
            json.dump(self.events, f, indent=4)

    def events_file(self):
        # Single shared file for all events
        return EVENT_DIR / "events.json"
