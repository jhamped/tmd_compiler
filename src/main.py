from lexical_analyzer import *
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage, filedialog
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

# File operations
def open_file():
    # Restrict file dialog to .tmd files primarily
    file_path = filedialog.askopenfilename(
        filetypes=[("TMD Files", "*.tmd"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            if not file_path.endswith(".tmd"):
                raise ValueError("Only .tmd files are supported.")
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                textFrame.delete("1.0", tk.END)
                textFrame.insert("1.0", content)

            # Extract the file name from the file path
            file_name = file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
            file_name_label.config(text=file_name)  # Update the navigation bar label
            
            window.title(f"TMD Compiler - {file_path}")  # Update window title
            update_line_numbers()
        except Exception as e:
            console.insert(tk.END, f"Error opening file: {str(e)}\n", "error")

def save_as_file():
    # Force .tmd as the effective extension
    file_path = filedialog.asksaveasfilename(
        defaultextension=".tmd",
        filetypes=[("TMD Files", "*.tmd")]
    )
    if file_path:
        try:
            # Ensure the file path ends with .tmd
            if not file_path.endswith(".tmd"):
                file_path += ".tmd"
            with open(file_path, "w", encoding="utf-8") as file:
                content = textFrame.get("1.0", "end-1c")
                file.write(content)

                # Extract the file name from the file path
            file_name = file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
            file_name_label.config(text=file_name)  # Update the navigation bar label
            
            window.title(f"TMD Compiler - {file_path}")  # Update window title
        except Exception as e:
            console.insert(tk.END, f"Error saving file: {str(e)}\n", "error")

def clear_click(event=None):
    for item in table.get_children():
        table.delete(item)
    textFrame.delete("1.0", tk.END)
    console.delete("1.0", tk.END)
    lexeme.clear()
    token.clear()
    state.clear()
    update_line_numbers()
    window.title("TMD Compiler")
    file_name_label.config(text="") 

# Console close button event
def consoleClose_click(event):
    if console_open.get():
        console.pack_forget()
        consoleClose.config(text="˄")
    else:
        console.pack(side="bottom", fill="both")
        consoleClose.config(text="˅")
    console_open.set(not console_open.get())

# Lexical button event
def on_enter_lexical(event):
    lexicalBtn.config(fg="white")
def on_leave_lexical(event):
    lexicalBtn.config(fg="black")
def lexical_click(event):
    for item in table.get_children():
        table.delete(item)
    console.delete("1.0", tk.END)
    code = textFrame.get("1.0", "end")
    lexer(code, console, table)

# File button event
def on_enter_file(event):
    file_menu_button.config(fg="white")
def on_leave_file(event):
    file_menu_button.config(fg="black")

# Menu drawer event
def show_file_menu(event):
    x = file_menu_button.winfo_rootx()
    y = file_menu_button.winfo_rooty() + file_menu_button.winfo_height()
    file_menu.post(x, y)

def insert_tab(event):
    textFrame.insert(tk.INSERT, ' ' * 3)
    return "break"

# Function to update the line numbers
def update_line_numbers(event=None):
    line_numbers = ""
    
    line_count = int(textFrame.index('end-1c').split('.')[0])
    
    for i in range(1, line_count + 1):
        if i == 1:
            line_numbers += f"{i}"
        else:
            line_numbers += f"\n{i}"
    
    lineTextBox.config(state="normal")
    lineTextBox.delete("1.0", "end")  
    lineTextBox.insert("1.0", line_numbers, "right")  
    lineTextBox.config(state="disabled")

def on_text_change(event=None):
    update_line_numbers()
    synchronize_scroll()

def synchronize_scroll():
    text_frame_scroll_position = textFrame.yview()
    lineTextBox.yview_moveto(text_frame_scroll_position[0])

def multiple_yview(*args):
    lineTextBox.yview(*args)
    textFrame.yview(*args)

# Auto-close marker function
def auto_close(event, text_widget):
    closing_markers = {
        '"': '"',
        "'": "'",
        '{': '}', #CHANGED
        '[': ']',
        '(': ')',
        '<': '>>',
        '/*': '\n\n*/'
    }

    cursor_index = text_widget.index(tk.INSERT)
    preceding_char = text_widget.get(f"{cursor_index} - 1c")

    if event.char == "<":
        if preceding_char == "<":
            text_widget.insert(tk.INSERT, "<")
            text_widget.insert(tk.INSERT, ">>")
            text_widget.mark_set(tk.INSERT, f"{cursor_index} + 1c")
            return "break"
        else:
            text_widget.insert(tk.INSERT, "<")
            return "break"

    if event.char == "*" and preceding_char == "/":
        text_widget.insert(tk.INSERT, "*")
        text_widget.insert(tk.INSERT, closing_markers['/*'])
        text_widget.mark_set(tk.INSERT, f"{cursor_index} + 2c")
        return "break"

    elif event.char in closing_markers and event.char != "*":
        text_widget.insert(tk.INSERT, event.char)
        current_pos = text_widget.index(tk.INSERT)
        closing_marker = closing_markers[event.char]

        if event.char == '{':
            text_widget.insert(current_pos, closing_marker)
            text_widget.mark_set(tk.INSERT, f"{current_pos} + 0c")
        else:
            text_widget.insert(current_pos, closing_marker)
            text_widget.mark_set(tk.INSERT, current_pos)
        return "break"


# Main window
window = tk.Tk()
window.title("TMD Compiler")
icon = PhotoImage(file="TMD_Compiler/assets/TMD_Logo.png")
window.iconphoto(False, icon)
window.wm_state('zoomed')
dark_title_bar(window)

console_open = tk.BooleanVar(value=True)

# Left panel
environFrame = tk.Frame(window, bg="#202020")
environFrame.pack(side="left", fill="both", expand=True)

# Navigation bar
navFrame = tk.Frame(environFrame, bg="#a6b3f1", height=8)
navFrame.pack(side="top", fill="x")

# File name label (centered)
file_name_label = tk.Label(
    navFrame, text="", font=("Helvetica", 10, "bold"), bg="#a6b3f1", fg="black"
)
file_name_label.place(relx=0.5, rely=0.5, anchor="center")  # Center-aligned

# File drawer (Menu button for File operations)
file_menu_button = tk.Label(navFrame, text="File", font=("Helvetica", 11, "bold"), bg="#a6b3f1", fg="black")
file_menu_button.pack(side="left", pady=5, padx=(15, 0))
file_menu_button.bind("<Button-1>", show_file_menu)
file_menu_button.bind("<Enter>", on_enter_file)
file_menu_button.bind("<Leave>", on_leave_file)

# Load and resize icons 
open_icon = tk.PhotoImage(file="TMD_Compiler/assets/open_icon.png").subsample(50, 50)  
save_icon = tk.PhotoImage(file="TMD_Compiler/assets/save_icon.png").subsample(50, 50)
new_icon = tk.PhotoImage(file="TMD_Compiler/assets/_new_icon.png").subsample(50, 50)

# File menu
file_menu = tk.Menu(file_menu_button, tearoff=0, bg="#a6b3f1", fg="black", font=("Helvetica", 10))
file_menu.add_command(label="New", image=new_icon, compound="left", command=clear_click)
file_menu.add_command(label="Open", image=open_icon, compound="left", command=open_file)
file_menu.add_command(label="Save", image=save_icon, compound="left", command=save_as_file)

# Lexical button
lexicalBtn = tk.Label(navFrame, text="Lexical", font=("Helvetica", 11, "bold"), bg="#a6b3f1", borderwidth=1, relief="solid", width=8)
lexicalBtn.pack(side="right", pady=5, padx=(0, 15))
lexicalBtn.bind("<Button-1>", lexical_click)
lexicalBtn.bind("<Enter>", on_enter_lexical)
lexicalBtn.bind("<Leave>", on_leave_lexical)

# Code frame
codeFrame = tk.Frame(environFrame, bg="#202020")
codeFrame.pack(side="top", fill="both", expand=True)

#style scrollbar
scrollStyle = ttk.Style()
scrollStyle.theme_use("clam")
scrollStyle.configure("Black.Vertical.TScrollbar", background="#393939", troughcolor="#202020", arrowcolor="#A3A3A3", bordercolor="#393939")
scrollStyle.map("Black.Vertical.TScrollbar",background=[("active", "#393939"), ("disabled", "#393939")],)

code_scroll = ttk.Scrollbar(codeFrame, style="Black.Vertical.TScrollbar")

# Line numbers (lineTextBox)
lineTextBox = tk.Text(codeFrame, width=4, bg="#202020", fg="white", font=("Courier New", 13), insertbackground="black", padx=5, yscrollcommand=code_scroll.set, wrap="none", state="disabled")
lineTextBox.pack(side="left", fill="y", padx=(5, 0), pady=5)
lineTextBox.tag_configure("right", justify="right")

# Text editor (textFrame)
textFrame = tk.Text(codeFrame, height=25, bg="#272727", fg="white", font=("Courier New", 13), insertbackground="white", padx=5, yscrollcommand=code_scroll.set, wrap="none")
textFrame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
textFrame.bind("<Tab>", insert_tab) #CHANGED

# Bind the auto-close function to the relevant keys
keys_to_bind = ['"', "'", '{', '[', '(', '<', '*', '/']
for key in keys_to_bind:
    textFrame.bind(f"<Key-{key}>", lambda event, widget=textFrame: auto_close(event, widget))

textFrame.config(yscrollcommand=code_scroll.set)
lineTextBox.config(yscrollcommand=code_scroll.set)

code_scroll.pack(side="right", fill="y")
code_scroll.config(command=multiple_yview)

textFrame.bind("<KeyRelease>", on_text_change)
textFrame.bind("<Configure>", on_text_change)

# Console frame
consoleFrame = tk.Frame(environFrame, bg="#202020")
consoleFrame.pack(side="bottom", fill="both")

# Console panel
consolePanel = tk.Frame(consoleFrame, bg="#202020", height=3)
consolePanel.pack(side="top", fill="both")

# Console close button
consoleClose = tk.Label(consolePanel, text="˅", font=("Consolas", 13), fg="#ffffff", bg="#202020")
consoleClose.pack(side="right", pady=(7, 0), padx=(0, 15))
consoleClose.bind("<Button-1>", consoleClose_click)

textFrame.bind("<MouseWheel>", lambda event: synchronize_scroll())  
lineTextBox.bind("<MouseWheel>", lambda event: synchronize_scroll()) 

# Console
console = tk.Text(consoleFrame, bg="#202020", height=15, fg="white", font=("Consolas", 12), padx=10, pady=10, borderwidth=1, relief="solid")
console.pack(side="bottom", fill="both")
console.tag_configure("error", foreground="#b23232", font=("Consolas", 12, "bold"))
console.tag_configure("ln_col", foreground="#a8a8a8", font=("Consolas", 12))
console.tag_configure("expected", foreground="#bf384c", font=("Consolas", 12)) #CHANGED

# Right panel
tableFrame = tk.Frame(window, width=500, bg="#dee4ff")
tableFrame.pack(side="right", fill="both")

#----------CHANGED-----------
headingStyle = ttk.Style()
headingStyle.configure("Custom.Treeview.Heading", font=("Helvetica", 10), background="#f5f6fe", relief="flat")
headingStyle.map("Custom.Treeview.Heading", background=[("active", "#dee4ff")])

table = ttk.Treeview(tableFrame, columns=("Lexeme", "Token"), show="headings", style="Custom.Treeview")
table.heading("#1", text="Lexeme")
table.heading("#2", text="Token")
table.pack(fill="both", expand=True)
#---------CHANGED-----------

window.mainloop()
