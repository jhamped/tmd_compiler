import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
import ctypes as ct
import re
import string

# Lexemes and tokens
lexeme = []
token = []

#------------------------Definitions-------------------------
arithmetic_operator = ['+', '-', '*', '/', '%']
relational_operator = ['==', '!=', '<', '<=', '>', '>=']
logical_operator = ['&&', '||', '!']
unary_operator = ['++', '--']
assignment_operator = ['=', '+=', '-=', '*=', '/=', '%=']
number_operator = arithmetic_operator + relational_operator + logical_operator + unary_operator
all_operators = number_operator + assignment_operator

symbols = ['!', '#', '%', '&', '*', '(', ')', '-', '=', '+', '[', ']', '{', '}', ':', ';', ',', '<', '>', '.', '/', '~', '|']
more_symbols = ['@', '$', '^', '_', '?']
punc_symbols = more_symbols + symbols
quote_symbols = ['\'', '"']

alpha = list(string.ascii_letters)
alphanumeric = list(string.ascii_letters + string.digits)
ascii_def = alphanumeric + punc_symbols + quote_symbols

# Regular expression
keywords = ['strc', 'segm', 'main', 'bln', 'chr', 'int', 'dec', 'str', 'var', 'const', 'true', 'false', 'disp', 'insp', 'if', 
            'elif', 'else', 'switch', 'key', 'def', 'for', 'foreach', 'in', 'do', 'while', 'brk', 'rsm', 'exit', 'ret', 'none']
reg_symbols =  number_operator + assignment_operator + symbols

whitespace = {' ', '\t', '\n'}

# Delimiters
keyword1_delims = {
    'state_delim' : ['('], 
    'block_delim' : ['{'],
    'def_delim' : [':'],
    'comma_delim' : [']', '(', '{', '"', '\''] + alphanumeric + unary_operator,
    'iden_delim' : all_operators + [';', '&', '>', '(', ')', '[', ']', '{', '.', ','],
    'lit_delim' : [';', ',', '&'],
    'op_delim' : alphanumeric + ['(', '~'],
    'unary_delim' : alphanumeric + ['(', ')', ';', ',', '~'],
    'relate2_delim' : alphanumeric + ['(', '~'],
    'paren_delim' : alphanumeric + unary_operator + [';', '!', '#', '\'', '"', '(', ')'],
    'paren1_delim' : arithmetic_operator + relational_operator + ['&', '|', '{', ')', ';'],
    'brace_delim' : alphanumeric + unary_operator + [';', '(', '\'', '"', '{', '}'],
    'semicolon_delim' : alphanumeric + unary_operator + ['(', '}'],
    'bracket_delim' : alphanumeric + unary_operator + [']', ','],
    'bracket1_delim' : number_operator + [')', '=', ';', '&', '>'],
    'var_delim' : alpha + unary_operator + ['('],
    'var1_delim' : ascii_def,
    'concat_delim' : alpha + ['(', '"', '\'', '#'],
    'interpol_delim' : ['"'],
    'data_delim' : alpha + ['[', '('],
    'val_delim' : [';', ',', ')', '}'],
    'colon_delim' : alphanumeric + unary_operator + ['('],
    'jmp_delim' : [';'],
    'key_delim' : alphanumeric + ['\'', '"']
}

keyword2_delims = {
    'num_delim' : number_operator + keyword1_delims['comma_delim'],
    'relate_delim' : keyword1_delims['op_delim'] + ['!', '\'', '"', '~'],
    'relate1_delim' : keyword1_delims['relate2_delim'] + ['!'],
    'brace1_delim' : keyword1_delims['semicolon_delim'] + unary_operator + ['(', '}', ';', ','],
}

keyword3_delims = {
    'asn_delim' : keyword2_delims['relate_delim'] + ['(', '{']
}

keyword_delims = keyword1_delims | keyword2_delims | keyword3_delims

#--------------------Analyzers-------------------------

