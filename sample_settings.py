import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# --- Functions ---
# Create new note
    for widget in app.winfo_children():
            widget.destroy()

    successful_signin = ttk.Label(app, text="New note has been created")
    successful_signin.pack(pady=100)

# Create the main window
app = ttk.Window(themename="superhero") # Modern theme
app.title("Note creation")
app.geometry("1000x600")

# --- Layout ---
# Sidebar
sidebar = ttk.Frame(app, bootstyle="light")
sidebar.pack(side=LEFT, fill=Y)

# Main Content Area
content = ttk.Frame(app, padding=10)
content.pack(side=RIGHT, fill=BOTH, expand=True)

# Sidebar Components
title_label = ttk.Label(sidebar, text="Workspace", font=("Helvetica", 16, "bold"), bootstyle="inverse-light")
title_label.pack(pady=20, padx=10)

add_btn = ttk.Button(sidebar, text="+ Add Page", bootstyle="info-outline", command=new_note)
add_btn.pack(pady=10)

# Main Text Editor
editor = ttk.Text(content, font=("Helvetica", 12), wrap=WORD)
editor.pack(fill=BOTH, expand=True)

app.mainloop()