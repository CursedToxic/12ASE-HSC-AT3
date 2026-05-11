import tkinter as tk
import ttkbootstrap as ttk
from function import *
import webbrowser

root = ttk.Window(themename="cyborg")
root.title("Study App Basic GUI")
root.geometry("1280x720")

wide = 640

root.minsize(width=wide, height=480)

text = ttk.Label(root, text="Basic Study App", font=("Helvetica", 36))
text.pack(expand=True, fill=tk.BOTH, padx=(wide)/2, pady=15)

def signon():
    msg = ttk.Label(root, text="You have logged on.")
    msg.pack(pady=15)

def open_website():
    webbrowser.open("index.html")

login = ttk.Button(root, command=open_website, text="Login")
login.pack(pady=25)

def resize_text(event):
    # Calculate font size based on window width
    new_font_size = int(event.width/20)
    if new_font_size < 36:  # Set a minimum font size
        new_font_size = 36
    text.config(font=("Helvetica", new_font_size))

root.bind("<Configure>", resize_text)

root.mainloop()