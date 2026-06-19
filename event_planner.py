import sys
import customtkinter as ctk
import calendar
from datetime import *
import animations

PURPLE       = "#534AB7"
PURPLE_HOVER = "#3C3489"
BG_CARD      = ("gray85", "gray20")

def primary_btn(parent, text, command, width=100):
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color=PURPLE, hover_color=PURPLE_HOVER,
                         font=ctk.CTkFont(size=13), width=width)

def danger_btn(parent, text, command, width=32):
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color="transparent", hover_color=("gray80", "gray30"),
                         text_color=("#A32D2D", "#F09595"),
                         font=ctk.CTkFont(size=12), width=width)

def scrollable(parent):
    return ctk.CTkScrollableFrame(parent, fg_color="transparent")

# ─── Calendar ─────────────────────────────────────────────────────────────────

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.events       = {}
        self.selected_date = None
        self.current_date = datetime.now()

        self.build_header()
        self.build_main()
        self.display_month()
        self.after(0, self.bind_keys)

    def bind_keys(self):
        root = self.winfo_toplevel()
        self._kb_left  = root.bind("<Left>",      lambda _: self.change_month(-1), add="+")
        self._kb_right = root.bind("<Right>",     lambda _: self.change_month(1),  add="+")
        self._kb_today = root.bind("<Control-t>", lambda _: self.go_to_today(),    add="+")
        if sys.platform == "darwin":
            self._kb_today_mac = root.bind("<Command-t>", lambda _: self.go_to_today(), add="+")
        self.bind("<Destroy>", self.unbind_keys)

    def unbind_keys(self, e):
        if e.widget is not self:
            return
        root = self.winfo_toplevel()
        root.unbind("<Left>",      self._kb_left)
        root.unbind("<Right>",     self._kb_right)
        root.unbind("<Control-t>", self._kb_today)
        if sys.platform == "darwin":
            root.unbind("<Command-t>", self._kb_today_mac)

    # ── helpers ───────────────────────────────────────────────────────────────

    def key(self, d=None):
        return (d or self.selected_date).strftime("%Y-%m-%d")

    def refresh(self):
        self.display_month()
        self.render_events()

    # ── layout ────────────────────────────────────────────────────────────────

    def build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 8))
        hdr.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            hdr, text="◀", width=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda: self.change_month(-1),
            fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=12)
        self.prev_btn.grid(row=0, column=0, padx=(0, 10))

        self.month_year_label = ctk.CTkLabel(
            hdr, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.month_year_label.grid(row=0, column=1)

        ctk.CTkButton(
            hdr, text="Today", width=72,
            font=ctk.CTkFont(size=13),
            command=self.go_to_today,
            fg_color="transparent", hover_color=("gray80", "gray25"),
            border_width=1, border_color=("gray60", "gray40"),
            corner_radius=12).grid(row=0, column=2, padx=(0, 8))

        self.next_btn = ctk.CTkButton(
            hdr, text="▶", width=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda: self.change_month(1),
            fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=12)
        self.next_btn.grid(row=0, column=3, padx=(0, 0))

    def build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        # Calendar grid (left)
        self.calendar_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.calendar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        for c in range(7):
            self.calendar_frame.grid_columnconfigure(c, weight=1, uniform="days")
        for r in range(7):
            self.calendar_frame.grid_rowconfigure(r, weight=1)

        for col, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            ctk.CTkLabel(self.calendar_frame, text=day,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=("gray50", "gray55")).grid(
                row=0, column=col, padx=2, pady=4, sticky="ew")

        self.date_buttons = [
            [ctk.CTkButton(self.calendar_frame, text="",
                           font=ctk.CTkFont(size=13),
                           fg_color=BG_CARD, hover_color=PURPLE_HOVER, corner_radius=8,
                           command=lambda: None)
             for _ in range(7)]
            for _ in range(6)
        ]
        for r, week in enumerate(self.date_buttons):
            for c, btn in enumerate(week):
                btn.grid(row=r + 1, column=c, padx=2, pady=2, sticky="nsew")

        # Events panel (right)
        self.event_area = ctk.CTkFrame(main, fg_color="transparent")
        self.event_area.grid(row=0, column=2, sticky="nsew")
        self.event_area.grid_columnconfigure(0, weight=1)
        self.event_area.grid_rowconfigure(2, weight=1)

        self.render_events()

    # ── calendar rendering ────────────────────────────────────────────────────

    def display_month(self):
        self.month_year_label.configure(text=self.current_date.strftime("%B %Y"))

        year  = self.current_date.year
        month = self.current_date.month
        cal   = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
        today = datetime.now()

        for week_idx in range(6):
            week = cal[week_idx] if week_idx < len(cal) else [0] * 7
            for day_idx, day in enumerate(week):
                btn = self.date_buttons[week_idx][day_idx]
                if day == 0:
                    btn.configure(text="", state="disabled",
                                  fg_color="transparent", border_width=0)
                else:
                    date_obj = datetime(year, month, day)
                    key      = self._key(date_obj)
                    is_today = (day == today.day and month == today.month
                                and year == today.year)
                    is_sel   = (self.selected_date is not None
                                and self._key() == key)
                    fg = PURPLE if is_today else (PURPLE_HOVER if is_sel else BG_CARD)
                    btn.configure(
                        text=f"{day}\n●" if self.events.get(key) else str(day),
                        state="normal", fg_color=fg,
                        border_width=2 if is_sel else 0,
                        border_color=PURPLE,
                        command=lambda d=date_obj: self.select_date(d))

    # ── navigation ────────────────────────────────────────────────────────────

    def change_month(self, delta):
        m = self.current_date.month + delta
        y = self.current_date.year + (m - 1) // 12
        self.current_date = self.current_date.replace(year=y, month=(m - 1) % 12 + 1)
        self.refresh()

    def go_to_today(self):
        self.current_date = datetime.now()
        self.selected_date = self.current_date
        self.refresh()

    def select_date(self, date_obj):
        self.selected_date = date_obj
        self.refresh()

    # ── event actions ─────────────────────────────────────────────────────────

    def add_event(self):
        text = self.ev_entry.get().strip()
        if not text or not self.selected_date:
            return
        self.events.setdefault(self.key(), []).append(text)
        self.ev_entry.delete(0, "end")
        self.refresh()

    def delete_event(self, key, idx):
        self.events[key].pop(idx)
        if not self.events[key]:
            del self.events[key]
        self.refresh()

    # ── events panel ──────────────────────────────────────────────────────────

    def render_events(self):
        for w in self.event_area.winfo_children():
            w.destroy()

        header_text = (self.selected_date.strftime("Events — %B %d, %Y")
                       if self.selected_date else "Events")
        ctk.CTkLabel(self.event_area, text=header_text,
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 6))

        inp = ctk.CTkFrame(self.event_area, fg_color="transparent")
        inp.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        inp.grid_columnconfigure(0, weight=1)

        has_day = bool(self.selected_date)
        self.ev_entry = ctk.CTkEntry(
            inp, height=34,
            placeholder_text="Add event…" if has_day else "Select a day first",
            state="normal" if has_day else "disabled")
        self.ev_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.ev_entry.bind("<Return>", lambda _: self.add_event())

        add_btn = primary_btn(inp, "+ Add", self.add_event, width=72)
        add_btn.configure(state="normal" if has_day else "disabled")
        add_btn.grid(row=0, column=1)

        if not has_day:
            ctk.CTkLabel(self.event_area, text="Select a day to view events",
                         text_color=("gray60", "gray50")).grid(row=2, column=0, pady=8)
            return

        evs = self.events.get(self._key(), [])
        if not evs:
            ctk.CTkLabel(self.event_area, text="No events for this day",
                         text_color=("gray60", "gray50")).grid(row=2, column=0, pady=8)
            return

        ev_list = scrollable(self.event_area)
        ev_list.grid(row=2, column=0, sticky="nsew")
        ev_list.grid_columnconfigure(0, weight=1)
        key = self._key()
        for i, ev in enumerate(evs):
            row_frame = ctk.CTkFrame(ev_list, fg_color=BG_CARD, corner_radius=8)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            row_frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row_frame, text=f"• {ev}", anchor="w",
                         font=ctk.CTkFont(size=13)).grid(
                row=0, column=0, padx=10, pady=6, sticky="ew")
            danger_btn(row_frame, "🗑",
                       lambda k=key, idx=i: self._delete_event(k, idx)
                       ).grid(row=0, column=1, padx=(0, 6))
