from task_checkbox import * 
from ctkdateentry import CTkDateEntry, CTkStringVar

class Task(customtkinter.CTkScrollableFrame):
    def __init__(self):
        super().__init__()

        global tasks

        tasks = []
            
        self.scrollable_checkbox_frame = MyCheckboxFrame(self, title="Tasks", values=tasks)
        self.scrollable_checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.button = customtkinter.CTkButton(self,text="+ New Task", command=self.create_task)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="nw", columnspan=2)

    def create_task(self):
        global value
        global var

        value = customtkinter.CTkEntry(self, placeholder_text="Click to Insert Text...")
        value.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsw")
        
        var = CTkStringVar(self, value='Enter a Date') #Variable that will be inserted in CTkDateEntry

        date_entry = CTkDateEntry(self,
            width=150,
            variable =var,
            justify ='left')
        date_entry.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nse")

        entry = self.button = customtkinter.CTkButton(self,text="+ Create", command=self.insert_text)
        entry.grid(row=3, column=0, padx=10, pady=10, sticky="ne", columnspan=2)

    def insert_text(self):
        text = value.get()
        date = var.get()

        # Add to list of tasks
        tasks.append(f'{text} -> {date}')

        # Display added task
        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Tasks", values=tasks)
        self.scrollable_checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Clear entry field
        value.delete(0, "end")
