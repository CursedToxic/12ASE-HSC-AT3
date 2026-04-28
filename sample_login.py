import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# 1. Create the application window with a theme
app = ttk.Window(themename="cyborg")
app.title("Login Screen")
app.geometry("800x600")

# 2. Function to handle login
def check_login():
    user = username_entry.get()
    password = password_entry.get()
    print(f"User: {user}, Password: {password}")
    
    invalid_usr = True
    invalid_pwd = True
    inv_user = ttk.Label(app, text="Invalid Username", bootstyle="warning")
    inv_password = ttk.Label(app, text="Invalid Password", bootstyle="warning")

    if user.isalnum() == False or len(password) < 8 or "<" in password or ">" in password:
        if user.isalnum() == False:
            invalid_usr == True
            inv_user.pack(pady=10)
        if len(password) < 8 or "<" in password or ">" in password:
            invalid_pwd == True
            inv_password.pack(pady=10)

    else:
        for widget in app.winfo_children():
            widget.destroy()
        
        successful_signin = ttk.Label(app, text="Successful Login")
        successful_signin.pack(pady=100)

    # Add authentication logic here

# 3. Create Widgets
label = ttk.Label(app, text="Login", font=("Helvetica", 24), bootstyle="light")
label.pack(pady=30)

username_entry = ttk.Entry(app, font=("Helvetica", 12))
username_entry.insert(0, "Username")
username_entry.pack(pady=10)

password_entry = ttk.Entry(app, font=("Helvetica", 12), show="*")
password_entry.insert(0, "Password")
password_entry.pack(pady=10)

# 4. Use themed buttons (info, primary, danger, etc.)
login_btn = ttk.Button(
    app, 
    text="Submit", 
    command=check_login
)
login_btn.pack(pady=20)

app.mainloop()
