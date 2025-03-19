from definitions import *
import tkinter as tk
import re

def generate_code(console):
    current_token_index = 0
    output_val = ""
    exec_code = []
    locals_dict = {}
    results = []
    isString = False
    isInt = False
    isDec = False
    isBln = False

    while current_token_index < len(token):
        curr = token[current_token_index]
        isString = False
        isInt = False
        isDec = False
        isBln = False
        isVar = False
        isConversion = False

        if curr in ["int", "str", "chr", "bln", "dec", "var"]: 
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
            elif curr == "var":
                isVar = True
            if token[current_token_index+1] == "[":
                exp = ""
                list = declareArray(current_token_index)
                exp += list[1]
                current_token_index = list[0]
                print(f"curr {current_token_index} {lexeme[current_token_index]}")
                exec_code.append(f"{exp}")
                while lexeme[current_token_index] != ";":
                    exp = ""
                    list = declareMulArray(current_token_index)
                    exp += list[1]
                    current_token_index = list[0]
                    print(f"curr {current_token_index} {lexeme[current_token_index]}")
                    exec_code.append(f"{exp}")
                continue

            while True:
                iden = lexeme[current_token_index + 1]  
                print(f"curr1 {current_token_index} {lexeme[current_token_index]}")
                current_token_index += 2 
                
                if token[current_token_index] == "=":
                    current_token_index += 1
                    curr = token[current_token_index]
                    while token[current_token_index] not in [",", ";"]:
                        if curr == "&":
                            pass
                        elif curr == "str_lit":
                            if not isVar:
                                exp += lexeme[current_token_index].strip('"')
                            else:
                                exp += lexeme[current_token_index]
                        elif curr == "chr_lit":
                            if not isVar:
                                exp += lexeme[current_token_index].strip("'")
                            else:
                                exp += lexeme[current_token_index]
                        elif curr in ["true", "false"]:
                            exp += lexeme[current_token_index].capitalize()
                        elif curr.startswith("id"):
                            exp += f"{{{lexeme[current_token_index]}}}"
                        elif curr in ["int", "str", "chr", "bln", "dec"]:
                            isConversion = True
                            print("conversion")
                        elif curr == "(" and isConversion:
                            pass
                        elif curr == ")" and isConversion:
                            isConversion = False
                            pass
                        else:
                            if curr in ["int_lit", "dec_lit"]:
                                exp += checkNumLit(current_token_index)
                            else:
                                exp += lexeme[current_token_index]

                        current_token_index += 1
                        curr = token[current_token_index]
                    
                    if isString:
                        exp += '"'
                    if isInt:
                        print(f"int {isInt} {exp}")
                        exp = f"int(eval(f'{exp}'))" 


                    exec_code.append(f"{iden} = {exp.strip()}")
                    print(f"dec {iden} = {exp.strip()}")

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
                    
                if isString:
                    exp = 'f"'
                else: exp = ""

                if curr == ";":
                    break 

        elif curr == "disp":
            exp = ""
            output_val = 'result = f"'
            current_token_index += 2
            curr = token[current_token_index]

            while curr != ")":
                if curr == "&":
                    pass
                elif curr == "str_lit":
                    output_val += lexeme[current_token_index].strip('"')
                elif curr in ["true", "false"]:
                    output_val += lexeme[current_token_index].capitalize()
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
                                exp += checkNumLit(current_token_index)
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

                        exp = f"eval(f'{exp}')"
                        output_val += f"{{{exp.strip()}}}"  

                current_token_index += 1
                curr = token[current_token_index]

            output_val += '"'
            exec_code.append(output_val)

        elif curr.startswith("id"):
            print("pass id")
            print(f"next {token[current_token_index + 1]}")
            if token[current_token_index + 1] in assignment_operator or token[current_token_index + 1] == "[":
                print("pass id2")
                assign = f"{lexeme[current_token_index]}"
                current_token_index += 1
                curr = lexeme[current_token_index]

                while curr not in assignment_operator:
                    print("pass id3")
                    assign += lexeme[current_token_index]
                    current_token_index += 1
                    curr = lexeme[current_token_index]

                assign += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
                exp = ""
                while curr != ";":
                    print("pass id4")
                    if curr == "&":
                        pass
                    elif curr == "str_lit":
                        exp += lexeme[current_token_index].strip('"')
                    elif curr == "chr_lit":
                        exp += lexeme[current_token_index].strip("'")
                    elif curr.startswith("id"):
                        exp += f"{{{lexeme[current_token_index]}}}"
                    else:
                        if curr in ["int_lit", "dec_lit"]:
                            if curr == "dec_lit":
                                isDec = True
                            exp += checkNumLit(current_token_index)
                        else:
                            exp += lexeme[current_token_index]

                    current_token_index += 1
                    curr = token[current_token_index]
                
                exp = f"eval(f'{exp}')" 

                exec_code.append(f"{assign}{exp.strip()}")
                print(f"{assign}{exp.strip()}")

        #--------------------------------------
        current_token_index += 1


    print(exec_code)
    for code in exec_code:
        exec(code, {}, locals_dict)
        print(locals_dict)

        for key, value in locals_dict.items():
            if isinstance(value, bool):
                locals_dict[key] = str(value).lower()

        if "result" in locals_dict:
            results.append(locals_dict["result"])
        locals_dict.pop("result", None)

    results = [re.sub(r'(?<=\s)-(\d+)', r'~\1', str(res).replace("True", "true").replace("False", "false")) for res in results]

    for res in results:
        console.insert(tk.END, res)           

#--------------FUNCTIONS--------------------
def checkNumLit(token_index):
    lit = lexeme[token_index]
    if lit.startswith("~"):
        return lit.replace("~", "-")
    else:
        return lit
    
def declareArray(token_index):
    token_index += 2
    
    if token[token_index] == ",":
        iden = lexeme[token_index+2]
        token_index += 3

        list = initArray(token_index)
        exp = list[1]
    else:
        iden = lexeme[token_index+1]
        token_index += 2

        list = initArray(token_index)
        exp = list[1]

    exp = f"{iden} = {exp.replace("{", "[").replace("}", "]")}"
    return [list[0], exp]
        
def initArray(token_index):
    exp = ""
    if token[token_index] == "=":
        token_index += 1
        curr = lexeme[token_index]
        braces = 0
        while True:
            if curr in ["true", "false"]:
                curr = curr.capitalize()

            exp += curr
            token_index += 1
            curr = lexeme[token_index]

            print(f"curr {curr} {braces}")
            if curr == "{":
                braces += 1
            elif curr == "}":
                if braces == 0:
                    break  
                braces -= 1

        exp += curr
        token_index += 1
    elif token[token_index] in [",", ";"]:
        exp = "[]"

    print(f"exp {exp}")
    return [token_index, exp]

def declareMulArray(token_index):
    iden = lexeme[token_index + 1]
    token_index += 2

    list = initArray(token_index)
    exp = list[1]

    exp = f"{iden} = {exp.replace("{", "[").replace("}", "]")}"
    return [list[0], exp]
