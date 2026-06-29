import customtkinter as ctk
from pathlib import Path

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

class SettingsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, settings, on_apply):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        # Callback invoked with the new settings dict when Apply is pressed
        self.on_apply = on_apply

        # Configure Rows & Columns
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        # Appearance section heading
        section_label(self, row=1, text="Appearance")
        # Holds the currently selected appearance mode string
        self.appearance_var = ctk.StringVar(value=settings["appearance"])
        # Radio buttons for Light / Dark / System
        option_row(self, [(m, m) for m in APPEARANCE_OPTIONS], self.appearance_var, start_row=2)

        # Font size section heading
        section_label(self, row=3, text="Font Size")
        # Holds the currently selected font scale multiplier
        self.scale_var = ctk.DoubleVar(value=settings["font_scale"])
        # Radio buttons for Small / Medium / Large / Extra Large
        option_row(self, FONT_SIZE_OPTIONS, self.scale_var, start_row=4)

        # Pill-shaped button that saves the current selections
        apply_button = ctk.CTkButton(self, text="Apply", fg_color=PURPLE, hover_color=PURPLE_HOVER, corner_radius=50, font=ctk.CTkFont(size=14), width=140, command=self.apply)
        apply_button.grid(row=6, column=0, pady=24)

        # Data management section heading
        section_label(self, row=7, text="Data")
        # Card that wraps the delete button
        data_card = ctk.CTkFrame(self, fg_color=("gray88", "gray17"), corner_radius=12)
        data_card.grid(row=8, column=0, padx=20, pady=(0, 4), sticky="ew")
        data_card.grid_columnconfigure(0, weight=1)
        # Red-text button that triggers the confirmation dialog before deleting
        ctk.CTkButton(data_card, text="Delete All Data", fg_color="transparent", hover_color=("gray80", "gray30"), text_color=("#A32D2D", "#F09595"),
                      font=ctk.CTkFont(size=13), anchor="w", command=self.confirm_delete).grid(row=0, column=0, padx=20, pady=6, sticky="w")
    
    def apply(self):
        # Pass the current variable values back to the parent as a settings dict
        self.on_apply({"appearance": self.appearance_var.get(), "font_scale": self.scale_var.get()})

    # Followed Claude's instructions: Delete Data
    def confirm_delete(self):
        # White in light mode, black in dark mode
        dialog = ctk.CTkToplevel(self, fg_color=("white", "black"))
        dialog.title("Delete All Data")
        dialog.geometry("340x160")
        dialog.resizable(False, False)

        # Block interaction with the main window until this dialog is closed
        dialog.grab_set()
        # Warning message describing what will be deleted
        ctk.CTkLabel(dialog, text="This will permanently delete all events,\ntasks, notes, and flashcards.", font=ctk.CTkFont(size=13)).pack(pady=(24, 16))
        # Row that holds the two action buttons side by side
        button_row = ctk.CTkFrame(dialog, fg_color="transparent")
        button_row.pack()
        # Ghost-outlined button that dismisses the dialog without deleting
        ctk.CTkButton(button_row, text="Cancel", width=120, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), hover_color=("gray80", "gray25"),
                      command=dialog.destroy).pack(side="left", padx=(0, 8))
        # Red destructive button; calls delete then closes the dialog
        ctk.CTkButton(button_row, text="Delete", width=120, fg_color="#A32D2D", hover_color="#7A1F1F", command=lambda: [self.delete_all_data(), dialog.destroy()]).pack(side="left")

    def delete_all_data(self):
        # Remove files for each function
        for path in [
            Path("files/events/events.json"),
            Path("files/todo/todo.json"),
            Path("files/flashcards/flashcards.json"),
            Path("files/notes/notes.json"),
        ]:
            if path.exists():
                path.unlink()
        for txt in Path("files/notes").glob("*.txt"):
            txt.unlink()