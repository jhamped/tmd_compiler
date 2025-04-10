from definitions import *
import sys
import io
import tkinter as tk
import re

index = 0
code = ""
from tkinter import simpledialog
var_nameList = []


def get_input_from_tkinter():
    # Create a hidden Tkinter root window
    global var_nameList
    input_name = var_nameList.pop(0)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Ask for input using a simple dialog box
    user_input = simpledialog.askstring("", f"Please enter a {input_name}:")
    root.attributes('-topmost', 1)  # This ensures the window is always on top
    
    root.destroy()  # Destroy the root window after input is given
    if user_input is None:
        return None  # Cancel was clicked

    try:
        if '.' in user_input:
            return float(user_input)  # Convert to float
        return int(user_input)  # Convert to int
    except ValueError:
        # If it's not a number, return it as a string with double quotes
        return f'"{user_input}"'
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
def indent_level(indent):
    return "    " * indent 
def getNextToken(current_token_index):
    if current_token_index+1 < len(token):
        return token[current_token_index+1]
    else:
        return ""
def generate_code(console):
    console1 = console
    print(token)
    current_token_index = 0
    trans_code = ""
    indent = 0
    exec_code = []
    #locals_dict = {'console': console}
    

    output_val = ""
    exp = ""
    isString = False
    isInt = False
    isDec = False
    isBln = False
    haveTemp = True
    temp = ""
    unary = ""
    unary_indent = 0
    unary_statement = {}
    unary_dict = {}
    unary_dict = {}

    # Dynamically populate the unary_statement and unary_indent one by one
    def add_statement(stmt, indent):
        if indent not in unary_dict:
            unary_dict[indent] = []
        unary_dict[indent].append(stmt)

    # Function to get all unary statements for a specific unary_indent, one by one
    def get_statements_by_indent(indent_value):
        return unary_dict.get(indent_value, [])
            
    switch_statement = False
    function_name = ""
    
    print("running")
    while current_token_index < len(token):
        curr = token[current_token_index]
        print(f"-current {curr}")
        prev = ""
        if current_token_index <len(token)-1:
            prev = token[current_token_index-1]
            
        isString = False
        isInt = False
        isDec = False
        isBln = False
        isVar = False
        isConversion = False
        if curr == "main":
            trans_code += "def __main__():" 
        elif curr == "{" and (prev == ")" or prev == "main"):
            indent += 1 
            trans_code += "\n" + indent_level(indent)
        elif curr == "}" and (prev == ";" or prev == "}"):
            statements = get_statements_by_indent(indent)
            if statements:
                for stmt in statements:
                    trans_code += f"{stmt}"
                    statements.remove(stmt)

            indent -= 1 
            trans_code += "\n" + indent_level(indent)
        elif curr == ";":
            trans_code += "\n" + indent_level(indent)
        #for ( int i = 0; i < 5; i = i + 1)
        #for i in range(0, 5, 1):
        #while(){} while count < 5:
        #while con_val :
        #Looping Body
        elif curr == "while":
            trans_code += "while "
            exp = ""
            output_val = ""
            current_token_index += 2
            curr = token[current_token_index]

            while curr != ")":
                print(f"---{curr}")
                if curr == "&":
                    pass
                elif curr == "str_lit":
                    output_val += lexeme[current_token_index].strip('"')
                elif curr in ["true", "false"]:
                    trans_code += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    trans_code += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    if curr.startswith("id"):
                        exp += f"{{{lexeme[current_token_index]}}}"
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
                        output_val += f"{exp}"  

                current_token_index += 1
                curr = token[current_token_index]

            output_val += ":"
            exec_code.append(output_val)
            trans_code += output_val
        #for (int i = 0; i < 10 && i != 5; i++) {
        # while i < 10 and i != 5:
        #print(i)
        #i += 1
        elif curr == "for":
            #initialization
            current_token_index += 2
            curr = token[current_token_index]
            temp = ""
            if curr in datatype:
                current_token_index += 1
                curr = token[current_token_index]
            while curr != ";":
                if curr in ["true", "false"]:
                    temp += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    temp += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    temp += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
            trans_code += f"{temp}\n" + indent_level(indent)
            temp = ""
            current_token_index += 1
            curr = token[current_token_index]
            while curr != ";":
                if curr in ["true", "false"]:
                    temp += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    temp += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    temp += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
            
            indent += 1
            trans_code += f"while {temp}: \n" + indent_level(indent)
            
            
            temp = ""
            current_token_index += 1
            curr = token[current_token_index]
            while not (curr == ")" and getNextToken(current_token_index) == "{"):
                if curr in ["++", "--"] or getNextToken(current_token_index) in ["++", "--"]:
                    # Case 1: x++
                    unary = ""
                    if curr.startswith("id") and token[current_token_index + 1] in ["++", "--"]:
                        var_name = lexeme[current_token_index]
                        op = token[current_token_index + 1]
                        if op == "++":
                            #temp += f"{var_name}\n" + indent_level(indent)
                            unary += f"{var_name} += 1\n" + indent_level(indent)
                        else:
                            exec_code.append(f"{var_name} -= 1")
                            #temp += f"{var_name}\n" + indent_level(indent)
                            unary += f"{var_name} -= 1\n" + indent_level(indent)
                        current_token_index += 1  

                    # Case 2: ++x
                    elif curr in ["++", "--"] and token[current_token_index + 1].startswith("id"):
                        op = curr
                        var_name = lexeme[current_token_index + 1]
                        if op == "++":
                            exec_code.append(f"{var_name} += 1")
                            unary += f"{var_name} += 1\n" + indent_level(indent)
                        else:
                            exec_code.append(f"{var_name} -= 1")
                            unary += f"{var_name} -= 1\n" + indent_level(indent)
                        current_token_index += 1 
                    unary_indent = indent
                    unary_statement[unary_indent] = unary
                    
                    add_statement(unary, unary_indent)

                    
                elif curr in ["true", "false"]:
                    temp += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    temp += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    temp += lexeme[current_token_index]
                    
                current_token_index += 1
                curr = token[current_token_index]
            print(f"{curr} {indent}")
            trans_code += f"{temp} \n" + indent_level(indent)
            current_token_index += 1
            curr = token[current_token_index]
        #Conditional Body
        elif curr == "if":
            trans_code += f"if "
            current_token_index += 2
            curr = token[current_token_index]
            while not (curr == ")" and getNextToken(current_token_index) == "{"):
                if curr in ["true", "false"]:
                    trans_code += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    trans_code += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    trans_code += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
            trans_code += ":"
        elif curr == "elif":
            trans_code += f"elif "
            current_token_index += 2
            curr = token[current_token_index]
            while not (curr == ")" and getNextToken(current_token_index) == "{"):
                if curr in ["true", "false"]:
                    trans_code += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    trans_code += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    trans_code += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
            trans_code += ":"
        elif curr == "else":
            trans_code += f"else:" + indent_level(indent)
            indent += 1 
            trans_code += "\n" + indent_level(indent)
            current_token_index+=1
            curr = token[current_token_index]
                
        elif curr == "switch":
            trans_code += f"match "
            current_token_index += 2
            curr = token[current_token_index]
            while curr != ")":
                trans_code += f"{lexeme[current_token_index]}"
                current_token_index += 1
                curr = token[current_token_index]
            trans_code += f": "
        elif curr == "key":
            if token[current_token_index-1] == ";":
                indent -= 1 
                trans_code += "\n" + indent_level(indent)
            trans_code += f"case {lexeme[current_token_index+1]}"
            current_token_index += 1
            curr = token[current_token_index]
        elif curr == ":":
            indent += 1 
            trans_code += ":\n" + indent_level(indent)
        elif curr == "def":
            if token[current_token_index-1] == ";":
                indent -= 1 
                trans_code += "\n" + indent_level(indent)
            trans_code += f"case _"
        #segm a(){} def a:
        elif curr == "segm":
            trans_code += "def "
            tempdata = ""
            while True:
                curr = token[current_token_index]
                print(curr)
                if curr.startswith("id") and token[current_token_index+1] == "(":
                    trans_code += f"{lexeme[current_token_index]}("
                elif curr.startswith("id"):
                    if tempdata != "":
                        trans_code += f"{lexeme[current_token_index]}: {tempdata}"
                        tempdata = ""
                    else:
                        trans_code += f"{lexeme[current_token_index]}"
                elif curr in datatype:
                    pass
                elif curr == ",":
                    trans_code += ","
                elif curr == ")":
                    trans_code += "):"
                    break
                current_token_index += 1
                    
        elif curr in ["int", "str", "chr", "bln", "dec", "var"]: 
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
                trans_code += f"{exp}"
                while lexeme[current_token_index] != ";":
                    exp = ""
                    list = declareMulArray(current_token_index)
                    exp += list[1]
                    current_token_index = list[0]
                    print(f"curr {current_token_index} {lexeme[current_token_index]}")
                    exec_code.append(f"{exp}")
                    trans_code += f"{exp}"
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
                            #exp += f"{{{lexeme[current_token_index]}}}"
                            exp += f"{lexeme[current_token_index]}"
                        elif curr in ["int", "str", "chr", "bln", "dec"]:
                            isConversion = True
                            #if curr == "dec":
                            #    exp += float
                            #else:
                            #    exp += curr
                            print("conversion")
                        elif curr == "(" and isConversion:
                            #lexemetoken = lexeme[current_token_index+1]
                            #exp += f"({lexemetoken})"
                            #current_token_index += 2
                            #curr = token[current_token_index]
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
                    trans_code += f"{iden} = {exp.strip()}\n" + indent_level(indent)
                    print(f"dec {iden} = {exp.strip()}")

                elif token[current_token_index] in [",", ";"]:
                    curr = token[current_token_index]
                    if isString:
                        exp = "None"
                        if curr != ";":
                            exp+="\n"+indent_level(indent)
                    elif isInt:
                        exp = "0"
                        if curr != ";":
                            exp+="\n"+indent_level(indent)
                    elif isDec:
                        exp = "0.0"
                        if curr != ";":
                            exp+="\n"+indent_level(indent)
                    elif isBln:
                        exp = "false"
                        if curr != ";":
                            exp+="\\n"+indent_level(indent)
                
                    exec_code.append(f"{iden} = {exp}")
                    trans_code += f"{iden} = {exp}"
                    print(exec_code)
                if isString:
                    exp = 'f"'
                else: 
                    exp = ""
                if curr == ";":
                    trans_code += "\n"+indent_level(indent)
                    break 
        
        elif curr == "disp":
            exp = ""
            output_val = 'print(f"'
            current_token_index += 2
            curr = token[current_token_index]

            while curr != ")":
                """
                if curr.startswith("id") and token[current_token_index + 1] in ["++", "--"]:
                    var_name = lexeme[current_token_index]
                    op = token[current_token_index + 1]
                    if op == "++":
                        output_val += f"{var_name}"
                        #output_val += f"{var_name} += 1\n" + indent_level(indent)
                    else:
                        exec_code.append(f"{var_name} -= 1")
                        output_val += f"{var_name}"
                        #output_val += f"{var_name} -= 1\n" + indent_level(indent)
                    current_token_index += 2
                    curr = token[current_token_index]  
                    

                # Case 2: ++x
                elif curr in ["++", "--"] and token[current_token_index + 1].startswith("id"):
                    op = curr
                    var_name = lexeme[current_token_index + 1]
                    if op == "++":
                        output_val.append(f"{var_name} += 1")
                        trans_code += f"{var_name} += 1\n" + indent_level(indent)
                    else:
                        exec_code.append(f"{var_name} -= 1")
                        output_val += f"{var_name} -= 1\n" + indent_level(indent)
                    current_token_index += 1 
                    curr = token[current_token_index]"""
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
                        exp = f"eval(f\"{exp}\")"
                        output_val += f"{{{exp.strip()}}}"  

                current_token_index += 1
                curr = token[current_token_index]

            output_val += "\", end=\"\")"
            exec_code.append(output_val)
            trans_code += output_val
         
        elif curr == "insp":
            current_token_index += 2
            curr = token[current_token_index]
            variable_insp = ""
            while curr != ";":
                if curr == ")" and getNextToken(current_token_index) == ";":
                    pass
                else:
                    variable_insp += f"{lexeme[current_token_index]}"
                current_token_index += 1
                curr = token[current_token_index]
            global var_nameList
            var_nameList.append(variable_insp)
            trans_code += f"{variable_insp} = get_input_from_tkinter()\n" + indent_level(indent)
            #trans_code += f"{variable_insp} = console.get_input1()\n" + indent_level(indent)
        elif curr in ["++", "--"] or getNextToken(current_token_index) in ["++", "--"]:
            # Case 1: x++
            if curr.startswith("id") and token[current_token_index + 1] in ["++", "--"]:
                var_name = lexeme[current_token_index]
                op = token[current_token_index + 1]
                if op == "++":
                    trans_code += f"{var_name}\n" + indent_level(indent)
                    trans_code += f"{var_name} += 1\n" + indent_level(indent)
                else:
                    exec_code.append(f"{var_name} -= 1")
                    trans_code += f"{var_name}\n" + indent_level(indent)
                    rans_code += f"{var_name} -= 1\n" + indent_level(indent)
                current_token_index += 1  

            # Case 2: ++x
            elif curr in ["++", "--"] and token[current_token_index + 1].startswith("id"):
                op = curr
                var_name = lexeme[current_token_index + 1]
                if op == "++":
                    exec_code.append(f"{var_name} += 1")
                    trans_code += f"{var_name} += 1\n" + indent_level(indent)
                else:
                    exec_code.append(f"{var_name} -= 1")
                    trans_code += f"{var_name} -= 1\n" + indent_level(indent)
                current_token_index += 1 
            
        elif curr.startswith("id"):
            print("pass id")
            print(f"next {token[current_token_index + 1]}")
            exp = ""
            output_val = ""
            if token[current_token_index+1] == "(":
                print("function call ID")
                trans_code += f"{lexeme[current_token_index]}("
                current_token_index += 2
                curr = token[current_token_index]
                while curr != ")":
                    print(curr)
                    if curr == "&":
                        pass
                    elif curr == "str_lit":
                        output_val += lexeme[current_token_index].strip('"')
                    elif curr in ["true", "false"]:
                        output_val += lexeme[current_token_index].capitalize()
                    else:
                        if curr.startswith("id") and token[current_token_index+1] in ["&", ")"]:
                            output_val += f"{lexeme[current_token_index]}"
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
                                print(f"a {curr}")
                                current_token_index += 1
                                curr = token[current_token_index]
                            
                            exp = f"{exp}"
                            print(f"asdad {exp}")
                            output_val += f"{exp.strip()}"  
                    current_token_index += 1
                    curr = token[current_token_index]
                output_val += ")"
                exec_code.append(output_val)
                trans_code += output_val
            if token[current_token_index + 1] in assignment_operator or token[current_token_index + 1] == "[":
                print(f"pass id2 ")
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
                #if assign not in exec_code
                exec_code.append(f"{assign}{exp.strip()}")
                trans_code += f"{assign}{exp.strip()}" + "\n" + indent_level(indent)
                print(f"assign {assign}{exp.strip()}")
        
        elif curr == "ret":
            trans_code += "return "
            current_token_index += 1
            curr = token[current_token_index]
            curlexeme = lexeme[current_token_index]
            while curlexeme != ";":
                trans_code += f"{curlexeme} "
                current_token_index += 1
                curlexeme = lexeme[current_token_index]
            curr = token[current_token_index]
            
        elif curr == "rsm":
            trans_code += "continue"
            current_token_index += 1
            curr = token[current_token_index]
            
        elif curr == "brk":
            trans_code += "break"
            current_token_index += 1
            curr = token[current_token_index]
        
        elif curr == "exit":
            trans_code += "exit() "
            current_token_index += 1
            curr = token[current_token_index]
        current_token_index += 1

    print(f"exp {exp}")
    print(f"exec_code {exec_code}") 

    print(f"---trans code---")
    print(trans_code)
    print(f"run")
    
    #exec(trans_code, globals(), locals_dict)
    #console.insert(tk.END,"run the exec.")
    output_buffer = io.StringIO()
    
    # Redirect stdout to our buffer
    old_stdout = sys.stdout
    sys.stdout = output_buffer
    """
    try:
    # Execute the code
        trans_code += "\n__main__()"
        exec(trans_code, globals())
    except NameError as e:
        error_msg = f"NameError: {str(e)}\nThis usually means you're using a variable before declaring it.\n"
        console.insert(tk.END, error_msg, "error")
        # Also print the generated code for debugging
        console.insert(tk.END, "\nGenerated code that caused the error:\n", "error")
        console.insert(tk.END, trans_code + "\n", "error")
    except Exception as e:
        import traceback
        traceback.print_exc(file=output_buffer)
        # Restore stdout
        sys.stdout = old_stdout
    """
    try:
    # Execute the code
        trans_code += "\n__main__()"
        exec(trans_code, globals())
    except NameError as e:
        console.insert(tk.END, f"{e}\n", "error")
    except Exception as e:
        import traceback
        last_line = traceback.format_exception_only(type(e), e)[-1].strip()
        console.insert(tk.END, f"{last_line}\n", "error")

    # Get the captured output
    captured_output = output_buffer.getvalue()
    #Also insert the generated code for reference
    """
    console.insert(tk.END, "\n=== Generated Code ===\n")
    console.insert(tk.END, trans_code)
    console.insert(tk.END, "\n=== End of Code ===\n")
    """
    
    # Insert the output into the console widget
    console.insert(tk.END, "\n=== Execution Output ===\n")
    console.insert(tk.END, captured_output)
    #console.insert(tk.END, "\n=== End of Output ===\n")
    

              
