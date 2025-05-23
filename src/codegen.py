from definitions import *
import sys
import io
import tkinter as tk
import re
import tempfile
import subprocess
import os
import threading
import builtins
index = 0
code = ""
from tkinter import simpledialog
var_nameList = []
scope_stack = ["global"]

def checkNumLit(token_index):
    lit = lexeme[token_index]
    if lit.startswith("~"):
        return lit.replace("~", "-")
    else:
        return lit

def declareArray(token_index, iden, var_type, dims):
    print(f"declaring array {token_index}")
    try:
        # Get Identifier
        #if token_index >= len(token) or not token[token_index].startswith("id"):
        #    raise SyntaxError(f"Expected array name after array type declaration at token {token_index}. Found: {token[token_index] if token_index < len(token) else 'EOF'}")
        
        #iden = lexeme[token_index]
        token_index += 1
        current_scope = scope_stack[-1] if scope_stack else "global"
        
        # Check for initialization
        if token_index < len(token) and token[token_index] == "=":
            token_index += 1
            if token_index < len(token) and token[token_index] == "{":
                # Handle initialized array
                values = []
                token_index += 1
                while token_index < len(token) and token[token_index] != "}":
                    if dims == 1:
                        # 1D array: {1, 2, 3}
                        val = lexeme[token_index]
                        if token[token_index] in ["true", "false"]:
                            val = val.capitalize()
                        elif token[token_index] in ["int_lit", "dec_lit"]:
                            val = checkNumLit(token_index)
                        values.append(val)
                        token_index += 1
                        if token_index < len(token) and token[token_index] == ",":
                            token_index += 1
                    elif dims == 2:
                        # 2D array: {{1,2},{3,4}}
                        if token_index < len(token) and token[token_index] == "{":
                            token_index += 1
                            row = []
                            while token_index < len(token) and token[token_index] != "}":
                                val = lexeme[token_index]
                                if token[token_index] in ["true", "false"]:
                                    val = val.capitalize()
                                elif token[token_index] in ["int_lit", "dec_lit"]:
                                    val = checkNumLit(token_index)
                                row.append(val)
                                token_index += 1
                                if token_index < len(token) and token[token_index] == ",":
                                    token_index += 1
                            values.append(row)
                            token_index += 1
                            if token_index < len(token) and token[token_index] == ",":
                                token_index += 1
                if token_index < len(token):
                    token_index += 1  # Skip past }
                exp = f"{iden} = DynamicArray('{var_type}', dims={dims}, initial_values={values}, scope='{current_scope}')"
            else:
                exp = f"{iden} = DynamicArray('{var_type}', dims={dims}, scope='{current_scope}')"
        else:
            exp = f"{iden} = DynamicArray('{var_type}', dims={dims}, scope='{current_scope}')"
        
        return [token_index, exp]
    
    except Exception as e:
        print(f"Error in array declaration at token {token_index}: {e}")
        print(f"Current token: {token[token_index] if token_index < len(token) else 'EOF'}")
        print(f"Surrounding tokens: {token[max(0,token_index-3):min(len(token),token_index+3)]}")
        raise

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

            if curr == "{":
                braces += 1
            elif curr == "}":
                if braces == 0:
                    break  
                braces -= 1

        exp += curr
        token_index += 1
    elif token[token_index] in [",", ";"]:
        # Initialize empty dynamic array
        exp = "[]"

    return [token_index, exp]

def handleArrayOperations(var_name, operation, value=None):

    if operation == "push":
        return f"{var_name}.append({value})"
    elif operation == "pop":
        return f"{var_name}.pop()"
    elif operation == "insert":
        return f"{var_name}.insert({value[0]}, {value[1]})"
    elif operation == "remove":
        return f"{var_name}.remove({value})"
    elif operation == "resize":
        return f"{var_name} = {var_name}[:{value}] + [None]*({value}-len({var_name}))"

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
def getPrevToken(current_token_index):
    if current_token_index-1 > 0:
        return token[current_token_index-1]
    else:
        return ""
