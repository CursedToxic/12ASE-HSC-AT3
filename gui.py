import sys
import customtkinter
from datetime import datetime
from event_planner import CalendarFrame
from todo import TodoFrame
from notes import NotesFrame
from flashcards import FlashcardsFrame
from settings import SettingsFrame
import animations

# Variables
app_name = "Locked In(c)."

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title(app_name)
        self.geometry("800x600")
        self.minsize(800, 600)
        self.configure(fg_color=("white", "black"))
        self.update_idletasks()

        # Configure Columns
        self.grid_columnconfigure(0, weight=1)

        # Configure Rows
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self.settings = {"appearance": "Dark", "font_scale": 1.0}
        self.apply_settings(self.settings)

        # Instructed by Claude: Creates a font the dynamically adjusts based on window size
        self.responsive_font = animations.responsive_font(
            self, divisor=25, min_size=48, max_size=1024)
        self.login_font = animations.responsive_font(
            self, divisor=20, min_size=18, max_size=42)
        self.greeting_font = animations.responsive_font(
            self, weight="bold", divisor=30, min_size=16, max_size=38)
        self.clock_job  = None
        self.history    = []
        self.logged_in  = False

        self.ui_title = customtkinter.CTkLabel(
            self, text=app_name, font=self.responsive_font,
            fg_color="transparent"
        )
        self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        login_button = customtkinter.CTkButton(self, text="Login", corner_radius=50, command=self.login_system).grid(row=1, column=0, padx=10, pady=10, sticky="n")
        # animations.click_pulse(login_button)

        # Create and Display a button for registraion
        register_button = customtkinter.CTkButton(self, text="Register",  corner_radius=50, command=self.registration).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        
        # Theme button: Outsourcing from Claude
        self.theme_btn = customtkinter.CTkButton(
            self,
            text="☀" if self.settings["appearance"] == "Dark" else "🌙",
            width=36, height=36, corner_radius=18,
            fg_color="transparent", border_width=1,
            border_color=("gray70", "gray30"),
            text_color=("gray30", "gray70"),
            hover_color=("gray85", "gray20"),
            command=lambda: self.toggle_theme(self.theme_btn)
        )
        self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.setup_keybinds()

    # ── Theming ───────────────────────────────────────────────────────────────

    def toggle_theme(self, btn):
        new_mode = "Light" if self.settings["appearance"] == "Dark" else "Dark"
        self.settings["appearance"] = new_mode
        self.apply_settings(self.settings)
        btn.configure(text="☀" if new_mode == "Dark" else "🌙")
    
        self.update_idletasks()

    # ── Keybinds ──────────────────────────────────────────────────────────────

    # Instructions from Claude: Set Keybinds using .bind()
    def setup_keybinds(self):
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
        self.tab_sections = [
            self.show_todo, self.show_notes,
            self.show_flashcards, self.show_calendar,
        ]
        self.tab_index = -1
        # self.bind("<Tab>", lambda _: self._tab_navigate())
        self.bind("<Control-h>", lambda _: self.go_home() if self.logged_in else None)
        if mac:
            self.bind("<Command-h>", lambda _: self.go_home() if self.logged_in else None)
        self.bind("<Escape>", lambda _: self.go_back())

    def go_back(self):
        if self.history:
            self.history.pop()()

    def tab_navigate(self, e):
        focused = self.focus_get()
        if isinstance(focused, (customtkinter.CTkEntry, customtkinter.CTkTextbox)):
            return  # let the widget handle Tab normally
        self.tab_index = (self.tab_index + 1) % len(self.tab_sections)
        self.tab_sections[self.tab_index]()
        return "break"

    # ── Clear helpers ─────────────────────────────────────────────────────────

    # Instructions from Claude: Remove all elements using .destroy()
    def clear(self, num_rows=10):
        geo = self.geometry()
        if self.clock_job:
            self.after_cancel(self.clock_job)
            self.clock_job = None
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
        def build():
            # Clear screen
            self.clear()

            # Reconfigure rows
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(8, weight=1)

            # Login screen title
            customtkinter.CTkLabel(self, text="Login", font=self.login_font).grid(
                row=1, column=0, pady=(0, 10))

            # Username text & entry
            username_label = customtkinter.CTkLabel(self, text="Username")
            username_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), width=220)
            username_label.grid(row=2, column=0, pady=0)
            username_entry.grid(row=3, column=0, pady=6)

            # Password text & entry
            password_label = customtkinter.CTkLabel(self, text="Password")
            password_entry = customtkinter.CTkEntry(
                self, font=("Helvetica", 12), show="*", width=220)
            password_label.grid(row=5, column=0, pady=0)
            password_entry.grid(row=6, column=0, pady=6)

            # Invalid Username Message
            inv_user_label = customtkinter.CTkLabel(self, text="Invalid Username: Must be Alphanumeric", text_color="red")

            # Invalid Password Message
            inv_pwd_label = customtkinter.CTkLabel(self, text="", text_color="red")

            # Error Handling: Invalid detail format
            inv_details = customtkinter.CTkLabel(self, text="Invalid Username or Password format.")

            def check_login():
                    user = username_entry.get()

                    self.username = user

                    password = password_entry.get()

                    # Gemini gave instructions and helped debug here. This enabled me to imporve percieved program responsiveness.

                    # Followed AI's instructions to optimise the criteria
                    invalid_usr = (not user.isalnum() or len(user) < 2)
                    invalid_pwd = (len(password) < 8 or "<" in password or ">" in password or password.isalnum())

                    if invalid_usr:
                        # Display Invalid User Message
                        inv_user_label.grid(row=4, column=0)

                    else:
                        # Remove Message when valid
                        inv_user_label.grid_remove()

                    if invalid_pwd:
                        if "<" in password or ">" in password:
                            error_msg = "Must not contain '<' or '>'"

                        elif len(password) < 8:
                            error_msg = "Must be more than 8 characters"
                        
                        elif password.isalnum():
                            error_msg = "Must not be alphanumeric"

                        # ChatGPT helped me debug this
                        # Configure the input message within the check_login function to remove potential issues where error_msg is defined
                        inv_pwd_label.configure(text=f"Invalid Password: {error_msg}")

                        # Display the error message
                        inv_pwd_label.grid(row=7, column=0)

                    else:
                        # Remove Message when valid
                        inv_pwd_label.grid_remove()

                    if not invalid_usr and not invalid_pwd:
                        self.show_clock()

            username_entry.bind("<Return>", lambda _: password_entry.focus())
            password_entry.bind("<Return>",  lambda _: check_login())

            submit_btn = customtkinter.CTkButton(self, text="Login", corner_radius=50, command=check_login)
            submit_btn.grid(row=8, column=0, pady=16)
            # animations.click_pulse(submit_btn)

            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
            self.update_idletasks()

        build()

    # ── Registration ──────────────────────────────────────────────────────────

    def registration(self):
        def build():
            self.clear()

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(8, weight=1)

            customtkinter.CTkLabel(self, text="Register", font=self.login_font).grid(
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
                self, text="Username must be Alphanumeric", text_color="red")
            
            inv_pwd_label = customtkinter.CTkLabel(self, text="", text_color="red")

            def check_registration():
                user = username_entry.get()

                self.username = user

                password = password_entry.get()

                # Gemini gave instructions and helped debug here. This enabled me to imporve percieved program responsiveness.

                # Followed AI's instructions to optimise the criteria
                invalid_usr = (not user.isalnum() or len(user) < 2)

                # Set invalid_pwd to be true
                invalid_pwd = True

                if invalid_usr:
                    # Display Invalid User Message
                    inv_user_label.grid(row=4, column=0)

                else:
                    # Remove Message when valid
                    inv_user_label.grid_remove()

                if "<" in password or ">" in password:
                    error_msg = "Must not contain '<' or '>'"

                elif len(password) < 8:
                    error_msg = "Must be more than 8 characters"
                        
                elif password.isalnum():
                    error_msg = "Must not be alphanumeric"

                    # ChatGPT helped me debug this
                    # Configure the input message within the check_login function to remove potential issues where error_msg is defined
                    inv_pwd_label.configure(text=f"Invalid Password: {error_msg}")

                    # Display the error message
                    inv_pwd_label.grid(row=7, column=0)

                else:
                    # Remove Message when valid
                    invalid_pwd = not invalid_pwd
                    inv_pwd_label.grid_remove()

                if not invalid_usr and not invalid_pwd:
                    self.show_clock()

            username_entry.bind("<Return>", lambda _: password_entry.focus())
            password_entry.bind("<Return>",  lambda _: check_registration())

            submit_btn = customtkinter.CTkButton(
                self, text="Register", corner_radius=50, command=check_registration)
            submit_btn.grid(row=8, column=0, pady=16)
            # animations.click_pulse(submit_btn)

            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
            self.update_idletasks()

        build()

    # ── Clock screen ──────────────────────────────────────────────────────────

    def show_clock(self):
        self.logged_in = True
        self.history.clear()
        def build():
            self.clear()

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(4, weight=1)

            customtkinter.CTkLabel(self, text=f"Welcome, {self.username}", font=("Helvetica", 18), text_color="gray60").grid(row=1, column=0, pady=(0, 6))

            clock_frame = customtkinter.CTkFrame(self, fg_color="transparent")
            clock_frame.grid(row=2, column=0)

            clock_font = customtkinter.CTkFont(family="Helvetica", size=64, weight="bold")
            ampm_font  = customtkinter.CTkFont(family="Helvetica", size=28, weight="bold")

            time_label = customtkinter.CTkLabel(clock_frame, text="", font=clock_font, fg_color="transparent")
            time_label.grid(row=0, column=0, padx=(0, 8))

            am_pm = customtkinter.CTkLabel(clock_frame, text="", font=ampm_font, text_color="#534AB7", fg_color="transparent")
            am_pm.grid(row=0, column=1)

            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home)
            home_btn.grid(row=3, column=0, pady=20)

            def tick():
                now = datetime.now()
                time_label.configure(text=now.strftime("%I:%M:%S"))
                am_pm.configure(text=now.strftime("%p"))
                self.clock_job = self.after(1000, tick)

            tick()

        build()

    # ── Home screen ───────────────────────────────────────────────────────────

    def go_home(self):
        self.history.clear()
        def build():
            self.clear()

            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=0)
            self.grid_rowconfigure(3, weight=1)
            self.grid_rowconfigure(4, weight=1)
            self.grid_rowconfigure(5, weight=0)

            hour = datetime.now().hour
            if hour < 12:
                greeting = f"🌤 Good Morning, {self.username}"
            elif hour < 17:
                greeting = f"☀️ Good Afternoon, {self.username}"
            else:
                greeting = f"🌙 Good Evening, {self.username}"

            header = customtkinter.CTkFrame(self, fg_color="transparent")
            header.grid(row=0, column=0, padx=20, pady=(20, 2), sticky="ew")
            header.grid_columnconfigure(0, weight=1)

            customtkinter.CTkLabel(header, text=greeting, font=self.greeting_font, anchor="w").grid(row=0, column=0, sticky="w")

            settings_btn = customtkinter.CTkButton(
                header, text="⚙", width=36, height=36, corner_radius=18, fg_color="transparent", border_width=1,
                border_color="gray30", text_color="gray50", hover_color="#1a1a1a", command=self.show_settings
            ).grid(row=0, column=1)

            clock_strip_font = customtkinter.CTkFont(family="Helvetica", size=14)
            clock_strip = customtkinter.CTkLabel(self, text="", font=clock_strip_font, text_color="gray55", fg_color="transparent")
            clock_strip.grid(row=1, column=0, pady=(0, 18))

            # Display Date and Time
            def tick_strip():
                now = datetime.now()
                clock_strip.configure(text=now.strftime("%A, %B %d  •  %I:%M:%S %p"))
                self.clock_job = self.after(1000, tick_strip)

            tick_strip()

            customtkinter.CTkLabel(self, text="JUMP TO", font=("Helvetica", 11), text_color="gray50").grid(row=2, column=0, pady=(0, 8))

            panel_frame = customtkinter.CTkFrame(self, fg_color="transparent")
            panel_frame.grid(row=3, column=0, padx=32, sticky="nsew")

            for i in range(4):
                panel_frame.grid_columnconfigure(i, weight=1, uniform="cards")
            panel_frame.grid_rowconfigure(0, weight=1)
            
            # List of functions that are currently supported, more coming soon :)
            functions = [
                ("☑\nTo-Do",      ("#c8e6c9", "#1a472a"), self.show_todo),
                ("📝\nNotes",      ("#c5cae9", "#1a1a47"), self.show_notes),
                ("🃏\nFlashcards", ("#ffccbc", "#47201a"), self.show_flashcards),
                ("📅\nCalendar",   ("#e1bee7", "#2a1a47"), self.show_calendar),
            ]

            # Create empty list for cards 
            widgets, widget_colors = [], []
            for col, (label, color, cmd) in enumerate(functions):
                card = customtkinter.CTkFrame(panel_frame, fg_color=color, corner_radius=12, cursor="hand")
                card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
                card.grid_rowconfigure(0, weight=1)
                card.grid_columnconfigure(0, weight=1)

                customtkinter.CTkLabel(card, text=label, font=("Helvetica", 13), fg_color="transparent", justify="center").grid(row=0, column=0, padx=12, pady=20)

                card.bind("<Button-1>", lambda e, c=cmd: c())
                for child in card.winfo_children():
                    child.bind("<Button-1>", lambda e, c=cmd: c())

                widgets.append(card)
                widget_colors.append(color)

            logout_btn = customtkinter.CTkButton(self, text="Log Out", corner_radius=50, fg_color="transparent", border_width=1, border_color="gray30", text_color="gray50", hover_color="#1a1a1a", command=self.logout).grid(row=4, column=0, pady=20)

        build()

    def apply_settings(self, new_settings):
        self.settings = new_settings
        geo = self.geometry()
        customtkinter.set_appearance_mode(self.settings["appearance"])
        customtkinter.set_widget_scaling(self.settings["font_scale"])
        self.geometry(geo)
        self.configure(fg_color=("white", "black"))

    def show_settings(self):
        self.history.append(self.go_home)
        def build():
            self.clear()
            self.grid_rowconfigure(0, weight=1)
            SettingsFrame(self, self.settings, on_apply=self.on_settings_apply).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home).grid(row=1, column=0, pady=10)
        build()

    # Followed Claude's instructions
    def on_settings_apply(self, new_settings):
        self.apply_settings(new_settings)

    def show_flashcards(self):
        self.history.append(self.go_home)
        def build():
            self.clear()
            self.grid_rowconfigure(0, weight=1)
            FlashcardsFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home).grid(row=1, column=0, pady=10)
        build()

    def show_todo(self):
        self.history.append(self.go_home)
        def build():
            self.clear()
            self.grid_rowconfigure(0, weight=1)
            TodoFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home).grid(row=1, column=0, pady=10)
        build()

    def show_notes(self):
        self.history.append(self.go_home)
        def build():
            self.clear()
            self.grid_rowconfigure(0, weight=1)
            NotesFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home).grid(row=1, column=0, pady=10)
        build()

    def show_calendar(self):
        self.history.append(self.go_home)
        def build():
            self.clear()
            self.grid_rowconfigure(0, weight=1)
            CalendarFrame(self).grid(row=0, column=0, sticky="nsew")
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home).grid(row=1, column=0, pady=10)
        build()

    def logout(self):
        self.logged_in = False
        self.history.clear()
        def build():
            self.clear()

            self.grid_rowconfigure(0, weight=3)
            self.grid_rowconfigure(1, weight=1)

            self.ui_title = customtkinter.CTkLabel(self, text=app_name, font=self.responsive_font, fg_color="transparent")
            self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

            login_btn = customtkinter.CTkButton(self, text="Login", corner_radius=50, command=self.login_system)
            login_btn.grid(row=1, column=0, padx=10, pady=10, sticky="n")

            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        build()

app = App()
app.mainloop()