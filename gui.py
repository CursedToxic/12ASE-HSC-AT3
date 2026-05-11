import customtkinter
from datetime import datetime
from task_creator import *
from radio_button import *
 
 
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Basic Study App")
        self.geometry("640x480")
        self.configure(fg_color="#000000")
 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
 
        self.responsive_font = customtkinter.CTkFont(family="Helvetica", size=24)
        self._clock_job = None
 
        self.ui_title = customtkinter.CTkLabel(
            self, text="Basic Study App", font=self.responsive_font,
            fg_color="transparent"
        )
        self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
 
        login_button = customtkinter.CTkButton(
            self, text="Login", corner_radius=50, command=self.login_system
        )
        login_button.grid(row=1, column=0, padx=10, pady=10, sticky="n")
 
        self.bind("<Configure>", self.handle_resize)
        self.after(10, self._initial_scale)
 
    # ── Responsive font ───────────────────────────────────────────────────────
 
    def _initial_scale(self):
        width = self.winfo_width()
        self._apply_scale(width if width > 1 else 640)
 
    def handle_resize(self, event):
        if event.widget != self:
            return
        self._apply_scale(event.width)
 
    def _apply_scale(self, width):
        calculated_size = int(width / 25)
        new_size = max(12, min(calculated_size, 128))
        self.responsive_font.configure(size=new_size)
        self.update_idletasks()
 
    # ── Login screen ──────────────────────────────────────────────────────────
 
    def login_system(self):
        if self._clock_job:
            self.after_cancel(self._clock_job)
            self._clock_job = None
 
        for widget in self.winfo_children():
            widget.destroy()
 
        for r in range(8):
            self.grid_rowconfigure(r, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
 
        customtkinter.CTkLabel(self, text="Login", font=("Helvetica", 24)).grid(
            row=1, column=0, pady=(0, 10))
 
        username_entry = customtkinter.CTkEntry(self, font=("Helvetica", 12), width=220)
        username_entry.insert(0, "Username")
        username_entry.grid(row=2, column=0, pady=6)
 
        password_entry = customtkinter.CTkEntry(
            self, font=("Helvetica", 12), show="*", width=220)
        password_entry.insert(0, "Password")
        password_entry.grid(row=3, column=0, pady=6)
 
        inv_user_label = customtkinter.CTkLabel(
            self, text="Invalid Username", text_color="orange")
        inv_pwd_label = customtkinter.CTkLabel(
            self, text="Invalid Password", text_color="orange")
        inv_user_label.grid(row=4, column=0)
        inv_pwd_label.grid(row=5, column=0)
        inv_user_label.grid_remove()
        inv_pwd_label.grid_remove()
 
        def check_login():
            user = username_entry.get()
            password = password_entry.get()
 
            invalid_usr = not user.isalnum()
            invalid_pwd = (
                len(password) < 8 or "<" in password or ">" in password
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
 
        customtkinter.CTkButton(self, text="Submit", command=check_login).grid(
            row=6, column=0, pady=16)
 
    # ── Clock screen ──────────────────────────────────────────────────────────
 
    def show_clock(self):
        for widget in self.winfo_children():
            widget.destroy()
 
        for r in range(5):
            self.grid_rowconfigure(r, weight=0)
        self.grid_rowconfigure(0, weight=1)   # top spacer
        self.grid_rowconfigure(4, weight=1)   # bottom spacer
 
        customtkinter.CTkLabel(
            self, text="Welcome", font=("Helvetica", 18),
            text_color="gray60"
        ).grid(row=1, column=0, pady=(0, 6))
 
        # ── Time + AM/PM side by side in a frame ──
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
 
        # ── Home button ──
        customtkinter.CTkButton(
            self, text="⌂  Home", corner_radius=50,
            command=self.go_home
        ).grid(row=3, column=0, pady=20)
 
        def tick():
            now = datetime.now()
            time_label.configure(text=now.strftime("%I:%M:%S"))
            ampm_label.configure(text=now.strftime("%p"))
            self._clock_job = self.after(1000, tick)
 
        tick()
 
    # ── Home screen ───────────────────────────────────────────────────────────
 
    def go_home(self):
        if self._clock_job:
            self.after_cancel(self._clock_job)
            self._clock_job = None
 
        for widget in self.winfo_children():
            widget.destroy()
 
        for r in range(3):
            self.grid_rowconfigure(r, weight=0)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
 
        self.responsive_font = customtkinter.CTkFont(family="Helvetica", size=24)
 
        self.ui_title = customtkinter.CTkLabel(
            self, text="Basic Study App", font=self.responsive_font,
            fg_color="transparent"
        )
        self.ui_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
 
        customtkinter.CTkButton(
            self, text="Login", corner_radius=50, command=self.login_system
        ).grid(row=1, column=0, padx=10, pady=10, sticky="n")
 
        self.after(10, self._initial_scale)
 
 
app = App()
app.mainloop()
 