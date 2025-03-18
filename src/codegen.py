from definitions import *
import tkinter as tk

def generate_code(console):
    current_token_index = 0
    output_val = "result = "
    exec_code = []
    locals_dict = {}
    isString = False
    isInt = False
    isDec = False
    isBln = False

    while current_token_index < len(token):
        curr = token[current_token_index]

        if curr in ["int", "str", "var", "chr", "bln", "dec"]: 
            exp = ""
            if curr in ["str", "chr"]:
                isString = True
                exp = 'f"'
            elif curr == "int":
                isInt = True
            elif curr == "dec":
                isDec = True
            elif curr == "bln":
                isBln = True
            iden = lexeme[current_token_index + 1]  
            current_token_index += 2 
            
            if token[current_token_index] == "=":
                current_token_index += 1
                curr = token[current_token_index]
                while token[current_token_index] != ";":
                    if curr == "&":
                        pass
                    elif curr == "str_lit":
                        exp += lexeme[current_token_index].strip('"')
                    elif curr == "chr_lit":
                        exp += lexeme[current_token_index].strip("'")
                    else:
                        if curr.startswith("id"):
                            exp += f"{{{lexeme[current_token_index]}}}"
                        else: 
                            if curr in ["int_lit", "dec_lit"]:
                                exp += check_num_lit(current_token_index)
                            else:
                                exp += lexeme[current_token_index] + " "

                    current_token_index += 1
                    curr = token[current_token_index]
                
                if isString:
                    exp += '"'
                    isString = False
                if isInt:
                    exp = f"int(eval(f'{exp}'))" 
                    isInt = False
 
                exec_code.append(f"{iden} = {exp.strip()}")

            elif token[current_token_index] in [",", ";"]:
                curr = token[current_token_index]
                if isString:
                    exp = "none"
                elif isInt:
                    exp = "0"
                elif isDec:
                    exp = "0.0"
                elif isBln:
                    exp = "false"
             
                exec_code.append(f"{iden} = {exp}")

        elif curr == "disp":
            exp = ""
            output_val += 'f"'
            current_token_index += 2
            curr = token[current_token_index]

            while curr != ")":
                if curr == "&":
                    pass
                elif curr == "str_lit":
                    output_val += lexeme[current_token_index].strip('"')
                else:
                    if curr.startswith("id") and token[current_token_index+1] in ["&", ")"]:
                        output_val += f"{{{lexeme[current_token_index]}}}"
                    else:                    
                        parens = 0  

                        while True:
                            if curr == "(":
                                parens += 1
                            elif curr == ")":
                                if parens == 0:
                                    break  
                                parens -= 1

                            if curr == "int_lit" and not isDec:
                                isInt = True
                            elif curr == "dec_lit":
                                isInt = False
                                isDec = True
                            if curr in ["int_lit", "dec_lit"]:
                                exp += check_num_lit(current_token_index)
                            else:
                                exp += lexeme[current_token_index]

                            if current_token_index + 1 < len(token):
                                next_token = token[current_token_index + 1]
                                if next_token == ")" and parens == 0:
                                    break  
                                if next_token == "&":
                                    break  

                            current_token_index += 1
                            curr = token[current_token_index]

                        
                        if isInt:
                            exp = f"int(eval(f'{exp}'))" 
                            isInt = False
                        elif isDec:
                            exp = f"eval(f'{exp}')" 
                            isDec = False
                        output_val += f"{{{exp.strip()}}}"  

                current_token_index += 1
                curr = token[current_token_index]

            output_val += '"'
            exec_code.append(output_val)

        current_token_index += 1

    for code in exec_code:
        exec(code, {}, locals_dict)

    if "result" in locals_dict:
        console.insert(tk.END, locals_dict["result"] + "\n")           

def check_num_lit(token):
    lit = lexeme[token]
    if lit.startswith("~"):
        return lit.replace("~", "-")
    else:
        return lit
