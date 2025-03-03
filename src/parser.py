from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def parse(console):
    add_all_set()
    if not token:  # If token list is empty
        console.insert(tk.END, "Syntax Error: No tokens to parse")
        return
    stack = ["<program>"]  # Initialize stack with start symbol and end marker
    current_token_index = 0

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
            console.insert(tk.END, "Syntax Error")
        top = stack.pop()
        lookahead = get_lookahead()
        if lookahead is None:
            console.insert(tk.END, f"Syntax Error: Unexpected end of input. No main function found")
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
                console.insert(tk.END, f"Syntax error: No rule for {top} with lookahead {lookahead}")
                break
        else:
            console.insert(tk.END, f"Syntax error: Unexpected symbol {lookahead}")
            break

    if stack or current_token_index < len(token):
        console.insert(tk.END, "\nInput rejected: Syntax error.")
    else:
        console.insert(tk.END, "Input accepted: Syntactically correct.")
