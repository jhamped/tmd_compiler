from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def parse(console):    
    current_token_index = 0
    
    def error_message(error):
        line = rows[current_token_index]
        column = col[current_token_index]
        console.insert(tk.END, "Syntax Error: ", "error")
        console.insert(tk.END, f"{error}")
        console.insert(tk.END, f"\n           line {line}, col {column}\n", "ln_col")


    add_all_set()
    if not token:  # If token list is empty
        error_message("No tokens to parse")
        return
    stack = ["<program>"]  # Initialize stack with start symbol and end marker

    def get_lookahead():
        if current_token_index >= len(token):  # Prevent index out of range
            return None
        curr_token = token[current_token_index]
        
        if current_token_index < len(token):
            if curr_token.startswith("id"):
                curr_token = "id"
            return curr_token
        else:
            None

    while stack:
        if len(token) > current_token_index:
            lookahead = get_lookahead()
        else:
            error_message("End of file")
        top = stack.pop()
        lookahead = get_lookahead()
        if lookahead is None:
            error_message("Unexpected end of input. No main function found")
            return
        if top == lookahead:
            # Terminal matches lookahead, consume the token
            print(f"Match: {lookahead}")
            current_token_index += 1
        elif top in parsing_table:
            # Non-terminal: use the parsing table
            rule = parsing_table[top].get(lookahead)
            if rule:
                print(f"Apply rule: {top} -> {' '.join(rule)}")
                if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                    stack.extend(reversed(rule))
            else:
                error_message(f"No rule for {token} with lookahead {lookahead}")
                break
        else:
            error_message(f"Unexpected symbol {lookahead}")
            break

    #if stack or current_token_index < len(token):
        #error_message("Input rejected")
    #else:
     #   console.insert(tk.END, "Input accepted: Syntactically correct.")
