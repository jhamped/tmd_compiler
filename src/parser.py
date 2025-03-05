from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def parse(console):    
    current_token_index = 0
    
    def error_message(error):
        line = rows[current_token_index] if current_token_index < len(rows) else "0"
        column = col[current_token_index] if current_token_index < len(col) else "0"
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
    prevlookahead = ""
    recoverytop = ""
    blockFound = False
    recovery_nonterminal = ["<statements>", "<conditional_body>", "<nested_foreach_body>", "<foreach_body>"]
    while stack:
        if len(token) > current_token_index:
            lookahead = get_lookahead()
        #else:
            #error_message("End of file")
        top = stack.pop()
        if top in recovery_nonterminal:
            recoverytop = top
        lookahead = get_lookahead()
        if lookahead is None:
            error_message("Unexpected End-of-File. ")
            return
        if top == lookahead:
            # Terminal matches lookahead, consume the token
            print(f"Match: {lookahead}")
            prevlookahead = lookahead
            current_token_index += 1
            if blockFound == True:
                stack.append("}")
                stack.append(recoverytop)
                blockFound = False
        elif top in parsing_table:
            # Non-terminal: use the parsing table
            rule = parsing_table[top].get(lookahead)
            if rule:
                print(f"Apply rule: {top} -> {' '.join(rule)}")
                if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                    stack.extend(reversed(rule))
            else:
                error_message(f"Unexpected {lookahead} after {prevlookahead} Expected: {list(parsing_table.get(top, {}).keys())} ")
                #error_message(f"Expected: {list(parsing_table.get(top, {}).keys())} ")
                #return
                recovery_tokens = [";", "}"]  
                while current_token_index < len(token) and get_lookahead() not in recovery_tokens:
                    if get_lookahead() == "{":
                        blockFound = True
                    current_token_index += 1
                current_token_index +=1
                while top != recoverytop:
                    top = stack.pop()
                if recoverytop not in stack:
                    stack.append(recoverytop)
                if top == "<global_dec>":
                    stack.pop()
        else:
            error_message(f"Unexpected symbol {lookahead} after {prevlookahead} Expected: {top}")
            return
    
    if stack or current_token_index < len(token):
        error_message(f"Unexpected {get_lookahead()} after main function")
    #else:
        #print("Input accepted: Syntactically correct.")