def generate_code(console):
    if errorflag[0] == True:  
        return
    else:
        console.delete("1.0", tk.END)
    global scope_stack
    # Start with global scope
    scope_stack = ["global"]
    console1 = console
    print(token)
    current_token_index = 0
    trans_code = """
class DynamicArray:
    def __init__(self, dtype, dims=1, initial_values=None, scope=None):
        self.dtype = dtype
        self.default = {'int':0, 'dec':0.0, 'str':'None', 'chr':"None", 'bln':False, 'var':None}.get(dtype, None)
        self.dims = dims
        self.scope = scope
        
        if dims == 1:
            self.data = []
            if initial_values is not None:
                for val in initial_values:
                    if dtype == 'int':
                        self.data.append(int(val))
                    elif dtype == 'dec':
                        self.data.append(float(val))
                    else:
                        self.data.append(val.strip('"').strip("'"))
        elif dims == 2:
            self.data = []
            if initial_values is not None:
                for row in initial_values:
                    new_row = []
                    for val in row:
                        if dtype == 'int':
                            new_row.append(int(val))
                        elif dtype == 'dec':
                            new_row.append(float(val))
                        else:
                            new_row.append(val.strip('"').strip("'"))
                    self.data.append(new_row)
    def __len__(self):
        return len(self.data)
    def __getitem__(self, index):
        if isinstance(index, tuple):  # Handle comma syntax (1,2)
            row, col = index
            if row >= len(self.data):
                return self.default
            if col >= len(self.data[row]):
                return self.default
            return self.data[row][col]
        else:  # Single index access
            if index >= len(self.data):
                return self.default
            return self.data[index]
    
    def __setitem__(self, index, value):
        if isinstance(index, tuple):  # Handle comma syntax (1,2)
            row, col = index
            while row >= len(self.data):
                self.data.append([])
            while col >= len(self.data[row]):
                self.data[row].append(self.default)
            if self.dtype == 'int':
                self.data[row][col] = int(value)
            elif self.dtype == 'dec':
                self.data[row][col] = float(value)
            else:
                self.data[row][col] = value
        else:  # Single index
            while index >= len(self.data):
                self.data.append(self.default)
            if self.dtype == 'int':
                self.data[index] = int(value)
            elif self.dtype == 'dec':
                self.data[index] = float(value)
            else:
                self.data[index] = value
    
    def __repr__(self):
        return str(self.data)
"""
    indent = 0
    linelevel = 0
    exec_code = []
    #locals_dict = {'console': console}
    symbol_table = {}

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
    declared_globals_in_functions = {} 
    current_function_scope = None
    isDoWhile = False
    def current_scope():
        print(f"Current Scope: {scope_stack[-1] if scope_stack else "global"}")
        return scope_stack[-1] if scope_stack else "global"
    
    def enter_scope(scope_type):
        nonlocal current_function_scope, declared_globals_in_functions
        print(f"Enter Scope: {scope_type}:{len(scope_stack)}")
        scope_stack.append(f"{scope_type}:{len(scope_stack)}")
        if scope_type:
            current_function_scope = scope_stack[-1]
            declared_globals_in_functions[current_function_scope] = set()
    
    def exit_scope():
        nonlocal current_function_scope
        print(f"Exit Scope: {current_function_scope}/{scope_stack[-1]}/{len(scope_stack)}")
        if len(scope_stack) > 1:  
            popped_scope = scope_stack.pop()
            if popped_scope:
                current_function_scope = scope_stack[-1] if len(scope_stack) > 1 else None
    def emit_global(var_name, indent):
        nonlocal current_function_scope, declared_globals_in_functions
        
        if current_function_scope is None:
            return ""  
        
        var_info = symbol_table.get(var_name, {})
        is_global_var = var_info.get("scope", "") == "global"
        
        if not is_global_var:
            return "" 
        
        if var_name in declared_globals_in_functions.get(current_function_scope, set()):
            return ""  
        
        declared_globals_in_functions[current_function_scope].add(var_name)
        
        return f"global {var_name}\n{indent_level(indent)}"
    def add_statement(stmt, indent):
        if indent not in unary_dict:
            unary_dict[indent] = []
        unary_dict[indent].append(stmt)

    def get_statements_by_indent(indent_value):
        return unary_dict.get(indent_value, [])

    switch_statement = False
    function_name = ""
    isSwitchStatement = False
    print("running")
    while current_token_index < len(token):
        if errorflag[0] == True:  
            return
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
        #Code Structure Handling
        if curr == "main":
            trans_code += "def __main__():"
            enter_scope("function:main")
            indent += 1
            trans_code += "\n" + indent_level(indent)
            current_token_index += 1
            curr = token[current_token_index]
        elif curr == "{":
            
            if prev == ")" or prev == "main":
                if getNextToken(current_token_index) == "}":
                    trans_code += "\n" + indent_level(indent+1) +"pass\n" + indent_level(indent)
                    enter_scope(f"block:{linelevel+1}")
                else:
                    indent += 1
                    trans_code += "\n" + indent_level(indent)
                    enter_scope(f"block:{linelevel}")
                linelevel += 1
        
        elif curr == "}":
            if prev == ";" or prev == "}":
                statements = get_statements_by_indent(indent)
                if statements:
                    for stmt in statements:
                        trans_code += f"{stmt}"
                        statements.remove(stmt)
                if prev == ";" and isSwitchStatement:
                    indent -=2
                    isSwitchStatement = False
                else:
                    indent -= 1
                trans_code += "\n" + indent_level(indent)
                exit_scope() 
        elif curr == ";":
            trans_code += "\n" + indent_level(indent)
        #Looping Body
        elif curr == "while":
            #do while
            if isDoWhile:
                isDoWhile = False
                trans_code += "\n"+indent_level(indent+1)+"if "
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
                            id_name = lexeme[current_token_index]
                            if id_name in dir(builtins) and id_name not in ["True", "False", "true", "false"]:
                                id_name = f"_{id_name}"
                            prev_type = symbol_table.get(id_name, {}).get("type", None)
                            if prev_type in ["str", "chr"]:
                                exp += f"\"{{{lexeme[current_token_index]}}}\""
                            else:
                                if token[current_token_index].startswith("id"):
                                    iden = lexeme[current_token_index]
                                    if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                                        iden = f"_{iden}"
                                    exp += f"{{{iden}}}"
                                else:
                                    exp += f"{{{lexeme[current_token_index]}}}"
                            if getNextToken(current_token_index) == ")":
                                trans_code += f"{id_name}"
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
                                elif curr == "chr_lit":
                                    exp += lexeme[current_token_index].replace("'", '"')
                                elif curr.startswith("id"):
                                    id_name = lexeme[current_token_index]
                                    prev_type = symbol_table.get(id_name, {}).get("type", None)
                                    if prev_type in ["str", "chr"]:
                                        exp += f"\"{{{lexeme[current_token_index]}}}\""
                                    else:
                                        exp += f"{{{lexeme[current_token_index]}}}"
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
                trans_code += output_val+  "break"
            else:
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
                            id_name = lexeme[current_token_index]
                            prev_type = symbol_table.get(id_name, {}).get("type", None)
                            if prev_type in ["str", "chr"]:
                                exp += f"\"{{{lexeme[current_token_index]}}}\""
                            else:
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
                                elif curr == "chr_lit":
                                    exp += lexeme[current_token_index].replace("'", '"')
                                elif curr.startswith("id"):
                                    id_name = lexeme[current_token_index]
                                    prev_type = symbol_table.get(id_name, {}).get("type", None)
                                    if prev_type in ["str", "chr"]:
                                        exp += f"\"{{{lexeme[current_token_index]}}}\""
                                    else:
                                        exp += f"{{{lexeme[current_token_index]}}}"
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
                    if token[current_token_index].startswith("id"):
                        iden = lexeme[current_token_index]
                        if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                            iden = f"_{iden}"
                        temp += iden
                    else:
                        temp += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
            trans_code += f"{temp}\n" + indent_level(indent)
            temp = ""
            current_token_index += 1
            curr = token[current_token_index]
            #Condition
            while curr != ";":
                if curr in ["true", "false"]:
                    temp += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    temp += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    if token[current_token_index].startswith("id"):
                        iden = lexeme[current_token_index]
                        if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                            iden = f"_{iden}"
                        temp += iden
                    else:
                        temp += lexeme[current_token_index]
                current_token_index += 1
                curr = token[current_token_index]
            
            indent += 1
            trans_code += f"while {temp}: \n" + indent_level(indent)
            
            #iteration
            temp = ""
            current_token_index += 1
            curr = token[current_token_index]
            while not (curr == ")" and getNextToken(current_token_index) == "{"):
                if curr in ["++", "--"] or getNextToken(current_token_index) in ["++", "--"]:
                    # Case 1: x++
                    unary = ""
                    if curr.startswith("id") and token[current_token_index + 1] in ["++", "--"]:
                        var_name = lexeme[current_token_index]
                        if var_name in dir(builtins) and var_name not in ["True", "False", "true", "false"]:
                            var_name = f"_{var_name}"
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
                        if var_name in dir(builtins) and var_name not in ["True", "False", "true", "false"]:
                            var_name = f"_{var_name}"
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
        elif curr == "foreach":
            trans_code += "\n" + indent_level(indent) + f"__index25 = 0"
            trans_code += "\n" + indent_level(indent) + f"for "
            current_token_index += 3
            curr = token[current_token_index]
            for_iden = lexeme[current_token_index]
            if for_iden in dir(builtins) and for_iden not in ["True", "False", "true", "false"]:
                for_iden = f"_{for_iden}"
            trans_code += f"{for_iden} in "
            current_token_index += 2
            for_iden = lexeme[current_token_index]
            if for_iden in dir(builtins) and for_iden not in ["True", "False", "true", "false"]:
                for_iden = f"_{for_iden}"
            trans_code += f"{for_iden}:"
            current_token_index += 1
            curr = token[current_token_index]
            
            trans_code += "\n" + indent_level(indent+1) + f"if eval('len({for_iden}) < __index25+1'):"
            trans_code += "\n" + indent_level(indent+2) + f"break"
            trans_code += "\n" + indent_level(indent+1) + f"else:"
            trans_code += "\n" + indent_level(indent+2) + f"__index25 += 1"
            
        elif curr == "do":
            isDoWhile = True
            current_token_index += 1
            curr = token[current_token_index]
            indent +=1
            trans_code += "while True:" + "\n" + indent_level(indent)
        #Conditional Body
        elif curr == "if":
            trans_code += f"if "
            current_token_index += 2
            curr = token[current_token_index]
            while not (curr == ")" and getNextToken(current_token_index) == "{"):
                print(f"CONDITION IF {lexeme[current_token_index]}")
                if curr in ["true", "false"]:
                    trans_code += lexeme[current_token_index].capitalize()
                elif curr in ["&&", "||", "!"]:
                    trans_code += {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                else:
                    if token[current_token_index].startswith("id"):
                        iden = lexeme[current_token_index]
                        if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                            iden = f"_{iden}"
                        trans_code += iden
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
                    if token[current_token_index].startswith("id"):
                        iden = lexeme[current_token_index]
                        if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                            iden = f"_{iden}"
                        trans_code += iden
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
            isSwitchStatement = True
            trans_code += f"match "
            current_token_index += 2
            curr = token[current_token_index]
            while curr != ")":
                trans_code += f"{lexeme[current_token_index]}"
                current_token_index += 1
                curr = token[current_token_index]
                if curr.startswith("id"):
                    iden = lexeme[current_token_index]
                    if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                        iden = f"_{iden}"
                    curr = iden
            trans_code += f": "
        elif curr == "key":
            if token[current_token_index-1] == ";":
                indent -= 1 
                trans_code += "\n" + indent_level(indent)
            iden = lexeme[current_token_index+1]
            if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                iden = f"_{iden}"
            trans_code += f"case {iden}"
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
        #Unary Statement
        elif curr in ["++", "--"] or getNextToken(current_token_index) in ["++", "--"]:
            # Case 1: x++
            if curr.startswith("id") and token[current_token_index + 1] in ["++", "--"]:
                var_name = lexeme[current_token_index]
                if var_name in dir(builtins) and var_name not in ["True", "False", "true", "false"]:
                    var_name = f"_{var_name}"
                op = token[current_token_index + 1]
                if op == "++":
                    trans_code += f"{var_name} += 1\n" + indent_level(indent)
                else:
                    exec_code.append(f"{var_name} -= 1")
                    trans_code += f"{var_name} -= 1\n" + indent_level(indent)
                current_token_index += 1
                curr = token[current_token_index]  

            # Case 2: ++x
            elif curr in ["++", "--"] and token[current_token_index + 1].startswith("id"):
                op = curr
                var_name = lexeme[current_token_index + 1]
                if var_name in dir(builtins) and var_name not in ["True", "False", "true", "false"]:
                    var_name = f"_{var_name}"
                if op == "++":
                    exec_code.append(f"{var_name} += 1")
                    trans_code += f"{var_name} += 1\n" + indent_level(indent)
                else:
                    exec_code.append(f"{var_name} -= 1")
                    trans_code += f"{var_name} -= 1\n" + indent_level(indent)
                current_token_index += 1
                curr = token[current_token_index] 
        #Function
        elif curr == "segm":
            trans_code += "def "
            tempdata = ""
            while True:
                curr = token[current_token_index]
                print(curr)
                if curr.startswith("id") and token[current_token_index+1] == "(":
                    iden = lexeme[current_token_index]
                    if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                        iden = f"_{iden}"
                    trans_code += f"{iden}("
                elif curr.startswith("id"):
                    iden = lexeme[current_token_index]
                    if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                        iden = f"_{iden}"
                    if tempdata != "":
                        trans_code += f"{iden}: {tempdata}"
                        tempdata = ""
                    else:
                        trans_code += f"{iden}"
                elif curr in datatype:
                    pass
                elif curr == ",":
                    trans_code += ","
                elif curr == ")":
                    trans_code += "):"
                    break
                current_token_index += 1
        #Variable Declaration        
        elif curr in ["int", "str", "chr", "bln", "dec", "var"]: 
            exp = ""
            var_type = curr
            
            isString = False
            exp_parts = []
            if curr in ["str", "chr"]:
                isString = True
                #exp = 'f"'
                #exp_parts.append("")
            elif curr == "int":
                isInt = True
            elif curr == "dec":
                isDec = True
            elif curr == "bln":
                isBln = True
            elif curr == "var":
                isVar = True
            if token[current_token_index+1] == "[":
                # Handle array declarations
                dims = 1
                var_type = curr
                while True:
                    print(f"ARRAY TOKEN {token[current_token_index]}")
                    
                    while curr != ",":
                        print(f"curr {curr}")
                        if curr.startswith("id"):
                            break
                        if token[current_token_index] == "[":
                            current_token_index += 1
                            curr = token[current_token_index]
                            if current_token_index < len(token) and curr == ",":
                                dims = 2
                                current_token_index += 1 # Skip past ,]
                            elif curr == "]":
                                pass  # Skip past ]
                        current_token_index += 1
                        curr = token[current_token_index]
                    array_iden = lexeme[current_token_index]
                    if array_iden in dir(builtins) and array_iden not in ["True", "False", "true", "false"]:
                        array_iden = f"_{array_iden}"
                    result = declareArray(current_token_index, array_iden, var_type, dims)
                    current_token_index = result[0]
                    curr = token[current_token_index]
                    array_decl = result[1]
                    print(f"DONE {curr}")
                    # Add to symbol table
                    array_name = array_decl.split('=')[0].strip()
                    symbol_table[array_name] = {
                        "type": var_type,
                        "scope": current_scope(),
                        "line": current_token_index,
                        "is_array": True,
                        "dims": 2 if "[,]" in token[current_token_index-5:current_token_index] else 1
                    }
                    
                    # Add to generated code
                    exec_code.append(array_decl)
                    trans_code += array_decl
                    
                    # Check for multiple declarations (comma separated)
                    if curr == ",":
                        trans_code += "\n" + indent_level(indent)
                        current_token_index += 1
                    elif curr == ";":
                        break
                        
                continue

            while True:
                iden = lexeme[current_token_index + 1]
                if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                    iden = f"_{iden}"
                print(f"DECLARATION OF {iden}")
                symbol_table[iden] = {
                    "type": var_type,
                    "scope": current_scope(),
                    "line": current_token_index  
                }
                print(f"curr1 {current_token_index} {lexeme[current_token_index]}")
                current_token_index += 2 
                
                if token[current_token_index] == "=":
                    current_token_index += 1
                    curr = token[current_token_index]
                        
                    while token[current_token_index] not in [",", ";"]:
                        print(f"Declaration {lexeme[current_token_index]}")
                        if curr == "&":
                            pass
                        elif curr == "str_lit":
                            if not isVar:
                                exp_parts.append(lexeme[current_token_index][:-1])
                                exp_parts.append('"')
                            else:
                                exp_parts.append(lexeme[current_token_index])
                        elif curr == "chr_lit":
                            if not isVar:
                                exp_parts.append(f"\"{lexeme[current_token_index][1:-1]}")
                                exp_parts.append('"')
                            else:
                                exp_parts.append(f"\"{lexeme[current_token_index][1:-1]}\"")
                        elif curr in ["true", "false"]:
                            exp_parts.append(lexeme[current_token_index].capitalize())
                        elif curr.startswith("id"):
                            #Translation Type Conversion
                            if var_type in ["int", "dec"] and symbol_table.get(lexeme[current_token_index], {}).get("type") in ["int", "dec"]:
                                if(var_type == "dec"):
                                    var_type = "float"
                                if getNextToken(current_token_index) == "[":
                                    temp_iden = lexeme[current_token_index]
                                    if temp_iden in dir(builtins) and temp_iden not in ["True", "False", "true", "false"]:
                                        temp_iden = f"_{temp_iden}"
                                    exp_parts.append(f"{var_type}({temp_iden}[")
                                    current_token_index += 2
                                    curr = token[current_token_index]
                                    while True:
                                        if curr.startswith("id"):
                                            temp_iden = lexeme[current_token_index]
                                            if temp_iden in dir(builtins) and temp_iden not in ["True", "False", "true", "false"]:
                                                temp_iden = f"_{temp_iden}"
                                            if symbol_table.get(temp_iden, {}).get("type") in ["int"]:
                                                exp_parts.append(f"{temp_iden}")
                                            else:
                                                console.insert(tk.END, f"Semantic Error: index should only be integer\n", "error")
                                                errorflag[0] = True
                                                return
                                        elif curr in literals:
                                            if curr == "int_lit":
                                                exp_parts.append(f"{lexeme[current_token_index]}")
                                            else:
                                                console.insert(tk.END, "Semantic Error: index should only be integer\n", "error")
                                                errorflag[0] = True
                                                return
                                        
                                        elif curr == "]":
                                            exp_parts.append(f"])")
                                            break
                                        else:
                                            exp_parts.append(f"{curr}")
                                        current_token_index += 1
                                        curr = token[current_token_index]
                                else:
                                    temp_iden = lexeme[current_token_index]
                                    if temp_iden in dir(builtins) and temp_iden not in ["True", "False", "true", "false"]:
                                        temp_iden = f"_{temp_iden}"
                                    exp_parts.append(f"{var_type}({temp_iden})")
                                if(var_type == "float"):
                                    var_type = "dec"
                            elif var_type in ["str", "chr"] and symbol_table.get(lexeme[current_token_index], {}).get("type") in ["str", "chr"]:
                                var_type = "str"
                                temp_iden = lexeme[current_token_index]
                                if temp_iden in dir(builtins) and temp_iden not in ["True", "False", "true", "false"]:
                                    temp_iden = f"_{temp_iden}"
                                exp_parts.append(f"{var_type}({temp_iden})")
                            else:
                                if token[current_token_index].startswith("id"):
                                    temp_iden = lexeme[current_token_index]
                                    if temp_iden in dir(builtins) and temp_iden not in ["True", "False", "true", "false"]:
                                        temp_iden = f"_{temp_iden}"
                                    exp_parts.append(temp_iden)
                                else:
                                    exp_parts.append(lexeme[current_token_index])
                        elif curr in ["int", "str", "chr", "bln", "dec"]:
                            isConversion = True
                            isChar = False
                            if curr == "bln":
                                con_type = "bool"
                            elif curr == "dec":
                                con_type = "float"
                            elif curr == "int":
                                con_type = "int"
                            else:
                                con_type = "str"
                            if curr == "chr":
                                isChar = True
                            conversion_store = f"eval('{con_type}("
                            current_token_index += 2
                            curr = token[current_token_index]
                            convert_value = lexeme[current_token_index]
                            if convert_value in dir(builtins) and convert_value not in ["True", "False", "true", "false"]:
                                convert_value = f"_{convert_value}"
                            if convert_value in ["true", "false"]:
                                convert_value = convert_value.capitalize()
                            elif con_type == "int":
                                if curr == "str_lit":
                                    convert_value = convert_value.strip('"')
                                elif curr == "chr_lit":
                                    convert_value = convert_value.strip("'")
                                    convert_value = f"eval(str(ord(\\\\'{convert_value}\\\\')))"
                                elif curr.startswith("id"):
                                    convert_id = lexeme[current_token_index]
                                    if convert_id in dir(builtins) and convert_id not in ["True", "False", "true", "false"]:
                                        convert_id = f"_{convert_id}"
                                    id_type = symbol_table.get(convert_id, {}).get("type", None)
                                    if id_type == "str":  
                                        convert_value = f"eval({convert_id.strip('"')})"
                                    elif id_type == "chr":
                                        convert_value = f"eval(str(ord({convert_id})))"
                            conversion_store += f"{convert_value})')"
                            if con_type == "bool" and curr.startswith("id"):
                                convert_id = lexeme[current_token_index]
                                if convert_id in dir(builtins) and convert_id not in ["True", "False", "true", "false"]:
                                    convert_id = f"_{convert_id}"
                                conversion_store = f"eval('{convert_id}.capitalize()') if str({convert_id}).lower() in ['true', 'false'] else bool({convert_id})"
                            
                            if isChar:
                                conversion_store += f"[0]"
                                isChar = False
                            #if con_type in ["str", "chr"]:
                            #    conversion_store += "+\""
                            current_token_index += 1
                            curr = token[current_token_index]
                            exp_parts.append(conversion_store)
                            print("conversion")
                        elif curr in ["&&", "||", "!"]:
                            trans_logic = {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                            exp_parts.append(trans_logic)
                        else:
                            if curr in ["int_lit", "dec_lit"]:
                                exp_parts.append(checkNumLit(current_token_index))
                            else:
                                if token[current_token_index].startswith("id"):
                                    temp_iden = lexeme[current_token_index]
                                    if temp_iden in dir(builtins) and temp_iden not in ["True", "False", "true", "false"]:
                                        temp_iden = f"_{temp_iden}"
                                    exp_parts.append(temp_iden)
                                else:
                                    exp_parts.append(lexeme[current_token_index])

                        current_token_index += 1
                        curr = token[current_token_index]
                    
                    exp = "".join(exp_parts)
                    exp_parts = []
                    #if isString:
                    #    exp += '"'
                    # type conversion based on requirements
                    if var_type == "int":
                        if exp.strip().isdigit():
                            trans_code += f"{iden} = int({exp.strip()})\n{indent_level(indent)}{iden} = int({iden})\n{indent_level(indent)}"
                        else:
                            trans_code += f"{iden} = int(eval(\"{exp.strip()}\"))\n{indent_level(indent)}{iden} = int({iden})\n{indent_level(indent)}"
                    elif var_type == "dec":
                        if exp.strip().isdigit():
                            trans_code += f"{iden} = float({exp.strip()})\n{indent_level(indent)}{iden} = int({iden})\n{indent_level(indent)}"
                        else:
                            trans_code += f"{iden} = float(eval(\"{exp.strip()}\"))\n{indent_level(indent)}{iden} = float({iden})\n{indent_level(indent)}"
                    else:
                        trans_code += f"{iden} = {exp.strip()}\n{indent_level(indent)}"
                    
                    exec_code.append(f"{iden} = {exp.strip()}")
                    print(f"dec {iden} = {exp.strip()}")

                elif token[current_token_index] in [",", ";"]:
                    curr = token[current_token_index]
                    default_values = {
                        "int": "0",
                        "dec": "0.0",
                        "str": '""',
                        "chr": "''",
                        "bln": "False",
                        "var": "None"
                    }
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
                    if var_type == "int":
                        trans_code += f"{iden} = int({default_values[var_type]})\n{indent_level(indent)}{iden} = int({iden})\n{indent_level(indent)}"
                    elif var_type == "dec":
                        trans_code += f"{iden} = float({default_values[var_type]})\n{indent_level(indent)}{iden} = float({iden})\n{indent_level(indent)}"
                    else:
                        trans_code += f"{iden} = {default_values[var_type]}\n{indent_level(indent)}"
                    
                    exec_code.append(f"{iden} = {default_values[var_type]}")
                    
                    exec_code.append(f"{iden} = {exp}")
                    print(exec_code)
                
                #if isString:
                #    exp = 'f"'
                #else: 
                #    exp = ""
                if curr == ";":
                    trans_code += "\n"+indent_level(indent)
                    break 
        #Assignment Statement
        elif curr.startswith("id"):
            print("pass id")
            print(f"next {token[current_token_index + 1]}")
            exp = ""
            output_val = ""
            var_name = lexeme[current_token_index] 
            if var_name in dir(builtins) and var_name not in ["True", "False", "true", "false"]:
                var_name = f"_{var_name}"
            global_decl = emit_global(var_name, indent)
            if global_decl:
                trans_code += global_decl
                
            if token[current_token_index+1] == "(":
                print("function call ID")
                iden_temp = lexeme[current_token_index]
                if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                    iden_temp = f"_{iden_temp}"
                trans_code += f"{iden_temp}("
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
                    elif curr in ["&&", "||", "!"]:
                        trans_logic = {"&&": " and ", "||": " or ", "!": " not "}.get(curr, "")
                        output_val += f" {trans_logic} "
                    else:
                        if curr.startswith("id") and token[current_token_index+1] in ["&", ")"]:
                            iden_temp = lexeme[current_token_index]
                            if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                                iden_temp = f"_{iden_temp}"
                            output_val += f"{iden_temp}"
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
                                    iden_temp = lexeme[current_token_index]
                                    if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                                        iden_temp = f"_{iden_temp}"
                                    exp += iden_temp

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
                iden_temp = lexeme[current_token_index]
                if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                    iden_temp = f"_{iden_temp}"
                assign = f"{iden_temp}"
                current_token_index += 1
                curr = lexeme[current_token_index]
                if token[current_token_index] == "[":
                    array_access = var_name
                    current_token_index += 1
                    
                    index_expr = ""
                    dims = 1  
                    
                    while token[current_token_index] != "]":
                        if token[current_token_index] == ",":
                            dims += 1
                            index_expr += ","  
                        elif token[current_token_index] in ["true", "false"]:
                            index_expr += lexeme[current_token_index].capitalize()
                        else:
                            if token[current_token_index].startswith("id"):
                                index_name = lexeme[current_token_index]
                                if index_name in dir(builtins) and index_name not in ["True", "False", "true", "false"]:
                                    index_name = f"_{index_name}"
                                global_decl = emit_global(index_name, indent)
                                if global_decl:
                                    trans_code += global_decl
                            index_expr += lexeme[current_token_index]
                        current_token_index += 1
                    
                    if dims == 1:
                        array_access += f"[{index_expr}]"
                    else:  
                        array_access += f"[{index_expr}]"  
                    
                    current_token_index += 1  
                    
                    # Handle assignment operator
                    if current_token_index < len(token) and token[current_token_index] in assignment_operator:
                        assign_op = lexeme[current_token_index]
                        current_token_index += 1
                        
                        # Get right-hand side expression
                        rhs = ""
                        while current_token_index < len(token) and token[current_token_index] != ";":
                            if token[current_token_index] in ["true", "false"]:
                                rhs += lexeme[current_token_index].capitalize()
                            else:
                                if token[current_token_index].startswith("id"):
                                    iden_temp = lexeme[current_token_index]
                                    if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                                        iden_temp = f"_{iden_temp}"
                                    rhs += iden_temp
                                else:
                                    rhs += lexeme[current_token_index]
                                
                            current_token_index += 1
                        
                        # Generate assignment code
                        if assign_op == "=":
                            assignment_code = f"{array_access} = {rhs}"
                        else:  # Handle +=, -=, etc.
                            op = assign_op[0]  
                            assignment_code = f"{array_access} = {array_access} {op} {rhs}"
                        
                        exec_code.append(assignment_code)
                        trans_code += assignment_code + "\n" + indent_level(indent)
                        continue
                    
                    # Handle assignment operator
                    if token[current_token_index] in assignment_operator:
                        assign_op = lexeme[current_token_index]
                        current_token_index += 1
                        
                        # Get right-hand side expression
                        rhs = ""
                        while token[current_token_index] != ";":
                            if token[current_token_index].startswith("id"):
                                iden_temp = lexeme[current_token_index]
                                if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                                    iden_temp = f"_{iden_temp}"
                                rhs += iden_temp
                            else:
                                rhs += lexeme[current_token_index]
                            current_token_index += 1
                        
                        # Generate assignment code
                        if assign_op == "=":
                            assignment_code = f"{array_access} = {rhs}"
                        else:  # Handle +=, -=, etc.
                            op = assign_op[0]  # Get the operator
                            assignment_code = f"{array_access} = {array_access} {op} {rhs}"
                        
                        exec_code.append(assignment_code)
                        trans_code += assignment_code
                    continue
                
                while curr not in assignment_operator:
                    print("pass id3")
                    assign += lexeme[current_token_index]
                    current_token_index += 1
                    curr = lexeme[current_token_index]
                exp = ""
                exp_parts = []
                assign_op = ""
                if curr in ["+=", "-=", "*=", "/=", "%=", "="]:
                    assign_op = curr
                assign += lexeme[current_token_index]
                
                current_token_index += 1
                curr = token[current_token_index]
                while curr != ";":
                    print(f"pass id4 {curr}")
                    if curr == "&":
                        exp_parts.append("+")
                    elif curr == "str_lit":
                        exp_parts.append(lexeme[current_token_index])
                    elif curr == "chr_lit":
                        exp_parts.append(lexeme[current_token_index])
                    #elif curr.startswith("id"):
                    #    exp += f"{{{lexeme[current_token_index]}}}"
                    elif curr in ["true", "false"]:
                        exp_parts.append(lexeme[current_token_index].capitalize())
                    elif curr.startswith("id"):#here
                        #Translation Type Conversion
                        print(f"-------------------------{lexeme[current_token_index]}")
                        curr_identifier = lexeme[current_token_index]
                        if curr_identifier in dir(builtins) and curr_identifier not in ["True", "False", "true", "false"]:
                            curr_identifier = f"_{curr_identifier}"
                        if getNextToken(current_token_index) == "[":
                            current_token_index+=1
                            curr = token[current_token_index]
                            arr_identifier = ""
                            while curr != "]":
                                if token[current_token_index].startswith("id"):
                                    iden = lexeme[current_token_index]
                                    if iden in dir(builtins) and iden not in ["True", "False", "true", "false"]:
                                        iden = f"_{iden}"
                                    arr_identifier += iden
                                else:
                                    arr_identifier += lexeme[current_token_index]
                                current_token_index+=1
                                curr = token[current_token_index]
                            curr_identifier += f"{arr_identifier}]"
                        var_type = symbol_table.get(curr_identifier, {}).get("type", None)
                        iden_temp = lexeme[current_token_index]
                        if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                            iden_temp = f"_{iden_temp}"
                        if var_type in ["int", "dec"] and symbol_table.get(iden_temp, {}).get("type") in ["int", "dec"]:
                            if var_type == "dec":
                                var_type = "float"
                            exp_parts.append(f"{var_type}({curr_identifier})")
                            if var_type == "float":
                                var_type = "dec"
                        elif var_type in ["str", "chr"] and symbol_table.get(iden_temp, {}).get("type") in ["str", "chr"]:
                            var_type = "str"
                            exp_parts.append(f"{var_type}({curr_identifier})")
                        else:
                            exp_parts.append(f"{curr_identifier}")
                    elif curr in ["int", "str", "chr", "bln", "dec"]:
                        isConversion = True
                        isChar = False
                        if curr == "bln":
                            con_type = "bool"
                        elif curr == "dec":
                            con_type = "float"
                        elif curr == "int":
                            con_type = "int"
                        else:
                            con_type = "str"
                        if curr == "chr":
                            isChar = True
                        conversion_store = f"eval('{con_type}("
                        current_token_index += 2
                        curr = token[current_token_index]
                        convert_value = lexeme[current_token_index]
                        if convert_value in dir(builtins) and convert_value not in ["True", "False", "true", "false"]:
                            convert_value = f"_{convert_value}"
                        if convert_value in ["true", "false"]:
                            convert_value = convert_value.capitalize()
                        elif con_type == "int":
                            if curr == "str_lit":
                                convert_value = convert_value.strip('"')
                                    #convert_value = f"eval(str(ord(\\\\'{convert_value}\\\\')))"
                                #convert_value = ', '.join(str(ord(char)) for char in convert_value)
                                #conversion_store = f"eval(("
                                #convert_value = f"eval(\'\\\',\\\'.join([str(ord(char)) for char in \"{convert_value}\"])\')"
                                #convert_value = f"eval(str(ord(char) for char in \"{convert_value}\"))"
                            elif curr == "chr_lit":
                                convert_value = convert_value.strip("'")
                                convert_value = f"eval(str(ord(\\\\'{convert_value}\\\\')))"
                            elif curr.startswith("id"):
                                convert_id = lexeme[current_token_index]
                                if convert_id in dir(builtins) and convert_id not in ["True", "False", "true", "false"]:
                                    convert_id = f"_{convert_id}"
                                if convert_id in dir(builtins) and convert_id not in ["True", "False", "true", "false"]:
                                    convert_id = f"_{convert_id}"
                                id_type = symbol_table.get(convert_id, {}).get("type", None)
                                if id_type == "str":
                                    convert_value = f"eval({convert_id.strip('"')})"
                                elif id_type == "chr":
                                    convert_value = f"eval(str(ord({convert_id})))"
                        conversion_store += f"{convert_value})')"
                        if con_type == "bool" and curr.startswith("id"):
                                convert_id = lexeme[current_token_index]
                                if convert_id in dir(builtins) and convert_id not in ["True", "False", "true", "false"]:
                                    convert_id = f"_{convert_id}"
                                conversion_store = f"eval('{convert_id}.capitalize()') if str({convert_id}).lower() in ['true', 'false'] else bool({convert_id})"
                        
                        if isChar:
                            conversion_store += f"[0]"
                            isChar = False
                        #if con_type in ["str", "chr"]:
                        #    conversion_store += "+\""
                        current_token_index += 1
                        curr = token[current_token_index]
                        exp_parts.append(conversion_store)
                        print("conversion")
                    else:
                        if curr in ["int_lit", "dec_lit"]:
                            if curr == "dec_lit":
                                isDec = True
                            exp_parts.append(checkNumLit(current_token_index))
                        elif curr in arithmetic_operator:
                            exp_parts.append(lexeme[current_token_index])
                            print(f"==========={exp_parts}")
                        elif getPrevToken(current_token_index) in ["str_lit", "chr_lit"] or getPrevToken(current_token_index).startswith('id'):
                            prevToken = getPrevToken(current_token_index)
                            if prevToken.startswith('id'):
                                prev_type = symbol_table.get(var_name, {}).get("type", None)
                                if prev_type in ["str", "chr"]:
                                    exp_parts.append("")
                                else:
                                    exp_parts.append(lexeme[current_token_index])
                            elif prevToken in ["str_lit", "chr_lit"]:
                                exp_parts.append(" ")
                        else:
                            exp_parts.append(lexeme[current_token_index])
                            print(f"==========={exp_parts}")

                    current_token_index += 1
                    curr = token[current_token_index]
                exp = "".join(exp_parts)
                exp_parts = []
                #exp = f"f'{exp}'" 
                # Get variable type from symbol table
                var_type = symbol_table.get(var_name, {}).get("type", None)
                # Generate the assignment with type enforcement if type is known
                if var_type == "int":
                    trans_code += f"{var_name} {assign_op} int(eval(\"{exp.strip()}\"))\n{indent_level(indent)}{var_name} = int({var_name})\n{indent_level(indent)}"
                elif var_type == "dec":
                    trans_code += f"{var_name} {assign_op} float(eval(\"{exp.strip()}\"))\n{indent_level(indent)}{var_name} = float({var_name})\n{indent_level(indent)}"
                else:
                    trans_code += f"{var_name} {assign_op} {exp.strip()}\n{indent_level(indent)}"
                
                exec_code.append(f"{assign}{exp.strip()}")
                print(f"assign {assign}{exp.strip()}")
                #if assign not in exec_code
                #exec_code.append(f"{assign}{exp.strip()}")
                #trans_code += f"{assign}{exp.strip()}" + "\n" + indent_level(indent)
                #print(f"assign {assign}{exp.strip()}")
        #Output Statement
        elif curr == "disp":
            exp = ""
            output_val = 'console_disp(f"'
            current_token_index += 2
            curr = token[current_token_index]

            while curr != ")":
                if curr == "&":
                    exp = ""
                    pass
                elif curr == "str_lit":
                    output_val += lexeme[current_token_index].strip('"')
                elif curr in ["true", "false"]:
                    output_val += lexeme[current_token_index].capitalize()
                else:
                    if curr.startswith("id") and token[current_token_index+1] in ["&", ")"]:
                        iden_temp = lexeme[current_token_index]
                        if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                            iden_temp = f"_{iden_temp}"
                        output_val += f"{{{iden_temp}}}"
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
                                if token[current_token_index].startswith("id"):
                                    iden_temp = lexeme[current_token_index]
                                    if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                                        iden_temp = f"_{iden_temp}"
                                    exp += iden_temp
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
            output_val += '")'
            exec_code.append(output_val)
            trans_code += output_val
        #Input Statement
        elif curr == "insp":
            current_token_index += 2
            curr = token[current_token_index]
            variable_insp = ""
            while curr != ";":
                if curr == ")" and getNextToken(current_token_index) == ";":
                    pass
                else:
                    iden_temp = lexeme[current_token_index]
                    if iden_temp in dir(builtins) and iden_temp not in ["True", "False", "true", "false"]:
                        iden_temp = f"_{iden_temp}"
                    variable_insp += f"{iden_temp}"
                current_token_index += 1
                curr = token[current_token_index]
            global var_nameList
            var_nameList.append(variable_insp)
            trans_code += f"{variable_insp} = console_insp('{variable_insp}')\n" + indent_level(indent)
         
        #Other Statement
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
            if isSwitchStatement:
                console.insert(tk.END, "Illegal Break: Break not allowed inside switch statement\n", "error")
                errorflag[0] = True  
                return
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
    trans_code += "\n__main__()"
    print(f"run")
    print("\n=== Symbol Table with Scope ===")
    for var, info in symbol_table.items():
        print(f"{var}: type={info['type']}, scope={info['scope']}, line={info['line']}")
    print("===============================")
    
    try:
        def handle_input(prompt=""):
            console.insert(tk.END, prompt)
            console.mark_set("input_start", tk.END)
            console.see(tk.END)
            console.focus_set()

            input_var = tk.StringVar()
            input_done = threading.Event()

            input_entry = tk.Entry(console, bg="#202020", fg="white", insertbackground="white", relief="flat", font=("Consolas", 12), textvariable=input_var)
            console.window_create("input_start", window=input_entry)
            input_entry.focus_set()

            def block_mouse(event):
                return "break"

            console.bind("<Button-1>", block_mouse)

            def on_enter(event):
                input_done.set()
                return "break"

            input_entry.bind("<Return>", on_enter)
            input_done.wait()

            user_input = input_var.get()
            user_input = user_input.replace("~", "-")
            processed_input = user_input.strip()

            input_entry.destroy()
            console.unbind("<Button-1>")

            user_input = user_input.replace("-", "~")
            console.insert(tk.END, user_input + "\n")
            return processed_input
            
        def console_disp(val):
            #val = str(val).lstrip()
            def replace_negative(match):
                number = match.group(0)
                return "~" + number[1:] 

            val = re.sub(r'(?<!\d)-\d+(\.\d+)?', replace_negative, val)


            console.insert(tk.END, val)
            console.see(tk.END)
        def console_insp(variable_insp):
            val = handle_input()
            val = val.replace("~", "-")
            dataType = symbol_table.get(variable_insp, {}).get("type", None)
            if dataType == "str":
                val = str(val)
                
            elif dataType == "int":
                if not (val.isdigit() or (val.startswith('-') and val[1:].isdigit())):
                    raise ValueError(f"Illegal Input. Expected an integer number for identifier '{val}'")
                else:
                    val = int(val)
                
            elif dataType == "dec":
                try:
                    val = float(val)
                except ValueError:
                    raise ValueError("Illegal Input. Expected a decimal number for identifier '{val}'")
                    return None
                
            elif dataType == "chr":
                if len(val) != 1:
                    raise ValueError("Illegal Input. Expected a single character for identifier '{val}'")
                    return None
                
            elif dataType == "bln":
                if val.lower() in ["true", "1"]:
                    val = True
                elif val.lower() in ["false", "0"]:
                    val = False
                else:
                    raise ValueError("Illegal Input. Expected a boolean value (True/False) for identifier '{val}'")
                    return None
            #console.insert(tk.END, f"DEBUG {dataType}/{variable_insp}/{symbol_table}")
            #console.insert(tk.END, f"[DEBUG INSP] returning: {repr(val)}\n")
            return val

        exec_env = {
            'console_disp': console_disp,
            'console_insp': console_insp,
            'handle_input': handle_input,
            'tk': tk,
            'console': console,
            'eval': eval,
        }
        try:
            exec(trans_code, exec_env, exec_env)
        except ValueError as ve:
            error_message = str(ve)
            if "could not convert string to float" in error_message:
                console.insert(tk.END, "\nError: cannot convert string to decimal because it contains non-digit characters\n", "error")
            elif "Illegal Input" in error_message:
                console.insert(tk.END, "\nExecution Error: ", "error")
                console.insert(tk.END, error_message)
            elif "Illegal Break" in error_message:
                console.insert(tk.END, "\nExecution Error: ", "error")
                console.insert(tk.END, error_message)
            else:
                console.insert(tk.END, f"\n{str(ve)}\n", "error")
        except Exception as e:
            error_message = str(e)
            if "invalid decimal literal" in error_message:
                console.insert(tk.END, "\nError: cannot convert string to integer because it contains non-digit characters\n", "error")
            elif "division by zero" in error_message:
                console.insert(tk.END, "\nMath Error: ", "error")
                console.insert(tk.END, f"Division by zero is not allowed")
            else:
                console.insert(tk.END, f"\nExecution failed: {str(e)}\n", "error")
    finally:
        pass

    # Show generated code
    #console.insert(tk.END, "\n=== Generated Code ===\n")
    #console.insert(tk.END, trans_code)
    #console.insert(tk.END, "\n=== End of Code ===\n")
