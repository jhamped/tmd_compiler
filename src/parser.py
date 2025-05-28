from definitions import *
import tkinter as tk

def parse(console):  
    if errorflag[0] == True:  
        return
    current_token_index = 0
    prevlookahead = "Start"
    
    def error_message(error):
        line = rows[current_token_index] if current_token_index < len(rows) else "0"
        column = col[current_token_index] if current_token_index < len(col) else "0"
        console.insert(tk.END, "Syntax Error: ", "error")
        console.insert(tk.END, f"{error}")
        console.insert(tk.END, f"\n           line {line}, col {column}\n", "ln_col")
        errorflag[0] = True
        return
    add_all_set()
    if not token:
        error_message("No tokens to parse")
        return
    stack = ["<program>"] 
    def get_lookahead():
        if current_token_index >= len(token):
            return None
        curr_token = token[current_token_index]

        if current_token_index < len(token):
            if curr_token.startswith("id"):
                curr_token = "id"
            return curr_token
        else:
            None
            
    
    while stack:
        
        if errorflag[0] == True:
            console.insert(tk.END, "Parsing interrupted...", "error")
            return
        if len(token) > current_token_index:
            lookahead = get_lookahead()
        top = stack.pop()
        lookahead = get_lookahead()
        if lookahead is None:
            error_message("Unexpected End-of-File. ")
            return
        
        if top == lookahead:
            prevlookahead = lookahead
            current_token_index += 1
        elif top in parsing_table:
            rule = parsing_table[top].get(lookahead)
            if rule:
                if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                    stack.extend(reversed(rule))
            else:
                if prevlookahead == "Start":
                    error_message(f"Unexpected {lookahead}. Program must start with a function 'segm', declaration, or 'main' block. ")
                else:
                    error_message(f"Unexpected {lookahead} after {prevlookahead} Expected: {list(parsing_table.get(top, {}).keys())} ")
                return
        else:
            error_message(f"Unexpected symbol {lookahead} after {prevlookahead} Expected: {top}")
            return
    
    if stack or current_token_index < len(token):
        error_message(f"Unexpected {get_lookahead()} after main function")
    else:
        console.tag_config("accepted", foreground="#00FFFF", font=("Arial", 12, "bold"))
        console.insert(tk.END,"Input accepted: ", "accepted")
        console.insert(tk.END,"Syntactically correct.\n")
