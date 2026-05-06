import customtkinter
from task_checkbox import *
from radio_button import *

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        global tasks

        self.title("Task Creator")
        self.geometry("640x480")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        tasks = []
        
        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Tasks", values=tasks)
        self.scrollable_checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.button = customtkinter.CTkButton(self,text="+ New Task", command=self.create_task)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="nw", columnspan=2)

    def create_task(self):
        global value

        value = customtkinter.CTkEntry(self, placeholder_text="Click to Insert Text...")
        value.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="new")

        entry = self.button = customtkinter.CTkButton(self,text="+ Create", command=self.insert_text)
        entry.grid(row=3, column=0, padx=10, pady=10, sticky="ne", columnspan=2)

    def insert_text(self):
        text = value.get()

        # Add to list of tasks
        tasks.append(text)

        # Display added task
        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Tasks", values=tasks)
        self.scrollable_checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Clear entry field
        value.delete(0, "end")

app = App()

app.mainloop()