#-----------------lexical analyzer---------------------
def lexical_click(event):
    event.pos = 0
    code = textFrame.get("1.0", "end")

    def get_char():  
        if event.pos < len(code):
            curr = code[event.pos]
            event.pos += 1
            return curr
        return None 
    
    def next_char():
        if event.pos < len(code):
            return code[event.pos]
        return None
    
    def skip_whitespace():  
        while(char := next_char()) in whitespace:
            get_char()

    def skip_single_comment():  
        while(char := get_char()) not in ['\n', None]:
            pass

    def skip_multi_comment():
        while True:
            char = get_char()
            if char == '*' and next_char() == '/':
                get_char() 
                break

    def get_string():
        string = "\""
        while True:
            char = get_char()
            if char == '"':
                string += char
                lexeme.append(string)
                token.append('str_lit')
                break
            else:
                string += char
                continue

    def get_character():
        character = "'"
        while True:
            char = get_char()
            if char == '\'':
                character += char
                if (len(character) == 3):
                    lexeme.append(character)
                    token.append('chr_lit')
                else:
                    console.insert(tk.END, "Error: ", "error")
                    console.insert(tk.END, "Character literals must only contain one character\n")
                break
            else:
                character += char
                continue
                
    def get_num():
        if re.match(r'^\d{1,10}$', num):
            lexeme.append(num)
            token.append('int_lit')
        elif re.match(r'^\d{1,10}+\.\d{1,7}+$', num):
            lexeme.append(num)
            token.append('dec_lit')
        elif re.match(r'^\d{11,}$', num):
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"{num} exceeds maximum length of 10 digits\n")
        elif re.match(r'^\d+\.\d{8,}+$', num):
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"{num} exceeds maximum length of 7 decimal places\n")
        elif num.isalnum():
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"Invalid identifier: {num}\n")
        else:
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"Invalid: {num}\n")

    def get_id():
        if re.match(r'[a-zA-Z0-9_]{1,30}$', key):
            lexeme.append(key)
            token.append('id')
        elif len(key) > 30:
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"Identifier {key} exceeds maximum length of 30 characters\n")
        else:
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"Invalid identifier: {key}\n")
    
    def check_keyword_delim():
        check = {
            True: lambda: (lexeme.append(key), token.append(key)),
            False: lambda: (console.insert(tk.END, "Error: ", "error"), console.insert(tk.END, f"{key} => wrong delimiter\n"))
        }
        
        skip_whitespace()
        nextchr = next_char()
        match key:
            case 'bln': check[nextchr in keyword_delims['data_delim']]()
            case 'brk': check[nextchr in keyword_delims['jmp_delim']]()
            case 'chr': check[nextchr in keyword_delims['data_delim']]()
            case 'const': check[nextchr in alpha]()
            case 'dec': check[nextchr in keyword_delims['data_delim']]()
            case 'def': check[nextchr in keyword_delims['def_delim']]()
            case 'disp': check[nextchr in keyword_delims['state_delim']]()
            case 'do': check[nextchr in keyword_delims['block_delim']]()
            case 'elif': check[nextchr in keyword_delims['state_delim']]()
            case 'else': check[nextchr in keyword_delims['block_delim']]()
            case 'exit': check[nextchr in keyword_delims['jmp_delim']]()
            case 'false': check[nextchr in keyword_delims['val_delim']]()
            case 'for': check[nextchr in keyword_delims['state_delim']]()
            case 'foreach': check[nextchr in keyword_delims['state_delim']]()
            case 'if': check[nextchr in keyword_delims['state_delim']]()
            case 'in': check[nextchr in alpha]()
            case 'insp': check[nextchr in keyword_delims['state_delim']]()
            case 'int': check[nextchr in keyword_delims['data_delim']]()
            case 'bln': check[nextchr in keyword_delims['key_delim']]()
            case 'main': check[nextchr in keyword_delims['state_delim']]()
            case 'none': check[nextchr in keyword_delims['val_delim']]()
            case 'ret': check[nextchr in keyword_delims['key_delim']]()
            case 'rsm': check[nextchr in keyword_delims['jmp_delim']]()
            case 'segm': check[nextchr in alpha]()
            case 'str': check[nextchr in keyword_delims['data_delim']]()
            case 'strc': check[nextchr in alpha]()
            case 'switch': check[nextchr in keyword_delims['state_delim']]()
            case 'true': check[nextchr in keyword_delims['val_delim']]()
            case 'var': check[nextchr in alpha]()
            case 'while': check[nextchr in keyword_delims['state_delim']]()

    def check_symbol_delim():
        check = {
            True: lambda: (lexeme.append(symbol), token.append(symbol)),
            False: lambda: (console.insert(tk.END, "Error: ", "error"), console.insert(tk.END, f"{symbol} => wrong delimiter\n"))
        }

        symbol = char 
        nextchr = next_char()
        match char:
            case '=':
                if nextchr == '=':
                    symbol += nextchr
                    get_char()
                    skip_whitespace()
                    nextchr = next_char()
                    #print(nextchr)
                    check[nextchr in keyword_delims['relate_delim']]()
                else:
                    check[nextchr in keyword_delims['asn_delim']]() 


    while (char := get_char()) is not None:
        skip_whitespace()  

        if char == '/' and next_char() == '/':
            get_char() 
            skip_single_comment()

        elif char == '/' and next_char() == '*':
            get_char() 
            skip_multi_comment()
        
        elif char == '"':
            get_string()

        elif char == '\'':
            get_character()

        elif char.isdigit():
            num = char
            while not next_char().isdigit:
                num += get_char()
            get_num()

        elif char.isalpha():
            key = char
            while (next := next_char()) and (next.isalnum() or next == '_'):
                key += get_char()
            if key in keywords:
                check_keyword_delim()
            else:
                get_id()

        elif char in reg_symbols:
            check_symbol_delim()
            #lexeme.append(char)
            #token.append(char)

        elif char == '_':
            invalid = "_"
            while next_char() not in whitespace:
                invalid += get_char()
            console.insert(tk.END, "Error: ", "error")
            console.insert(tk.END, f"Invalid identifier: {invalid}\n")

    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i]))   


#----------------------Other Functions------------------------

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

#syntax button
def on_enter_syntax(event):
    syntaxBtn.config(fg="white")
def on_leave_syntax(event):
    syntaxBtn.config(fg="black")


#----------------------------GUI-----------------------------

#title bar 
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

# Create the main window
window = tk.Tk()
window.title("TMD Compiler")
icon = PhotoImage(file="LexicalAnalyzer\TMD_logo.png")
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

#syntax button
syntaxBtn = tk.Label(navFrame, text="Syntax", font=("Helvetica", 11, "bold"), bg="#a6b3f1", borderwidth=1, relief="solid", width=10)
syntaxBtn.pack(side="right", pady=5, padx=(0, 10))
syntaxBtn.bind("<Button-1>", lexical_click)
syntaxBtn.bind("<Enter>", on_enter_syntax)
syntaxBtn.bind("<Leave>", on_leave_syntax)

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

# Create a frame for the Treeview on the right
tableFrame = tk.Frame(window, width=500, bg="#e5e2ed")
tableFrame.pack(side="right", fill="both")

# Create a Treeview for the table
table = ttk.Treeview(tableFrame, columns=("Lexeme", "Token"))
table["show"] = "headings"

# Define column headings
table.heading("#1", text="Lexeme")
table.heading("#2", text="Token")
table.pack(fill="both", expand=True)

window.mainloop()





