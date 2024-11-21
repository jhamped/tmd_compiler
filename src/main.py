from lexical_analyzer import *
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
import ctypes as ct


def dark_title_bar(window):
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))

def lexical_click(event):
    code = textFrame.get("1.0", "end")
    lexer(code, console, table)

#clear button
def on_enter_new(event):
    clrBtn.config(fg="white")
def on_leave_new(event):
    clrBtn.config(fg="#343537")
def clear_click(event):
    for item in table.get_children():
        table.delete(item)
    textFrame.delete("1.0", tk.END)
    console.delete("1.0", tk.END)
    lexeme.clear()
    token.clear()

#lexical button
def on_enter_lexical(event):
    lexicalBtn.config(fg="white")
def on_leave_lexical(event):
    lexicalBtn.config(fg="black")

#main window
window = tk.Tk()
window.title("TMD Compiler")
icon = PhotoImage(file="TMD_Compiler/TMD_Logo.png")
window.iconphoto(False, icon)
window.wm_state('zoomed')
dark_title_bar(window)

#left panel
environFrame = tk.Frame(window, bg="#202020")  # Adjust the width as needed
environFrame.pack(side="left", fill="both", expand=True)

#navigation bar
navFrame = tk.Frame(environFrame, bg="#a6b3f1", height=35)
navFrame.pack(side="top", fill="x")

#clear button
clrBtn = tk.Label(navFrame, text="Clear", font=("Helvetica", 10, "bold"), bg="#a6b3f1", fg="#343537")
clrBtn.pack(side="left", pady=5, padx=(15, 0))
clrBtn.bind("<Button-1>", clear_click)
clrBtn.bind("<Enter>", on_enter_new)
clrBtn.bind("<Leave>", on_leave_new)

#lexical button
lexicalBtn = tk.Label(navFrame, text="Lexical", font=("Helvetica", 11, "bold"), bg="#a6b3f1", borderwidth=1, relief="solid", width=10)
lexicalBtn.pack(side="right", pady=5, padx=(0, 15))
lexicalBtn.bind("<Button-1>", lexical_click)
lexicalBtn.bind("<Enter>", on_enter_lexical)
lexicalBtn.bind("<Leave>", on_leave_lexical)

#textbox for code
textFrame = tk.Text(environFrame, height=25, bg="#272727", fg="white", font=("Courier New", 13), insertbackground="white", padx=5)
textFrame.pack(side="top", fill="both", expand=True)

#console
console = tk.Text(environFrame, bg="#202020", height=15, fg="white", font=("Consolas", 12))
console.pack(side="bottom", fill="both")
console.tag_configure("error", foreground="#b23232", font=("Consolas", 12, "bold"))

#right panel
tableFrame = tk.Frame(window, width=500, bg="#e5e2ed")
tableFrame.pack(side="right", fill="both")

#table
table = ttk.Treeview(tableFrame, columns=("Lexeme", "Token"))
table["show"] = "headings"
table.heading("#1", text="Lexeme")
table.heading("#2", text="Token")
table.pack(fill="both", expand=True)

window.mainloop()