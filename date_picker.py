import customtkinter as ctk
from ctkdateentry import CTkDateEntry, CTkStringVar
from tkinter import *

root = ctk.CTk()

root.geometry('200x200')
root.title('CTkDateEntry')

var = CTkStringVar(root, value='Enter a Date') #Variable that will be inserted in CTkDateEntry

date_entry = CTkDateEntry(root,
    width=150,
    variable =var,
    justify ='left',
    font=('Roboto', 14, 'bold'),
    )
date_entry.pack(pady=50)

print(var.get())

root.mainloop()