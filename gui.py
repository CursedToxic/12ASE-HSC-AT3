import sys
import customtkinter
from datetime import datetime
from event_planner import CalendarFrame
from todo import TodoFrame
from notes import NotesFrame
from flashcards import FlashcardsFrame
from settings import SettingsFrame
import animations

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Basic Study App")
        self.geometry("800x600")
        self.minsize(800, 600)
        self.configure(fg_color=("white", "black"))
        self.update_idletasks()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)

        self.settings = {"appearance": "Dark", "font_scale": 1.0}
        self._apply_settings(self.settings)

        self.responsive_font = animations.responsive_font(
            self, divisor=25, min_size=48, max_size=1024)
        self._login_font = animations.responsive_font(
            self, divisor=20, min_size=18, max_size=42)
        self._greeting_font = animations.responsive_font(
            self, weight="bold", divisor=30, min_size=16, max_size=38)
        self._clock_job  = None
        self._history    = []
        self._logged_in  = False

        self.ui_title = customtkinter.CTkLabel(
            self, text="Basic Study App", font=self.responsive_font,
            fg_color="transparent"
        )
        self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        login_button = customtkinter.CTkButton(
            self, text="Login", corner_radius=50, command=self.login_system
        )
        login_button.grid(row=1, column=0, padx=10, pady=10, sticky="n")
        # animations.click_pulse(login_button)

        self.theme_btn = customtkinter.CTkButton(
            self,
            text="☀" if self.settings["appearance"] == "Dark" else "🌙",
            width=36, height=36, corner_radius=18,
            fg_color="transparent", border_width=1,
            border_color=("gray70", "gray30"),
            text_color=("gray30", "gray70"),
            hover_color=("gray85", "gray20"),
            command=lambda: self._toggle_theme(self.theme_btn)
        )
        self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        # animations.click_pulse(self.theme_btn)

        self._setup_keybinds()

    # ── Keybinds ──────────────────────────────────────────────────────────────

    def _setup_keybinds(self):
        mac = sys.platform == "darwin"

        # Clipboard — forward to whichever widget has focus
        for seq in ("<Control-c>", "<Command-c>" if mac else None):
            if seq: self.bind_all(seq, lambda e: e.widget.event_generate("<<Copy>>"))
        for seq in ("<Control-v>", "<Command-v>" if mac else None):
            if seq: self.bind_all(seq, lambda e: e.widget.event_generate("<<Paste>>"))
        for seq in ("<Control-x>", "<Command-x>" if mac else None):
            if seq: self.bind_all(seq, lambda e: e.widget.event_generate("<<Cut>>"))
        for seq in ("<Control-z>", "<Command-z>" if mac else None):
            if seq: self.bind_all(seq, lambda e: e.widget.event_generate("<<Undo>>"))
        for seq in ("<Control-a>", "<Command-a>" if mac else None):
            if seq: self.bind_all(seq, lambda e: e.widget.event_generate("<<SelectAll>>"))

        # App navigation
        self._tab_sections = [
            self.show_todo, self.show_notes,
            self.show_flashcards, self.show_calendar,
        ]
        self._tab_index = -1
        # self.bind("<Tab>", lambda _: self._tab_navigate())
        self.bind("<Control-h>", lambda _: self.go_home() if self._logged_in else None)
        if mac:
            self.bind("<Command-h>", lambda _: self.go_home() if self._logged_in else None)
        self.bind("<Escape>", lambda _: self._go_back())

    def _go_back(self):
        if self._history:
            self._history.pop()()

    def _tab_navigate(self, e):
        focused = self.focus_get()
        if isinstance(focused, (customtkinter.CTkEntry, customtkinter.CTkTextbox)):
            return  # let the widget handle Tab normally
        self._tab_index = (self._tab_index + 1) % len(self._tab_sections)
        self._tab_sections[self._tab_index]()
        return "break"

    # ── Clear helpers ─────────────────────────────────────────────────────────

    def _clear(self, num_rows=10):
        geo = self.geometry()
        if self._clock_job:
            self.after_cancel(self._clock_job)
            self._clock_job = None
        for widget in self.winfo_children():
            if widget is self.theme_btn:
                continue
            widget.destroy()
        self.theme_btn.place_forget()
        for r in range(num_rows):
            self.grid_rowconfigure(r, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.geometry(geo)

    # ── Login screen ──────────────────────────────────────────────────────────

    def login_system(self):
        def _build():
            self._clear()

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(8, weight=1)

            customtkinter.CTkLabel(self, text="Login", font=self._login_font).grid(
                row=1, column=0, pady=(0, 10))

            username_label = customtkinter.CTkLabel(self, text="Username")
            username_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), width=220)
            username_label.grid(row=2, column=0, pady=0)
            username_entry.grid(row=3, column=0, pady=6)

            password_label = customtkinter.CTkLabel(self, text="Password")
            password_entry = customtkinter.CTkEntry(
                self, font=("Helvetica", 12), show="*", width=220)
            password_label.grid(row=5, column=0, pady=0)
            password_entry.grid(row=6, column=0, pady=6)

            inv_user_label = customtkinter.CTkLabel(
                self, text="Invalid Username", text_color="orange")
            inv_pwd_label = customtkinter.CTkLabel(
                self, text="Invalid Password", text_color="orange")
            inv_user_label.grid(row=4, column=0)
            inv_pwd_label.grid(row=7, column=0)
            inv_user_label.grid_remove()
            inv_pwd_label.grid_remove()

            def check_login():
                user = username_entry.get()
                global username
                username = user
                password = password_entry.get()

                invalid_usr = not user.isalnum()
                invalid_pwd = (
                    len(password) < 8 or "<" in password or ">" in password or password.isalnum()
                )

                if invalid_usr:
                    inv_user_label.grid()
                else:
                    inv_user_label.grid_remove()

                if invalid_pwd:
                    inv_pwd_label.grid()
                else:
                    inv_pwd_label.grid_remove()

                if not invalid_usr and not invalid_pwd:
                    self.show_clock()

            username_entry.bind("<Return>", lambda _: password_entry.focus())
            password_entry.bind("<Return>",  lambda _: check_login())

            submit_btn = customtkinter.CTkButton(
                self, text="Submit", corner_radius=50, command=check_login)
            submit_btn.grid(row=8, column=0, pady=16)
            # animations.click_pulse(submit_btn)

            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
            self.update_idletasks()

        _build()

    def _toggle_theme(self, btn):
        new_mode = "Light" if self.settings["appearance"] == "Dark" else "Dark"
        self.settings["appearance"] = new_mode
        self._apply_settings(self.settings)
        btn.configure(text="☀" if new_mode == "Dark" else "🌙")
    
        self.update_idletasks()

    # ── Clock screen ──────────────────────────────────────────────────────────

    def show_clock(self):
        self._logged_in = True
        self._history.clear()
        def _build():
            self._clear()

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(4, weight=1)

            customtkinter.CTkLabel(
                self, text=f"Welcome, {username}", font=("Helvetica", 18),
                text_color="gray60"
            ).grid(row=1, column=0, pady=(0, 6))

            clock_frame = customtkinter.CTkFrame(self, fg_color="transparent")
            clock_frame.grid(row=2, column=0)

            clock_font = customtkinter.CTkFont(family="Helvetica", size=64, weight="bold")
            ampm_font  = customtkinter.CTkFont(family="Helvetica", size=28, weight="bold")

            time_label = customtkinter.CTkLabel(
                clock_frame, text="", font=clock_font, fg_color="transparent"
            )
            time_label.grid(row=0, column=0, padx=(0, 8))

            ampm_label = customtkinter.CTkLabel(
                clock_frame, text="", font=ampm_font,
                text_color="#534AB7", fg_color="transparent"
            )
            ampm_label.grid(row=0, column=1)

            home_btn = customtkinter.CTkButton(
                self, text="⌂  Home", corner_radius=50, command=self.go_home)
            home_btn.grid(row=3, column=0, pady=20)
            # animations.click_pulse(home_btn)

            def tick():
                now = datetime.now()
                time_label.configure(text=now.strftime("%I:%M:%S"))
                ampm_label.configure(text=now.strftime("%p"))
                self._clock_job = self.after(1000, tick)

            tick()

        _build()

    # ── Home screen ───────────────────────────────────────────────────────────

    def go_home(self):
        self._history.clear()
        def _build():
            self._clear()

            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=0)
            self.grid_rowconfigure(3, weight=0)
            self.grid_rowconfigure(4, weight=1)
            self.grid_rowconfigure(5, weight=0)

            hour = datetime.now().hour
            if hour < 12:
                greeting = f"🌤 Good Morning, {username}"
            elif hour < 17:
                greeting = f"☀️ Good Afternoon, {username}"
            else:
                greeting = f"🌙 Good Evening, {username}"

            header = customtkinter.CTkFrame(self, fg_color="transparent")
            header.grid(row=0, column=0, padx=20, pady=(20, 2), sticky="ew")
            header.grid_columnconfigure(0, weight=1)

            customtkinter.CTkLabel(
                header, text=greeting,
                font=self._greeting_font, anchor="w"
            ).grid(row=0, column=0, sticky="w")

            settings_btn = customtkinter.CTkButton(
                header, text="⚙", width=36, height=36, corner_radius=18,
                fg_color="transparent", border_width=1,
                border_color="gray30", text_color="gray50",
                hover_color="#1a1a1a",
                command=self.show_settings
            )
            settings_btn.grid(row=0, column=1)
            # animations.click_pulse(settings_btn)

            clock_strip_font = customtkinter.CTkFont(family="Helvetica", size=14)
            clock_strip = customtkinter.CTkLabel(
                self, text="", font=clock_strip_font, text_color="gray55",
                fg_color="transparent"
            )
            clock_strip.grid(row=1, column=0, pady=(0, 18))

            def tick_strip():
                now = datetime.now()
                clock_strip.configure(
                    text=now.strftime("%A, %B %d  •  %I:%M:%S %p")
                )
                self._clock_job = self.after(1000, tick_strip)

            tick_strip()

            customtkinter.CTkLabel(
                self, text="JUMP TO", font=("Helvetica", 11),
                text_color="gray50"
            ).grid(row=2, column=0, pady=(0, 8))

            cards_frame = customtkinter.CTkFrame(self, fg_color="transparent")
            cards_frame.grid(row=3, column=0, padx=32, sticky="nsew")
            for c in range(4):
                cards_frame.grid_columnconfigure(c, weight=1, uniform="cards")
            cards_frame.grid_rowconfigure(0, weight=1)

            features = [
                ("☑\nTo-Do",      ("#c8e6c9", "#1a472a"), self.show_todo),
                ("📝\nNotes",      ("#c5cae9", "#1a1a47"), self.show_notes),
                ("🃏\nFlashcards", ("#ffccbc", "#47201a"), self.show_flashcards),
                ("📅\nCalendar",   ("#e1bee7", "#2a1a47"), self.show_calendar),
            ]

            card_widgets, card_colors = [], []
            for col, (label, color, cmd) in enumerate(features):
                card = customtkinter.CTkFrame(
                    cards_frame, fg_color=color, corner_radius=12, cursor="hand2"
                )
                card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
                card.grid_rowconfigure(0, weight=1)
                card.grid_columnconfigure(0, weight=1)

                customtkinter.CTkLabel(
                    card, text=label, font=("Helvetica", 13),
                    fg_color="transparent", justify="center"
                ).grid(row=0, column=0, padx=12, pady=20)

                card.bind("<Button-1>", lambda e, c=cmd: c())
                for child in card.winfo_children():
                    child.bind("<Button-1>", lambda e, c=cmd: c())

                card_widgets.append(card)
                card_colors.append(color)

            # animations.stagger_cards(card_widgets, card_colors)

            logout_btn = customtkinter.CTkButton(
                self, text="Log Out", corner_radius=50,
                fg_color="transparent", border_width=1,
                border_color="gray30", text_color="gray50",
                hover_color="#1a1a1a",
                command=self._logout
            )
            logout_btn.grid(row=4, column=0, pady=20)
            # animations.click_pulse(logout_btn)

        _build()

    def _apply_settings(self, new_settings):
        self.settings = new_settings
        geo = self.geometry()
        customtkinter.set_appearance_mode(self.settings["appearance"])
        customtkinter.set_widget_scaling(self.settings["font_scale"])
        self.geometry(geo)
        self.configure(fg_color=("white", "black"))

    def show_settings(self):
        self._history.append(self.go_home)
        def _build():
            self._clear()
            self.grid_rowconfigure(0, weight=1)
            SettingsFrame(self, self.settings, on_apply=self._on_settings_apply).grid(
                row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50,
                command=self.go_home)
            home_btn.grid(row=1, column=0, pady=10)
            # animations.click_pulse(home_btn)
        _build()

    def _on_settings_apply(self, new_settings):
        self._apply_settings(new_settings)

    def show_flashcards(self):
        self._history.append(self.go_home)
        def _build():
            self._clear()
            self.grid_rowconfigure(0, weight=1)
            FlashcardsFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50,
                command=self.go_home)
            home_btn.grid(row=1, column=0, pady=10)
            # animations.click_pulse(home_btn)
        _build()

    def show_todo(self):
        self._history.append(self.go_home)
        def _build():
            self._clear()
            self.grid_rowconfigure(0, weight=1)
            TodoFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50,
                command=self.go_home)
            home_btn.grid(row=1, column=0, pady=10)
            # animations.click_pulse(home_btn)
        _build()

    def show_notes(self):
        self._history.append(self.go_home)
        def _build():
            self._clear()
            self.grid_rowconfigure(0, weight=1)
            NotesFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50,
                command=self.go_home)
            home_btn.grid(row=1, column=0, pady=10)
            # animations.click_pulse(home_btn)
        _build()

    def show_calendar(self):
        self._history.append(self.go_home)
        def _build():
            self._clear()
            self.grid_rowconfigure(0, weight=1)
            CalendarFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50,
                command=self.go_home)
            home_btn.grid(row=1, column=0, pady=10)
            # animations.click_pulse(home_btn)
        _build()

    def _logout(self):
        self._logged_in = False
        self._history.clear()
        def _build():
            self._clear()

            self.grid_rowconfigure(0, weight=3)
            self.grid_rowconfigure(1, weight=1)

            self.ui_title = customtkinter.CTkLabel(
                self, text="Basic Study App", font=self.responsive_font,
                fg_color="transparent"
            )
            self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

            login_btn = customtkinter.CTkButton(
                self, text="Login", corner_radius=50, command=self.login_system)
            login_btn.grid(row=1, column=0, padx=10, pady=10, sticky="n")
            # animations.click_pulse(login_btn)

            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        _build()


app = App()
app.mainloop()
