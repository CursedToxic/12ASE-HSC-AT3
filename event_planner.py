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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.events = {}
        self.selected = None
        today = date.today()
        self.year, self.month = today.year, today.month

        ctk.CTkLabel(self, text="Calendar",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, padx=20, sticky="ew")
        self.content.grid_columnconfigure(0, weight=1)

        self.event_area = ctk.CTkFrame(self, fg_color="transparent")
        self.event_area.grid(row=2, column=0, padx=20, pady=(8, 16), sticky="nsew")
        self.event_area.grid_columnconfigure(0, weight=1)
        self.event_area.grid_rowconfigure(1, weight=1)

        self.render_month()

    def render_month(self):
        for w in self.content.winfo_children():
            w.destroy()

        nav = ctk.CTkFrame(self.content, fg_color="transparent")
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        nav.grid_columnconfigure(1, weight=1)

        prev_btn = ctk.CTkButton(nav, text="◀", width=36, command=self.prev_month,
                      fg_color="transparent", hover_color=("gray80", "gray30"),
                      text_color=("gray10", "gray90"))
        prev_btn.grid(row=0, column=0)
        animations.click_pulse(prev_btn)
        ctk.CTkLabel(nav, text=f"{calendar.month_name[self.month]} {self.year}",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1)
        next_btn = ctk.CTkButton(nav, text="▶", width=36, command=self.next_month,
                      fg_color="transparent", hover_color=("gray80", "gray30"),
                      text_color=("gray10", "gray90"))
        next_btn.grid(row=0, column=2)
        animations.click_pulse(next_btn)

        grid = ctk.CTkFrame(self.content, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew")
        for col, d in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            ctk.CTkLabel(grid, text=d, width=52, font=ctk.CTkFont(size=11),
                         text_color=("gray50", "gray55")).grid(row=0, column=col, padx=1, pady=2)

        today = date.today()
        first_wd = calendar.monthrange(self.year, self.month)[0]
        first_wd = (first_wd + 1) % 7
        days_in = calendar.monthrange(self.year, self.month)[1]

        cell = 0
        for offset in range(first_wd):
            ctk.CTkLabel(grid, text="", width=52).grid(
                row=1 + cell // 7, column=cell % 7)
            cell += 1

        for day in range(1, days_in + 1):
            key = f"{self.year}-{self.month}-{day}"
            is_today = (day == today.day and self.month == today.month and self.year == today.year)
            is_sel = key == self.selected
            has_ev = bool(self.events.get(key))

            indicator = "●" if has_ev else ""
            label = f"{day}\n{indicator}" if has_ev else str(day)

            fg = PURPLE if is_today else ("gray80" if is_sel else "transparent")
            txt = "white" if is_today else ("gray10", "gray90")
            border = 2 if is_sel else 0

            btn = ctk.CTkButton(
                grid, text=label, width=52, height=42,
                fg_color=fg, hover_color=("gray75", "gray35"),
                text_color=txt, border_width=border,
                border_color=PURPLE,
                font=ctk.CTkFont(size=11),
                command=lambda k=key, dy=day: self.select_day(k, dy)
            )
            btn.grid(row=1 + cell // 7, column=cell % 7, padx=1, pady=1)
            cell += 1

    def prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.render_month()
        self.render_events()

    def next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.render_month()
        self.render_events()

    def select_day(self, key, day):
        self.selected = key
        self.render_month()
        self.render_events(day=day)

    def add_event(self):
        text = self.ev_entry.get().strip()
        if not text or not self.selected:
            return
        self.events.setdefault(self.selected, []).append(text)
        self.ev_entry.delete(0, "end")
        self.render_month()
        self.render_events()

    def delete_event(self, key, idx):
        self.events[key].pop(idx)
        self.render_month()
        self.render_events()

    def render_events(self, day=None):
        for w in self.event_area.winfo_children():
            w.destroy()
        if not self.selected:
            return

        m_name = calendar.month_name[self.month]
        d = self.selected.split("-")[2] if not day else day
        ctk.CTkLabel(self.event_area,
                     text=f"Events — {m_name} {d}, {self.year}",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 6))

        inp_row = ctk.CTkFrame(self.event_area, fg_color="transparent")
        inp_row.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        inp_row.grid_columnconfigure(0, weight=1)
        self.ev_entry = ctk.CTkEntry(inp_row, placeholder_text="Add event…", height=34)
        self.ev_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.ev_entry.bind("<Return>", lambda e: self.add_event())
        add_btn = primary_btn(inp_row, "+ Add", self.add_event, width=72)
        add_btn.grid(row=0, column=1)
        animations.click_pulse(add_btn)

        evs = self.events.get(self.selected, [])
        if not evs:
            ctk.CTkLabel(self.event_area, text="No events for this day",
                         text_color=("gray60", "gray50")).grid(row=2, column=0, pady=8)
            return

        ev_list = scrollable(self.event_area)
        ev_list.grid(row=2, column=0, sticky="nsew")
        ev_list.grid_columnconfigure(0, weight=1)
        for i, ev in enumerate(evs):
            row = ctk.CTkFrame(ev_list, fg_color=BG_CARD, corner_radius=8)
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=f"• {ev}", anchor="w",
                         font=ctk.CTkFont(size=13)).grid(
                row=0, column=0, padx=10, pady=6, sticky="ew")
            key = self.selected
            del_btn = danger_btn(row, "🗑", lambda k=key, idx=i: self.delete_event(k, idx))
            del_btn.grid(row=0, column=1, padx=(0, 6))
            animations.click_pulse(del_btn)

