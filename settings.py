import customtkinter as ctk

PURPLE       = "#534AB7"
PURPLE_HOVER = "#3C3489"

FONT_SIZE_OPTIONS = [("Small",  0.85), ("Medium", 1.0), ("Large",  1.2), ("Extra Large", 1.5)]

APPEARANCE_OPTIONS = ["Light", "Dark", "System"]

def section_label(parent, row, text):
    ctk.CTkLabel(parent, text=text.upper(), font=ctk.CTkFont(size=11), text_color="gray50").grid(row=row, column=0, padx=20, pady=(16, 4), sticky="w")


def option_row(parent, options, current_var, start_row):
    card = ctk.CTkFrame(parent, fg_color=("gray88", "gray17"), corner_radius=12)
    card.grid(row=start_row, column=0, padx=20, pady=(0, 4), sticky="ew")
    card.grid_columnconfigure(0, weight=1)
    for i, (label, value) in enumerate(options):
        top_pad = 12 if i == 0 else 4
        bottom_pad = 12 if i == len(options) - 1 else 4
        ctk.CTkRadioButton(card, text=label, variable=current_var, value=value, fg_color=PURPLE, hover_color=PURPLE_HOVER,
                           font=ctk.CTkFont(size=13)).grid(row=i, column=0, padx=20, pady=(top_pad, bottom_pad), sticky="w")


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, settings, on_apply):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.on_apply = on_apply
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        # Title
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        section_label(self, row=1, text="Appearance")
        self.appearance_var = ctk.StringVar(value=settings["appearance"])
        option_row(self, [(m, m) for m in APPEARANCE_OPTIONS], self.appearance_var, start_row=2)

        section_label(self, row=3, text="Font Size")
        self.scale_var = ctk.DoubleVar(value=settings["font_scale"])
        option_row(self, FONT_SIZE_OPTIONS, self.scale_var, start_row=4)

        apply_btn = ctk.CTkButton(self, text="Apply", fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=50, font=ctk.CTkFont(size=14), width=140,command=self.apply)
        apply_btn.grid(row=6, column=0, pady=24)

    def apply(self):
        self.on_apply({"appearance": self.appearance_var.get(), "font_scale": self.scale_var.get()})