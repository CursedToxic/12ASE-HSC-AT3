from gui import *

entry = ttk.Entry(root, font=("Helvetica", 18))
entry.pack(pady=10)

def change_theme(event):
    selected_theme = theme_menu.get()
    root.style.theme_use(selected_theme)

theme_menu = ttk.Combobox(root, values=root.style.theme_names(), state="readonly") # make it so that the user cannot add any themes that do not exist
theme_menu.set("Select Theme")  # Default text
theme_menu.bind("<<ComboboxSelected>>", change_theme)  # Bind the selection of the theme menu to a function that changes the theme
theme_menu.pack(pady=5)