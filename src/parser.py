from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def parse(console):  
    if errorflag[0] == True:  
        return
    print(f"token: {token}")
    print(f"lexeme: {lexeme}")
    current_token_index = 0
    prevlookahead = ""
    
    def error_message(error):
        line = rows[current_token_index] if current_token_index < len(rows) else "0"
        column = col[current_token_index] if current_token_index < len(col) else "0"
        console.insert(tk.END, "Syntax Error: ", "error")
        console.insert(tk.END, f"{error}")
        console.insert(tk.END, f"\n           line {line}, col {column}\n", "ln_col")
        errorflag[0] = True
        return
    add_all_set()
    if not token:  # If token list is empty
        error_message("No tokens to parse")
        return
    stack = ["<program>"]  # Initialize stack with start symbol and end marker
    def get_lookahead():
        #0 > 8 FALSE
        if current_token_index >= len(token):  # Prevent index out of range
            return None
        curr_token = token[current_token_index]
        #curr_token = main
        # 0 < 8 TRUE
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
        #8 > 0
        if len(token) > current_token_index:
            lookahead = get_lookahead()
            
        #else:
            #error_message("End of file")
        #stack []
        #top = <program>
        ##stack ["}", "<statements>", "{"]
        #top = "main"
        print(f"stack: {stack}")
        top = stack.pop()
        print(f"after stack: {stack}")
        print(f"top {top}")
        lookahead = get_lookahead()
        if lookahead is None:
            error_message("Unexpected End-of-File. ")
            return
        
        #main == main
        if top == lookahead:
            # Terminal matches lookahead, consume the token
            print(f"Match: {lookahead}")
            prevlookahead = lookahead
            current_token_index += 1
        #TRUE
        elif top in parsing_table:
            # Non-terminal: use the parsing table
            rule = parsing_table[top].get(lookahead)
            #rule = ["null"]
            print(f"rule: {rule}/{lookahead}/{top}")
            if rule:
                print(f"Apply rule: {top} -> {' '.join(rule)}")
                if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                    #stack [<program>]
                    #<global_dec>", "<segm>", "main", "{", "<statements>", "}"
                    #stack ["<global_dec>", "<segm>", "main", "{", "<statements>", "}"]
                    #stack ["}", "<statements>", "{", "main", "<segm>", "<global_dec>"]
                    stack.extend(reversed(rule))
                    #stack ["}", "<statements>", "{", "main", "<segm>", "<global_dec>"]
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
