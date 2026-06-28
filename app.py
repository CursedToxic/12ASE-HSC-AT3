import sys
import customtkinter
from datetime import datetime
from events import CalendarFrame
from todo import TodoFrame
from notes import NotesFrame
from flashcards import FlashcardsFrame
from settings import SettingsFrame
from encryption import *
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
        
        # Establish default values for clock, history and login state
        self.clock_job  = None
        self.history    = []
        self.logged_in  = False

        # Display the Title
        self.ui_title = customtkinter.CTkLabel(self, text=app_name, font=self.responsive_font, fg_color="transparent")
        self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Create and Display a Login Button
        login_button = customtkinter.CTkButton(self, text="Login", corner_radius=50, command=self.login).grid(row=1, column=0, padx=10, pady=10, sticky="n")

        # Create and Display a button for registraion
        register_button = customtkinter.CTkButton(self, text="Register",  corner_radius=50, command=self.registration).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        
        # Theme button: Outsourcing from Claude
        self.theme_btn = customtkinter.CTkButton(
            self, text="☀" if self.settings["appearance"] == "Dark" else "🌙", width=36, height=36, corner_radius=18, fg_color="transparent", border_width=1,
            border_color=("gray70", "gray30"), text_color=("gray30", "gray70"), hover_color=("gray85", "gray20"), command=lambda: self.toggle_theme(self.theme_btn))
        self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Call the function to setup keybinds
        self.setup_keybinds()

    def toggle_theme(self, button):
        new_mode = "Light" if self.settings["appearance"] == "Dark" else "Dark"
        self.settings["appearance"] = new_mode
        self.apply_settings(self.settings)
        button.configure(text="☀" if new_mode == "Dark" else "🌙")
    
        self.update_idletasks()

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

    # ChatGPT heped me debug, the reason for the second brackets is to actually navigate back rather than simply removing from a list.
    def go_back(self):
        if self.history:
            self.history.pop()()

    # Instructions from Claude: Bind the tab key to an event
    def tab_navigate(self, e):
        focused = self.focus_get()
        if isinstance(focused, (customtkinter.CTkEntry, customtkinter.CTkTextbox)):
            return  # let the widget handle Tab normally
        self.tab_index = (self.tab_index + 1) % len(self.tab_sections)
        self.tab_sections[self.tab_index]()
        return "break"

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

    def go_to_title(self):
        # ChatGPT instructed me to create this function
        # Reset History & Login State
        self.logged_in = False
        self.history.clear()

        def build():
            self.clear()

            # Reconfigure rows (reset layout)
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=3)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=1)

            # Title
            self.ui_title = customtkinter.CTkLabel(self, text=app_name, font=self.responsive_font, fg_color="transparent")
            self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

            # Login button
            customtkinter.CTkButton(self, text="Login", corner_radius=50, command=self.login).grid(row=1, column=0, padx=10, pady=10, sticky="n")

            # Register button
            customtkinter.CTkButton(self, text="Register", corner_radius=50, command=self.registration).grid(row=2, column=0, padx=10, pady=10, sticky="n")

            # Theme button
            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        build()

    def registration(self):
        def build():
            self.clear()

            # Configure Rows
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(9, weight=1)

            # Title of Screen
            customtkinter.CTkLabel(self, text="Register", font=self.login_font).grid(row=1, column=0, pady=(0, 10))

            # Create & Display Username and Password Entry Fields
            username_label = customtkinter.CTkLabel(self, text="Username")
            username_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), width=220)
            username_label.grid(row=2, column=0, pady=0)
            username_entry.grid(row=3, column=0, pady=6)

            password_label = customtkinter.CTkLabel(self, text="Password")
            password_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), show="*", width=220)
            password_label.grid(row=5, column=0, pady=0)
            password_entry.grid(row=6, column=0, pady=6)

            # Create a label for invalid username, text will be configured later
            inv_user_label = customtkinter.CTkLabel(self, text="", text_color="red")
            inv_pwd_label = customtkinter.CTkLabel(self, text="", text_color="red")

            # File path for registration: ChatGPT helped me come to this solution
            registration_file_path = Path(__file__).parent / "files/priv/creds.json"

            def check_registration():
                # ChatGPT instructed me for the implementation of multiple user accounts
                data = load_users(registration_file_path)
                
                user = username_entry.get()
                self.username = user
                password = password_entry.get()

                # Followed AI's instructions to optimise the criteria
                invalid_usr = (not user.isalnum() or len(user) < 2 or user in data["users"])        

                if invalid_usr:
                    # Check if Username Already Exits
                    if user in data["users"]:
                        inv_user_label.configure(text="Username already exists")
                        inv_user_label.grid(row=4, column=0)

                    # Check if Username contains special characters
                    elif not user.isalnum():
                        inv_user_label.configure(text="Username must be alphanumeric")
                        inv_user_label.grid(row=4, column=0)

                    # Check if Username is less than two characters long
                    elif len(user) < 2:
                        inv_user_label.configure(text="Username must be at least 2 characters")
                        inv_user_label.grid(row=4, column=0)                            

                else:
                    # Remove Message when valid
                    inv_user_label.grid_remove()

                # Password validation: ChatGPT suggested this as a cleaner approach
                # Assume password is valid
                error_msg = None

                # Check for each case where password would be invalid
                if "<" in password or ">" in password:
                    error_msg = "Must not contain '<' or '>'"

                elif len(password) < 8:
                    error_msg = "Must be at least 8 characters"

                elif password.isalnum():
                    error_msg = "Must contain at least one special character"

                # If the password is invalid, display the appropriate error message
                # Then set the invalid password tag to true to indicate an invalid password attempt
                if error_msg:
                    inv_pwd_label.configure(text=error_msg)
                    inv_pwd_label.grid(row=7, column=0)
                    invalid_pwd = True

                # Otherwise, remove the invalid password text if it was previously displayed
                else:
                    inv_pwd_label.grid_remove()
                    invalid_pwd = False

                # If both username and password are valid, display the next screen
                if not invalid_usr and invalid_pwd == False:
                    data["users"][user] = {"password_hash": hash_password(password)}
                    save_users(registration_file_path, data)
                    self.show_clock()
            
            # Keybinds to move to next field
            username_entry.bind("<Tab>", lambda _: password_entry.focus())
            password_entry.bind("<Return>",  lambda _: check_registration())
            
            # Register Button to create an account
            register_button = customtkinter.CTkButton(self, text="Register", corner_radius=50, command=check_registration)
            register_button.grid(row=8, column=0, padx=10, pady=(16,10), sticky="n")

            # Back Button to return to title screen
            back_button = customtkinter.CTkButton(self, text="Back", corner_radius=50, command=self.go_to_title)
            back_button.grid(row=9, column=0, padx=10, pady=10, sticky="n")
            
            # I had to learn this. This inserts the element into the desired position, without the constraints of a grid.
            # Relative coordinates ensure that when the window is being scaled, the button always stays in the same place.
            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

            # Refresh app
            self.update_idletasks()

        build()
    
    def login(self):
        def build():
            # Clear screen
            self.clear()

            # Reconfigure rows
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(9, weight=1)

            # Login screen title
            customtkinter.CTkLabel(self, text="Login", font=self.login_font).grid(row=1, column=0, pady=(0, 10))

            # Username text & entry
            username_label = customtkinter.CTkLabel(self, text="Username")
            username_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), width=220)
            username_label.grid(row=2, column=0, pady=0)
            username_entry.grid(row=3, column=0, pady=6)

            # Password text & entry
            password_label = customtkinter.CTkLabel(self, text="Password")
            password_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), show="*", width=220)
            password_label.grid(row=5, column=0, pady=0)
            password_entry.grid(row=6, column=0, pady=6)

            # Invalid Username Message
            inv_user_label = customtkinter.CTkLabel(self, text="", text_color="red")

            # Invalid Password Message
            inv_pwd_label = customtkinter.CTkLabel(self, text="", text_color="red")

            # Registration file to check
            registration_file_path = Path(__file__).parent / "files/priv/creds.json"

            # ChatGPT instructed me to do this: extract data from users
            data = load_users(registration_file_path)

            def check_login():
                    # Followed ChatGPT's instructions to optimise the criteria
                    # ChatGPT instructed me for the password hashing

                    user = username_entry.get()
                    self.username = user
                    password = password_entry.get()

                    valid_usr = False
                    valid_pwd = False

                    # Check whether the username exists.
                    if user not in data["users"]:
                        inv_user_label.configure(text="Username Does Not Exist")
                        inv_user_label.grid(row=4, column=0)
                        return
                    
                    else:
                        # Remove Message when valid
                        inv_user_label.grid_remove()
                        valid_usr = not valid_usr

                    # Identify stored encrypted password
                    stored_hash = data["users"][user]["password_hash"]                    

                    # Check stored hash against the encrypted password
                    if hash_password(password) != stored_hash:
                        inv_pwd_label.configure(text="Wrong password")
                        inv_pwd_label.grid(row=7, column=0)
                        return
                    
                    else:
                        inv_pwd_label.grid_remove()
                        valid_pwd = not valid_pwd
                    
                    # If both the user and password are valid show the next page
                    if valid_usr and valid_pwd:
                        self.show_clock()

            # Keyboard Navigation for login screen
            username_entry.bind("<Tab>", lambda _: password_entry.focus())
            password_entry.bind("<Return>",  lambda _: check_login())

            # Login Button
            login_button = customtkinter.CTkButton(self, text="Login", corner_radius=50, command=check_login)
            login_button.grid(row=8, column=0, padx=10, pady=(16,10), sticky="n")

            # Back Button to return to title screen
            back_button = customtkinter.CTkButton(self, text="Back", corner_radius=50, command=self.go_to_title)
            back_button.grid(row=9, column=0, padx=10, pady=10, sticky="n")

            # Place the theme button so it always stays in the top right corner
            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
            self.update_idletasks()
        build()

    def show_clock(self):
        self.logged_in = True
        self.history.clear()
        def build():
            # Clear screen
            self.clear()

            # Configure Rows
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(4, weight=1)

            # Welcome Text
            customtkinter.CTkLabel(self, text=f"Welcome, {self.username}", font=("Helvetica", 18), text_color="gray60").grid(row=1, column=0, pady=(0, 6))

            # It's important to display the Welcome text before and therefore outside of the frame to because I want the text to be above the clock (UI decision)

            # Build the clock interface
            # Note it is important to use .grid() separately in order to display the elements properly (ChatGPT helped me discover this)

            # Create a Frame to store clock details
            clock_frame = customtkinter.CTkFrame(self, fg_color="transparent")
            clock_frame.grid(row=2, column=0)
            
            # Define the fonts (with help from Claude Code)
            clock_font = customtkinter.CTkFont(family="Helvetica", size=64, weight="bold")
            am_pm_font  = customtkinter.CTkFont(family="Helvetica", size=28, weight="bold")

            # Display the clock
            time_label = customtkinter.CTkLabel(clock_frame, text="", font=clock_font, fg_color="transparent")
            time_label.grid(row=0, column=0, padx=(0, 8))

            # Display an AM/PM label
            am_pm = customtkinter.CTkLabel(clock_frame, text="", font=am_pm_font, text_color="#534AB7", fg_color="transparent")
            am_pm.grid(row=0, column=1)

            # Home button
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home)
            home_btn.grid(row=3, column=0, pady=20)

            # Followed instructions from Claude Code, converts datetime into string, same with AM/PM, update every 1000ms or 1s
            def tick():
                now = datetime.now()
                # Convert datetime into string
                time_label.configure(text=now.strftime("%I:%M:%S"))
                am_pm.configure(text=now.strftime("%p"))
                # Update every 1000ms (1s for those who don't know)
                self.clock_job = self.after(1000, tick)

            tick()
        build()

    def go_home(self):

        # Clear History
        self.history.clear()
        
        def build():
            self.clear()

            # Configure rows for the home screen interface
            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=0)
            self.grid_rowconfigure(3, weight=1)
            self.grid_rowconfigure(4, weight=1)
            self.grid_rowconfigure(5, weight=0)

            # Use datetime to obtain the hour data and output difference greetings based on the time
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

            # Display Date and Time based on Actual Date and Time
            def tick_strip():
                # Obtain current datetime
                now = datetime.now()
                # Configure the text to display datetime (including AM/PM)
                clock_strip.configure(text=now.strftime("%A, %B %d  •  %I:%M:%S %p"))
                # Update after 1000ms(1s)
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

            # Configure Cursor
            if sys.platform == "darwin":
                cursor = "hand"

            else:
                cursor = "hand2"

            # Create empty list for cards 
            widgets, widget_colors = [], []
            for col, (label, color, cmd) in enumerate(functions):
                card = customtkinter.CTkFrame(panel_frame, fg_color=color, corner_radius=12, cursor=cursor)
                card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
                card.grid_rowconfigure(0, weight=1)
                card.grid_columnconfigure(0, weight=1)

                # Display text for each function
                customtkinter.CTkLabel(card, text=label, font=("Helvetica", 13), fg_color="transparent", justify="center").grid(row=0, column=0, padx=12, pady=20)

                # Keybinds for each of the functions: Claude instructed me to do this
                card.bind("<Button-1>", lambda e, c=cmd: c())
                for child in card.winfo_children():
                    child.bind("<Button-1>", lambda e, c=cmd: c())

                widgets.append(card)
                widget_colors.append(color)

            # Logout Button
            logout_btn = customtkinter.CTkButton(self, text="Log Out", corner_radius=50, fg_color="transparent", border_width=1, border_color="gray30", text_color="gray50",
                                                hover_color="#1a1a1a", command=self.logout).grid(row=4, column=0, pady=20)

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

            # Configure Rows
            self.grid_rowconfigure(0, weight=1)
            
            # Create Frame for settings
            SettingsFrame(self, self.settings, on_apply=self.on_settings_apply).grid(row=0, column=0, sticky="nsew")

            # Display home button
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

            # Configure rows
            self.grid_rowconfigure(0, weight=1)

            # Create Frame for calendar file
            CalendarFrame(self).grid(row=0, column=0, sticky="nsew")

            # Display home button
            home_btn = customtkinter.CTkButton(self, text="⌂  Home", corner_radius=50, command=self.go_home).grid(row=1, column=0, pady=10)
        build()

    def logout(self):
        # Reset Login State
        self.logged_in = False

        # Reset History State
        self.history.clear()
        
        def build():
            self.clear()

            # Configure Rows
            self.grid_rowconfigure(0, weight=3)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=1)

            # Title
            self.ui_title = customtkinter.CTkLabel(self, text=app_name, font=self.responsive_font, fg_color="transparent")
            self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

            # Login Button
            login_btn = customtkinter.CTkButton(self, text="Login", corner_radius=50, command=self.login)
            login_btn.grid(row=1, column=0, padx=10, pady=10, sticky="n")
            
            # Register Button
            register_btn = customtkinter.CTkButton(self, text="Register", corner_radius=50, command=self.login)
            register_btn.grid(row=2, column=0, padx=10, pady=10, sticky="n")

            # Theme Button
            self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        build()