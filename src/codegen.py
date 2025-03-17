from definitions import *
import tkinter as tk

def generate_code(console):
    current_token_index = 0
    output_val = "result = "
    exec_code = []
    locals_dict = {}

    while current_token_index < len(token):
        curr = token[current_token_index]

        if curr in ["int", "str", "var", "chr", "bln", "dec"]: 
            iden = lexeme[current_token_index + 1]
            current_token_index += 3 

            exp = ""
            while token[current_token_index] != ";":
                exp += lexeme[current_token_index] + " "
                current_token_index += 1

            exec_code.append(f"{iden} = {exp.strip()}")

        if curr == "disp":
            output_val += 'f"'
            current_token_index += 2
            curr = token[current_token_index]

            while curr != ")":
                if curr == "&":
                    pass
                elif curr == "str_lit":
                    output_val += lexeme[current_token_index].strip('"')
                else:
                    if curr.startswith("id"):
                        output_val += f"{{{lexeme[current_token_index]}}}"
                    else:
                        exp = ""
                        while curr != ")" and curr != "&":
                            exp += lexeme[current_token_index]
                            if token[current_token_index+1] == ")" or token[current_token_index+1] == "&":
                                break
                            current_token_index += 1
                            curr = token[current_token_index]

                        output_val += f"{{{exp}}}"

                current_token_index += 1
                curr = token[current_token_index]

            output_val += '"'
            exec_code.append(output_val)

        current_token_index += 1

    for code in exec_code:
        exec(code, {}, locals_dict)

    if "result" in locals_dict:
        console.insert(tk.END, locals_dict["result"] + "\n")                     
