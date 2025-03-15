from lexer import *
from parser import *
from semantic import *
import tkinter as tk
from tkinter import ttk, PhotoImage, filedialog, messagebox
import ctypes as ct

class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            if self.tab(index, 'state') == 'disabled':  # "+" tab is pressed
                self.add_new_tab(index)
                return "break"
            self.state(['pressed'])
            self._active = index
            return "break"

    def on_close_release(self, event):
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            if len(self.tabs()) > 1:
                self.forget(index)
                self.event_generate("<<NotebookTabClosed>>")
            else:
                messagebox.showwarning("Warning","Cannot close the remaining tab!")
        
        self.state(["!pressed"])
        self._active = None
    
    def __initialize_custom_style(self):
        style = ttk.Style()
        style.theme_use("alt")
        self.images = (
            tk.PhotoImage("x_close", file="assets\_x_close.png"),
            tk.PhotoImage("x_closeactive", file="assets\_x_closeactive.png"),
            tk.PhotoImage("x_closepressed", file="assets\_x_closepressed.png"),
            tk.PhotoImage("x_notselected", file="")
        )
        style.element_create("close", "image", "x_close",
                            ("active", "pressed", "!disabled", "x_closepressed"),
                            ("active", "!disabled", "x_closeactive"), 
                            ("!selected", "x_notselected"),
                            border=8, sticky='')
        style.configure("CustomNotebook", background="#1a1a1a", tabmargins=[0, -1.5, 0, 0], relief="flat")
        style.configure("CustomNotebook.Tab", padding=[0,5], relief="flat", borderwidth="0.5", width=12, anchor="center")
       
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                })
            ]
        })
        ])
        style.configure("CustomNotebook.Tab", focuscolor=style.configure(".")["background"])
        style.map(
            "CustomNotebook.Tab",
            background=[("selected", "#272727"), ("!selected", "#202020")],
            foreground=[("selected", "white"), ("!selected", "#616161")],
        )
    

class TMDCompiler:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("TMD Compiler")
        self.window.iconphoto(False, PhotoImage(file="assets\TMD_Logo.png"))
        self.window.wm_state('zoomed')
        self.dark_title_bar()

        self.lexeme = []
        self.token = []
        self.opened_files = {}  
        self.create_ui()
        self.keyboard_shortcut()

    def dark_title_bar(self):
        self.window.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ct.windll.user32.GetParent
        hwnd = get_parent(self.window.winfo_id())
        value = ct.c_int(2)
        set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ct.byref(value), ct.sizeof(value))

    def create_ui(self):
        style = ttk.Style()
        style.theme_use("alt")
        
        self.create_left_panel()
        self.create_notebook()
        self.create_console()
        self.create_code_editor()
        self.create_right_panel()

    def create_left_panel(self):
        self.environFrame = tk.Frame(self.window, bg="#202020")
        self.environFrame.pack(side="left", fill="both", expand=True)

        navFrame = tk.Frame(self.environFrame, bg="#a6b3f1", height=35)
        navFrame.pack(side="top", fill="x")

        # Load base icons and resize them to a smaller size
        self.new_icon = tk.PhotoImage(file="assets\_new_icon.png").subsample(28, 28)  # Adjust the subsample factor as needed
        self.new_hover_icon = tk.PhotoImage(file="assets\_new_icon_hover.png").subsample(28, 28)
        self.open_icon = tk.PhotoImage(file="assets\open_icon.png").subsample(30, 30)
        self.open_hover_icon = tk.PhotoImage(file="assets\open_icon_hover.png").subsample(30, 30)
        self.save_icon = tk.PhotoImage(file="assets\save_icon.png").subsample(33, 33)
        self.save_hover_icon = tk.PhotoImage(file="assets\save_icon_hover.png").subsample(33, 33)

        # Define hover and leave behavior as methods of the class
        def on_hover_button(self, button, hover_icon):
            button.config(image=hover_icon)

        def on_leave_button(self, button, original_icon):
            button.config(image=original_icon)

        # New button
        self.new_button = tk.Label(
            navFrame, image=self.new_icon, text=" New", font=("Helvetica", 10, "bold"),
            compound="left", bg="#a6b3f1", borderwidth=0, padx=4, pady=8
        )
        self.new_button.pack(side="left", padx=5)
        self.new_button.bind("<Button-1>", lambda e: self.new_file())
        self.new_button.bind("<Enter>", lambda e: self.new_button.config(image=self.new_hover_icon, fg="white"))
        self.new_button.bind("<Leave>", lambda e: self.new_button.config(image=self.new_icon, fg="black"))
        
        # Separator
        separator = tk.Canvas(navFrame, width=1, height=30, bg="black", highlightthickness=0)
        separator.pack(side="left", pady=6, padx=5)


        # Open button
        self.open_button = tk.Label(
            navFrame, image=self.open_icon, text=" Open", font=("Helvetica", 10, "bold"),
            compound="left", bg="#a6b3f1", borderwidth=0, padx=4, pady=5
        )
        self.open_button.pack(side="left", padx=5)
        self.open_button.bind("<Button-1>", lambda e: self.open_file())
        self.open_button.bind("<Enter>", lambda e: self.open_button.config(image=self.open_hover_icon, fg="white"))
        self.open_button.bind("<Leave>", lambda e: self.open_button.config(image=self.open_icon, fg="black"))

        # Separator
        separator = tk.Canvas(navFrame, width=1, height=30, bg="black", highlightthickness=0)
        separator.pack(side="left", pady=6, padx=5)

        
        # Save button
        self.save_button = tk.Label(
            navFrame, image=self.save_icon, text=" Save", font=("Helvetica", 10, "bold"),
            compound="left", bg="#a6b3f1", borderwidth=0, padx=4, pady=5
        )
        self.save_button.pack(side="left", padx=5)
        self.save_button.bind("<Button-1>", lambda e: self.save_as_file())
        self.save_button.bind("<Enter>", lambda e: self.save_button.config(image=self.save_hover_icon, fg="white"))
        self.save_button.bind("<Leave>", lambda e: self.save_button.config(image=self.save_icon, fg="black"))

        # Semantic button
        self.semanticBtn = tk.Label(
            navFrame, text="Semantic", font=("Helvetica", 11, "bold"),
            bg="#a6b3f1", borderwidth=1, relief="solid", width=8
        )
        self.semanticBtn.pack(side="right", pady=5, padx=(0, 20))
        self.semanticBtn.bind("<Enter>", lambda e: self.semanticBtn.config(fg="white"))
        self.semanticBtn.bind("<Leave>", lambda e: self.semanticBtn.config(fg="black"))
        self.semanticBtn.bind("<Button-1>", self.semantic_click)

        # Syntax button
        self.syntaxBtn = tk.Label(
            navFrame, text="Syntax", font=("Helvetica", 11, "bold"),
            bg="#a6b3f1", borderwidth=1, relief="solid", width=8
        )
        self.syntaxBtn.pack(side="right", pady=5, padx=(0, 15))
        self.syntaxBtn.bind("<Enter>", lambda e: self.syntaxBtn.config(fg="white"))
        self.syntaxBtn.bind("<Leave>", lambda e: self.syntaxBtn.config(fg="black"))
        self.syntaxBtn.bind("<Button-1>", self.syntax_click)

        # Lexical button
        self.lexicalBtn = tk.Label(
            navFrame, text="Lexical", font=("Helvetica", 11, "bold"),
            bg="#a6b3f1", borderwidth=1, relief="solid", width=8
        )
        self.lexicalBtn.pack(side="right", pady=5, padx=(0, 15))
        self.lexicalBtn.bind("<Button-1>", self.lexical_click)
        self.lexicalBtn.bind("<Enter>", lambda e: self.lexicalBtn.config(fg="white"))
        self.lexicalBtn.bind("<Leave>", lambda e: self.lexicalBtn.config(fg="black"))

    
    def create_notebook(self):
        # Initialize the CustomNotebook
        self.notebook = CustomNotebook(self.environFrame)
        self.notebook.pack(fill="both")

        new_tab_frame = tk.Frame(self.notebook, bg="#272727")
        
        new_tab_frame.pack(fill="x",padx=(0, 0), pady=0)

        # Check if the notebook has any existing tabs
        if len(self.notebook.tabs()) > 0:
            # Insert at index 0 if there are already tabs
            self.notebook.insert(0, new_tab_frame, text="Untitled")
        else:
            # Add as the first tab if there are no existing tabs
            self.notebook.add(new_tab_frame, text="Untitled")
        
        # Select the new tab
        self.notebook.select(new_tab_frame)

    def create_code_editor(self):
        
        self.codeFrame = tk.Frame(self.environFrame, bg="#272727")
        self.codeFrame.pack(side="top", fill="both", expand=True)
        code_scroll = ttk.Scrollbar(self.codeFrame, style="Black.Vertical.TScrollbar")

        self.lineTextBox = tk.Text(self.codeFrame, width=4, bg="#272727", fg="white",
                                   font=("Courier New", 13), insertbackground="black", padx=5, wrap="none", yscrollcommand=code_scroll.set)
        self.lineTextBox.pack(side="left", fill="y", padx=(0, 0), pady=0)
        self.lineTextBox.tag_configure("right", justify="right", relief="flat")

        self.textFrame = tk.Text(self.codeFrame, height=25, bg="#272727", fg="white",
                                 font=("Courier New", 13), insertbackground="white", padx=5, wrap="none", yscrollcommand=code_scroll.set, undo=True)
        self.textFrame.pack(side="left", fill="both", expand=True, padx=(0, 1), pady=0)
        self.textFrame.bind("<Tab>", self.insert_tab)


        #style scrollbar
        scrollStyle = ttk.Style()
        scrollStyle.configure("Black.Vertical.TScrollbar", background="#393939", troughcolor="#202020", arrowcolor="#A3A3A3", bordercolor="#393939")
        scrollStyle.map("Black.Vertical.TScrollbar",background=[("active", "#393939"), ("disabled", "#393939")],)
        
        code_scroll.pack(side="right", fill="y")

        self.textFrame.config(yscrollcommand=code_scroll.set)
        self.lineTextBox.config(yscrollcommand=code_scroll.set)

        self.textFrame.bind("<KeyRelease>", self.on_text_change)
        self.textFrame.bind("<Configure>", self.on_text_change)
        self.notebook.bind("<<NotebookTabChanged>>", self.get_current_tab)
        
        self.textFrame.bind("<MouseWheel>", lambda event: self.synchronize_scroll())  
        self.lineTextBox.bind("<MouseWheel>", lambda event: self.synchronize_scroll1()) 
        keys_to_bind = ['"', "'", '{', '[', '(', '<', '*', '/']
        for key in keys_to_bind:
            self.textFrame.bind(f"<Key-{key}>", lambda event, widget=self.textFrame: self.auto_close(event, widget))
            
    def create_console(self):
        # Create the console frame with an initial fixed height
        self.consoleFrame = tk.Frame(self.environFrame, bg="#202020", height=200)
        self.consoleFrame.pack(side="bottom", fill="x")
        self.consoleFrame.pack_propagate(False)  # Prevent auto-resizing

        # Add a panel for the draggable area
        consolePanel = tk.Frame(self.consoleFrame, bg="#1A1A1A", height=10, cursor="sb_v_double_arrow")
        consolePanel.pack(side="top", fill="x")

        self.consoleClose = tk.Label(consolePanel, text="˅", font=("Consolas", 13),
                                    fg="#ffffff", bg="#1A1A1A")
        self.consoleClose.pack(side="right", pady=(7, 0), padx=(0, 15))
        self.consoleClose.bind("<Button-1>", self.consoleClose_click)

        # Create the text widget for the console
        self.console = tk.Text(
            self.consoleFrame, bg="#202020", fg="white",
            font=("Consolas", 12), padx=10, pady=10, borderwidth=1, relief="solid"
        )
        self.console.pack(side="bottom", fill="both", expand=True)
        self.console.tag_configure("error", foreground="#b23232", font=("Consolas", 12, "bold"))
        self.console.tag_configure("ln_col", foreground="#a8a8a8", font=("Consolas", 12))
        self.consoleFlag = False
        # Bind mouse events for resizing
        consolePanel.bind("<ButtonPress-1>", self.start_drag)
        consolePanel.bind("<B1-Motion>", self.perform_drag)

    def start_drag(self, event):
        # Record the initial mouse position and console height
        self.start_y = event.y_root
        self.start_height = self.consoleFrame.winfo_height()
        # Store the total height of the environment frame for boundaries
        self.environ_height = self.environFrame.winfo_height()

    def perform_drag(self, event):
        # Calculate the vertical change in mouse position
        delta_y = self.start_y - event.y_root
        new_console_height = self.start_height + delta_y
        """
        self.console.insert(1.0,f"height:   {new_console_height}   delta_y: {delta_y}   start: {self.start_y}   y_root: {event.y_root}\n")
        """
        
        if new_console_height > 200:
            self.consoleClose.config(text="˅")
            self.consoleFlag = True
        else:
            self.consoleClose.config(text="˄")
            
        # Define minimum and maximum heights for the console
        min_console_height = 50  # Minimum height for the console
        max_console_height = self.environ_height - 50  # Leave at least 50px for the code editor

        # Constrain the new console height within the allowed range
        new_console_height = max(min_console_height, min(new_console_height, max_console_height))

        # Update the console frame's height
        self.consoleFrame.config(height=new_console_height)

        # Update the code editor frame's height
        code_editor_height = self.environ_height - new_console_height
        self.codeFrame.pack_configure(height=code_editor_height)

        # Force the code editor to update its layout
        self.codeFrame.update_idletasks()
        
    def consoleClose_click(self, event):
        if self.consoleClose.cget("text") == "˅":
            self.console.pack_forget()  # Hide the console
            self.consoleClose.config(text="˄")
            self.consoleFrame.config(height=30)  # Minimized height for the header only
        else:
            self.console.pack(side="bottom", fill="both", expand=True)  # Show the console
            self.consoleClose.config(text="˅")
            self.consoleFrame.config(height=200)  # Restore to default height

    def create_right_panel(self):
        tableFrame = tk.Frame(self.window, width=500, bg="#e5e2ed")
        tableFrame.pack(side="right", fill="both")

        headingStyle = ttk.Style()
        headingStyle.configure("Custom.Treeview.Heading", font=("Helvetica", 10), background="#dee4ff", relief="flat")
        headingStyle.map("Custom.Treeview.Heading", background=[("active", "#dee4ff")])

        self.table = ttk.Treeview(tableFrame, columns=("Lexeme", "Token"), show="headings", style="Custom.Treeview")
        self.table.heading("#1", text="Lexeme")
        self.table.heading("#2", text="Token")
        self.table.pack(fill="both", expand=True)

    def multiple_yview(self, *args):
        self.lineTextBox.yview(*args)
        self.textFrame.yview(*args)
    
    def clear_text(self):
        current_tab = self.notebook.select()  
        for item in self.table.get_children():
            self.table.delete(item)
        self.textFrame.delete("1.0", tk.END)
        self.console.delete("1.0", tk.END)
        self.lexeme.clear()
        self.token.clear()
        current_tab = self.notebook.select()
        self.notebook.tab(current_tab, text="Untitled")  
        
        self.update_line_numbers()
        
    def has_text(self):
        if len(self.textFrame.get("1.0", "end-1c").strip()) > 0:
            return True
        else:
            return False
    
    def new_file(self, event=None):
        current_tab = self.notebook.select()  
        self.current_tab_name = self.notebook.tab(current_tab, "text") 
        
        if self.has_text() and self.current_tab_name == "Untitled":
            resp = messagebox.askyesno("Save as file",f"{self.current_tab_name} is unsaved! Do you want to save?")
            if resp:
                self.save_as_file()
            else:
                self.clear_text()
        elif self.current_tab_name != "Untitled":
            resp = messagebox.askyesno("Save as file",f"{self.current_tab_name} is unsaved! Do you want to save?")
            if resp:
                self.save_as_file()
                self.notebook.tab(current_tab, text="Untitled")
                self.clear_text()

            else:
                self.notebook.tab(current_tab, text="Untitled")
                self.clear_text()
        else: 
            
            self.notebook.tab(current_tab, text="Untitled")
            self.clear_text()
            
    def open_file(self):
        current_tab = self.notebook.select()  
        self.current_tab_name = self.notebook.tab(current_tab, "text") 
        resp = False
        flag = True
        total_tabs = len(self.notebook.tabs())
        if total_tabs > 11:
            return
        if self.current_tab_name == "Untitled":
            if self.has_text() and self.current_tab_name == "Untitled":
                resp = messagebox.askyesno("Open file",f"{self.current_tab_name} is unsaved! Do you want to save?")
                if resp:
                    self.save_as_file() 
                    current_tab = self.notebook.select()
                    flag = False
                    self.current_tab_name = self.notebook.tab(current_tab, "text") 
        file_path = filedialog.askopenfilename(filetypes=[("TMD Files", "*.tmd")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    if flag:
                        resp = messagebox.askyesno("Open file",f"Do you want to save first?")
                        if resp:
                            self.save_as_file()
                    fileName = file_path.split("/")[-1]
                    if len(fileName) > 11:
                        fileName = fileName[:11]
                    file_info = {"name": fileName, "path": file_path}
                    
                    index = self.find_tab_index(fileName)
                    if index is not None:
                        self.notebook.forget(index)
                        
                    self.opened_files[file_info["name"]] = file_info

                    new_frame = tk.Frame(self.notebook, bg="#272727")
                    self.notebook.add(new_frame, text=fileName)  #
                    self.notebook.select(new_frame)
                    
                    content = file.read()
                    self.textFrame.delete("1.0", tk.END)
                    self.textFrame.insert("1.0", content)
                    
                    if not resp or not self.has_text:
                        self.forget_tab_by_name("Untitled")
                    
                    self.update_line_numbers()

            except Exception as e:
                self.console.insert(tk.END, f"Error opening file: {str(e)}\n", "error")
            
    
    def save_as_file(self):
        current_tab = self.notebook.select()  
        self.current_tab_name = self.notebook.tab(current_tab, "text")
        if self.current_tab_name == "Untitled":
            file_path = filedialog.asksaveasfilename(defaultextension=".tmd",
                                                    filetypes=[("TMD Files", "*.tmd")])
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        content = self.textFrame.get("1.0", "end-1c")
                        file.write(content)
                    
                    current_tab = self.notebook.select()
                    if len(self.current_tab_name) < 11:
                        fileName = file_path.split("/")[-1]
                        fileName = fileName[:11]
                        
                    else:
                        fileName = file_path.split("/")[-1]
                        
                    self.notebook.tab(current_tab, text=fileName)  

                    self.opened_files[self.notebook.tab(current_tab, "text")] = {"path": file_path}
                    
                    self.window.title(f"TMD Compiler - {file_path}")
                except Exception as e:
                    self.console.insert(tk.END, f"Error saving file: {str(e)}\n", "error")
        else:
            current_tab = self.notebook.select()  
            self.current_tab_name = self.notebook.tab(current_tab, "text") 
            file_info = self.opened_files.get(self.current_tab_name)
            
            if self.current_tab_name == "Untitled":
                self.save_as_file()
            try:
                file_path = file_info["path"] 
                with open(file_path, "w", encoding="utf-8") as file:
                    content = self.textFrame.get("1.0", "end-1c")
                    file.write(content)
            except Exception as e:
                self.console.insert(tk.END, f"Error saving file: {str(e)}\n", "error")
                
    def get_current_tab(self, event):
        current_tab = self.notebook.select()  
        self.current_tab_name = self.notebook.tab(current_tab, "text") 
        
        if self.current_tab_name == "Untitled":
            return
        
        file_info = self.opened_files.get(self.current_tab_name)
        if file_info:  
            file_path = file_info["path"]  
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.textFrame.delete("1.0", tk.END)
                    self.textFrame.insert("1.0", content)
                self.window.title(f"TMD Compiler - {file_path}")
                self.update_line_numbers()
            except Exception as e:
                self.console.insert(tk.END, f"Error opening file: {str(e)}\n", "error")
        else:
            self.console.insert(tk.END, "Error: No file info found for the current tab.\n", "error")
    def find_tab_index(self, name):
        for index in range(self.notebook.index("end")):
            if self.notebook.tab(index, "text") == name:
                return index
        return
    def forget_tab_by_name(self, name):
        index = self.find_tab_index(name)
        if index is not None:
            self.notebook.forget(index)

    def insert_tab(self, event):
        self.textFrame.insert(tk.INSERT, ' ' * 3)
        return "break"

    # Auto-close marker function
    def auto_close(self, event, text_widget):
        closing_markers = {
            '"': '"',
            "'": "'",
            '{': '}',
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

    def on_enter_semantic(self, event):
        self.semanticBtn.config(fg="white")
    def on_leave_semantic(self,event):
        self.semanticBtn.config(fg="black")

    def on_enter_lexical(self, event):
        self.lexicalBtn.config(fg="white")
    def on_leave_lexical(self,event):
        self.lexicalBtn.config(fg="black")
    def lexical_click(self, event):
        errorflag[0] = False
        lexeme.clear()
        token.clear()
        state.clear()
        idens.clear()
        for item in self.table.get_children():
            self.table.delete(item)
        self.console.delete("1.0", tk.END)
        code = self.textFrame.get("1.0", "end")
        lexer(code, self.console, self.table)

    def on_enter_syntax(self, event):
        self.syntaxBtn.config(fg="white")
    def on_leave_syntax(self,event):
        self.syntaxBtn.config(fg="black")
    def syntax_click(self, event):
        errorflag[0] = False
        #self.lexical_click
        lexeme.clear()
        token.clear()
        state.clear()
        idens.clear()
        rows.clear() # NEW!
        col.clear() # NEW!
        for item in self.table.get_children():
            self.table.delete(item)
        self.console.delete("1.0", tk.END)
        code = self.textFrame.get("1.0", "end")
        lexer(code, self.console, self.table)
        parse(self.console)
    def semantic_click(self, event):
        errorflag[0] = False
        #self.lexical_click
        lexeme.clear()
        token.clear()
        state.clear()
        idens.clear()
        rows.clear() # NEW!
        col.clear() # NEW!
        for item in self.table.get_children():
            self.table.delete(item)
        self.console.delete("1.0", tk.END)
        code = self.textFrame.get("1.0", "end")
        lexer(code, self.console, self.table)
        semantic(self.console)


    def update_line_numbers(self, event=None):
        line_numbers = ""
        line_count = int(self.textFrame.index('end-1c').split('.')[0])
        line_numbers = "\n".join(str(i) for i in range(1, line_count + 1))

        self.lineTextBox.config(state="normal")
        self.lineTextBox.delete("1.0", "end")
        self.lineTextBox.insert("1.0", line_numbers, "right")
        self.lineTextBox.config(state="disabled")

    def on_text_change(self, event=None):
        self.update_line_numbers()
        self.synchronize_scroll()

    def synchronize_scroll(self):
        self.text_frame_scroll_position = self.textFrame.yview()
        self.lineTextBox.yview_moveto(self.text_frame_scroll_position[0])
    
    def synchronize_scroll1(self):
        self.line_frame_scroll_position = self.lineTextBox.yview()
        self.textFrame.yview_moveto(self.line_frame_scroll_position[0])

    def _show_file_menu(self, event):
        x = self.file_menu_button.winfo_rootx()
        y = self.file_menu_button.winfo_rooty() + self.file_menu_button.winfo_height()
        self.file_menu.post(x, y)
    
    def keyboard_shortcut(self, event=None):
        self.window.bind("<Control-s>", lambda event: self.save_as_file())
        self.window.bind("<Control-S>", lambda event: self.save_as_file())
        self.window.bind("<Control-o>", lambda event: self.open_file())
        self.window.bind("<Control-O>", lambda event: self.open_file())
        self.window.bind("<Control-n>", lambda event: self.new_file())
        self.window.bind("<Control-N>", lambda event: self.new_file())
        self.window.bind("<Tab>", lambda event: self.insertTab())
        
    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = TMDCompiler()
    app.run()
