from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def semantic(console):  
    if errorflag[0] == True:  
        return
    print(f"token: {token}")
    print(f"lexeme: {lexeme}")
    current_token_index = 0
    prevlookahead = ""
    semantic_checker = Semantic(console)
    
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
    expressionstack = []
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
        if errorflag[0] == True:
            console.insert(tk.END, "Parsing interrupted...", "error")
            return
        if len(token) > current_token_index:
            lookahead = get_lookahead()
        #else:
            #error_message("End of file")
        top = stack.pop()
        lookahead = get_lookahead()
        if lookahead is None:
            error_message("Unexpected End-of-File. ")
            return
        
        
        if top == lookahead:
            # Terminal matches lookahead, consume the token
            print(f"Match: {lookahead}")
            prevlookahead = lookahead
            #-----Semantic-----
            semantic_checker.semantic_process(lookahead, current_token_index)
            current_token_index += 1
                
        elif top in parsing_table:
            # Non-terminal: use the parsing table
            rule = parsing_table[top].get(lookahead)
            #Semantic
            if top in non_terminal_check:
                semantic_checker.semantic_nonterminal(top)
            #End
            if rule:
                #print(f"Apply rule: {top} -> {' '.join(rule)}")
                if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                    stack.extend(reversed(rule))
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
        console.insert(tk.END,"Input accepted: ", "accepted")
        console.insert(tk.END,"Semantically correct.")
        semantic_checker.printSymbolTable()
        
class Semantic:
    def __init__(self, console):
        #Main variable
        self.symbol_table = []
        self.parameterList = []
        
        self.parentStack = ["global"]
        self.parent = "global"         # Current parent scope
        self.level_value = 0    
               
        self.console = console
        self.current_token_index = 0
        self.lookahead = ""
        
        #Identifier
        self.rhs_identifier = ""
        
        #Variable for symbol table
        self.type_value = ""
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.scope_value = "global"
        self.dimension_value = ""
        self.parent = "global"
        self.level_value = 0

    def error_message(self, error):
        line = rows[self.current_token_index] if self.current_token_index < len(rows) else "0"
        column = col[self.current_token_index] if self.current_token_index < len(col) else "0"
        self.console.insert(tk.END, "Semantic Error: ", "error")
        self.console.insert(tk.END, f"{error}")
        self.console.insert(tk.END, f"\n           line {line}, col {column}\n", "ln_col")
        errorflag[0] = True
        return
    
    def semantic_process(self, lookahead, current_token_index):
        print(f"{self.current_token_index}/{current_token_index}")
        if self.current_token_index != current_token_index:
            return
        self.lookahead = lookahead
        print(f"lookahead: {lookahead}")
        #Scope handling
        if lookahead == "{" and self.top != "<identifier_declaration>":
            self.level_value +=1
        elif lookahead in codeblocks:
            temp = self.parent
            self.parent = temp + str(self.level_value)
            temp2 = self.parent
            self.parentStack.append(self.parent)
            self.identifier_value = temp2
            self.parent = temp
            self.add_symbol_table()
            temp_top = ""
            if self.top == "<foreach_statement>":
                temp_top = self.top
            self.clear_all()
            self.top = temp_top
            self.parent = temp2
        elif lookahead == "}" and self.top != "<identifier_declaration>":
            self.parentStack.pop()
            if self.parentStack:
                self.parent = self.parentStack[-1]
        #Statement
        if lookahead == "const":
            self.type_value = "const"
        elif lookahead == "main":
            self.handle_main()
            
        elif lookahead == "segm":
            self.handle_segment_declaration()
        elif lookahead == "ret":
            pass
        elif lookahead in semantic_datatype:
            self.handle_identifier_declaration()
        elif lookahead.startswith("id"):
            self.handle_identifier_initialization()
        elif lookahead == "foreach":
            self.handle_foreach_statement()
        elif lookahead == "for":
            self.handle_for_statement()
        elif lookahead == "insp":
            self.current_token_index +=2
            identifier = lexeme[self.current_token_index]
            self.checkIfIDNotDeclared(identifier)
        elif lookahead == "disp":
            self.checkDisp()
        elif lookahead in ["if", "elif", "while"]:
            self.handle_condition_statement()
        elif lookahead == "switch":
            self.current_token_index +=2
            lookahead = token[self.current_token_index]
            self.checkIfIDNotDeclared(lexeme[self.current_token_index])
        #Literal checker
        if lookahead in arithmetic_operator:
            self.checkOperand()
        elif lexeme[self.current_token_index] == "~0":
            self.error_message("Invalid negative value")
            return
        elif lookahead in {"++", "--"}:
            self.checkPreUnary()
        elif lookahead.startswith("id") and self.getState("prev", "token", self.current_token_index-1) in ["++", "--"]:
            self.checkPostUnary()
        self.current_token_index +=1
    def handle_main(self):
        self.scope_value = self.lookahead
        self.parent = "global"
        self.identifier_value = "main"
        self.type_value = "segm"
        self.parentStack.pop()
        self.parentStack.append("main")
        self.add_symbol_table()
        self.parent = "main"
        self.isMainDeclared = True
        self.clear_all()

    def handle_segment_declaration(self):
        self.current_token_index += 1
        self.identifier_value = lexeme[self.current_token_index]
        segment_id = self.identifier_value
        self.type_value = "segm"
        self.add_symbol_table()
        self.parentStack.append(self.identifier_value)
        self.parent = self.identifier_value 
        self.clear_all()
        datatype_value = ""
        parameter_id = ""
        lookahead = token[self.current_token_index]
        while True:
            if errorflag[0] == True:  
                return
            if lookahead == "{":
                return
            elif lookahead in semantic_datatype:
                datatype_value = lookahead
            elif lookahead.startswith("id"):
                parameter_id = lexeme[self.current_token_index]
            elif lookahead == ",":
                self.update_param_symbol(segment_id, datatype_value, parameter_id)
                self.identifier_value = parameter_id
                self.datatype_value = datatype_value
                self.type_value = ""
                self.add_symbol_table()
                
            elif lookahead == ")":
                print(parameter_id)
                self.update_param_symbol(segment_id, datatype_value, parameter_id)
                self.identifier_value = parameter_id
                self.datatype_value = datatype_value
                self.type_value = ""
                self.add_symbol_table()
                self.clear_all()

            self.current_token_index += 1
            lookahead = token[self.current_token_index]
    
    def handle_identifier_declaration(self):
        lookahead = token[self.current_token_index]
        self.datatype_value = lookahead
        #Array
        if self.getState("next", "token", self.current_token_index+1) == "[":
            print("Array declaration")
            self.current_token_index += 1
            if self.getState("next", "token", self.current_token_index+1) == ",":
                self.dimension_value = 2
                self.current_token_index +=2
            else:
                self.dimension_value = 1
                self.type_value = "array"
                self.current_token_index +=1
            lookahead = token[self.current_token_index]
            param = 0
            while True:
                print(f"lookahead! {lookahead}/{self.current_token_index}")
                if errorflag[0] == True: 
                    return
                if lookahead == ";":
                    self.add_symbol_table()
                    self.clear_all()
                    return
                elif self.identifier_value == "" and lookahead.startswith( "id"):
                    self.identifier_value = lexeme[self.current_token_index]
                    self.checkIfIDAlreadyDeclared(self.identifier_value)
                elif lookahead == "{":
                    param += 1
                elif lookahead == "}":
                    param -= 1
                elif lookahead == "," and param == 0:
                    self.add_symbol_table()
                    self.identifier_value = ""
                elif lookahead in literals:
                    if self.datatype_value == "var":
                        new_datatype = self.getDatatypeOnLiterals(lookahead)
                        self.updateDatatype(self.identifier_value, new_datatype)
                    self.checkIfAssignmentIsValid(lookahead)
                elif lookahead in assignment_number:
                    if self.datatype_value not in ["int", "dec"]:
                        self.error_message(f"Compound Assignment is only allowed for number identifier")
                        return
                elif lookahead in arithmetic_operator:
                    self.checkOperand()
                self.current_token_index +=1
                lookahead = token[self.current_token_index]
        else:
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
            new_datatype = ""
            prev_datatype = self.datatype_value
            while True:
                print(f"Declaration ID: {lookahead}")
                if errorflag[0] == True:
                    return
                if lookahead == ";":
                    if new_datatype != "":
                        self.datatype_value = new_datatype
                    self.add_symbol_table()
                    self.clear_all()
                    return
                elif self.identifier_value == "" and lookahead.startswith("id"):
                    self.identifier_value = lexeme[self.current_token_index]
                    self.checkIfIDAlreadyDeclared(self.identifier_value)
                    if self.datatype_value == "bln":
                        self.checkBooleanDeclaration()
                        return
                    elif self.datatype_value == "str":
                        self.checkStringDeclaration()
                        return
                elif lookahead.startswith("id"):
                    self.checkIDType(lexeme[self.current_token_index])
                    #Function call
                    if self.getState("next", "token", self.current_token_index+1) == "(":
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        paren = 1
                        args_type = []
                        
                        while True:
                            print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                            if errorflag[0] == True:
                                return
                            if paren == 0:
                                self.check_function_arguments(identifier, args_type)
                                self.current_token_index -= 1
                                lookahead = token[self.current_token_index]
                                break
                            elif lookahead == "(":
                                paren += 1
                            elif lookahead == ")":
                                paren -= 1
                            elif lookahead in semantic_datatype:
                                args_type.append(lookahead)
                                self.current_token_index+=3
                                lookahead = token[self.current_token_index]
                            elif lookahead.startswith("id"):
                                self.checkIDType(lexeme[self.current_token_index])
                                args_id = lexeme[self.current_token_index]
                                datatype_arguments = self.getDatatype(args_id)
                                args_type.append(datatype_arguments)
                            elif lookahead in literals:
                                datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                args_type.append(datatype_arguments)
                            self.current_token_index += 1
                            lookahead = token[self.current_token_index]
                    else:
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        if self.datatype_value == "var":
                            new_datatype = self.getDatatype(identifier)
                        else:
                            self.checkIfAssignmentIDIsValid(identifier)
                elif lookahead in semantic_datatype:
                    type_conversion_type = lookahead
                    if type_conversion_type != self.datatype_value:
                        self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                        return
                    self.current_token_index += 2
                    lookahead = token[self.current_token_index]
                    if lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkTypeConversion(type_conversion_type, identifier, "id")
                    elif lookahead in literals:
                        self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                    if self.datatype_value == "var":
                        self.updateDatatype(self.identifier_value, type_conversion_type)
                elif lookahead in literals:
                    if self.datatype_value == "var":
                        new_datatype = self.getDatatypeOnLiterals(lookahead)
                    else:
                        self.checkIfAssignmentIsValid(lookahead)
                elif lookahead == ",":
                    if new_datatype != "":
                        self.datatype_value = new_datatype
                        self.add_symbol_table()
                        self.identifier_value = ""
                        new_datatype = ""
                        self.datatype_value = prev_datatype
                    else:
                        self.add_symbol_table()
                        self.identifier_value = ""
                elif lookahead in assignment_number:
                    if self.datatype_value not in ["int", "dec"]:
                        self.error_message(f"Compound Assignment is only allowed for number identifier")
                        return
                elif lookahead in arithmetic_operator:
                    self.checkOperand()
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
    
    def handle_identifier_initialization(self):
        rhs_identifier = lexeme[self.current_token_index]
        self.checkIfIDNotDeclared(rhs_identifier)
        identifier_type = self.getType(rhs_identifier)
        lookahead = token[self.current_token_index]
        #Function Call
        if self.getState("next", "token", self.current_token_index+1) == "(":
            identifier = lexeme[self.current_token_index]
            self.checkIfIDNotDeclared(identifier)
            self.current_token_index += 2
            lookahead = token[self.current_token_index]
            paren = 1
            args_type = []
            
            while True:
                print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                if errorflag[0] == True:
                    return
                if paren == 0:
                    self.check_function_arguments(identifier, args_type)
                    return
                elif lookahead == "(":
                    paren += 1
                elif lookahead == ")":
                    paren -= 1
                elif lookahead in semantic_datatype:
                    args_type.append(lookahead)
                    self.current_token_index+=3
                    lookahead = token[self.current_token_index]
                elif lookahead.startswith("id"):
                    self.checkIDType(lexeme[self.current_token_index])
                    args_id = lexeme[self.current_token_index]
                    datatype_arguments = self.getDatatype(args_id)
                    args_type.append(datatype_arguments)
                elif lookahead in literals:
                    datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                    args_type.append(datatype_arguments)
                elif lookahead in arithmetic_operator:
                    self.checkOperand()
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
        elif self.getState("next", "token", self.current_token_index+1) == "[":
            self.datatype_value = self.getDatatype(rhs_identifier)
            dimension = self.getDimension(rhs_identifier)
            dimension_found = 1
            print(f"DATATYPE {semantic_datatype}")
            while True:
                print(f"=lookahead {lookahead}")
                if errorflag[0] == True:
                    return
                if lookahead == ";":
                    self.clear_all()
                    return
                elif lookahead == "[":
                    #Index checker
                    while True:
                        print(f"== {lookahead}")
                        if errorflag[0] == True:
                            return
                        if lookahead == "]":
                            if dimension_found != dimension:
                                self.error_message(f"Array dimension mismatch. Expected {dimension}D but found {dimension_found}D")
                                return
                            break
                        elif lookahead == ",":
                            dimension_found = 2
                        elif lookahead in literals:
                            if lookahead != "int_lit":
                                self.error_message(f"Array index must only be integer.")
                                return
                        elif lookahead.startswith("id"):
                            self.checkIDType(lexeme[self.current_token_index])
                            index_id = lexeme[self.current_token_index]
                            datatype = self.getDatatype(index_id)
                            if datatype != "int":
                                self.error_message(f"Array index must only be integer.")
                                return
                        elif lookahead in arithmetic_operator:
                            self.checkOperand()
                        self.current_token_index +=1
                        lookahead = token[self.current_token_index]
                elif lookahead in assignment_number:
                    if self.datatype_value not in ["dec", "int"]:
                        self.error_message(f"Compound Assignment is only allowed for number identifier")
                        return
                    elif lookahead == "=" and identifier_type == "const":
                        self.error_message(f"Constant variable '{rhs_identifier}' can only be initialized once.")
                        return
                elif lookahead.startswith("id"):
                    #Function call
                    if self.getState("next", "token", self.current_token_index+1) == "(":
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        paren = 1
                        args_type = []
                        
                        while True:
                            print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                            if errorflag[0] == True:
                                return
                            if paren == 0:
                                self.check_function_arguments(identifier, args_type)
                                return
                            elif lookahead == "(":
                                paren += 1
                            elif lookahead == ")":
                                paren -= 1
                            elif lookahead in semantic_datatype:
                                args_type.append(lookahead)
                                self.current_token_index+=3
                                lookahead = token[self.current_token_index]
                            elif lookahead.startswith("id"):
                                self.checkIDType(lexeme[self.current_token_index])
                                args_id = lexeme[self.current_token_index]
                                datatype_arguments = self.getDatatype(args_id)
                                args_type.append(datatype_arguments)
                            elif lookahead in literals:
                                datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                args_type.append(datatype_arguments)
                            self.current_token_index += 1
                            lookahead = token[self.current_token_index]
                    else:
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkIfAssignmentIDIsValid(identifier)
                elif lookahead in semantic_datatype:
                    type_conversion_type = lookahead
                    if type_conversion_type != self.datatype_value:
                        self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                        return
                    self.current_token_index += 2
                    lookahead = token[self.current_token_index]
                    if lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkTypeConversion(type_conversion_type, identifier, "id")
                    elif lookahead in literals:
                        self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                    if self.datatype_value == "var":
                        self.updateDatatype(rhs_identifier, type_conversion_type)
                elif lookahead in literals:
                    self.checkIfAssignmentIsValid(lookahead)
                    if self.datatype_value == "var":
                        new_datatype = self.getDatatypeOnLiterals(lookahead)
                        self.updateDatatype(rhs_identifier, new_datatype)
                elif lookahead in arithmetic_operator:
                    self.checkOperand()
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
        else:
            identifier_temp = ""
            while True:
                if errorflag[0] == True:
                    return
                if lookahead == ";":
                    self.clear_all()
                    return
                elif lookahead in assignment_number:
                    if self.datatype_value not in ["dec", "int"]:
                        self.error_message(f"Compound Assignment is only allowed for number identifier")
                        return
                elif identifier_temp == "" and lookahead.startswith("id"):
                    identifier_temp = lexeme[self.current_token_index]
                    self.datatype_value = self.getDatatype(identifier_temp)
                    if self.datatype_value == "bln":
                        self.checkBooleanAssignment()
                        lookahead = token[self.current_token_index]
                        identifier_temp = ""
                        if lookahead == ";":
                            self.clear_all()
                            return
                    elif self.datatype_value == "str":
                        self.checkStringAssignment()
                        lookahead = token[self.current_token_index]
                        identifier_temp = ""
                        if lookahead == ";":
                            self.clear_all()
                            return
                elif self.getType(identifier_temp) == "const":
                    self.error_message(f"A constant identifier can only be declared in a declaration statement")
                    return
                elif lookahead.startswith("id"):
                    self.checkIDType(lexeme[self.current_token_index])
                    if self.getState("next", "token", self.current_token_index+1) == "(":
                        #Function call
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        paren = 1
                        args_type = []
                        
                        while True:
                            print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                            if errorflag[0] == True:
                                return
                            if paren == 0:
                                self.check_function_arguments(identifier, args_type)
                                return
                            elif lookahead == "(":
                                paren += 1
                            elif lookahead == ")":
                                paren -= 1
                            elif lookahead in semantic_datatype:
                                args_type.append(lookahead)
                                self.current_token_index+=3
                                lookahead = token[self.current_token_index]
                            elif lookahead.startswith("id"):
                                args_id = lexeme[self.current_token_index]
                                datatype_arguments = self.getDatatype(args_id)
                                args_type.append(datatype_arguments)
                            elif lookahead in literals:
                                datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                args_type.append(datatype_arguments)
                            self.current_token_index += 1
                            lookahead = token[self.current_token_index]
                    else:
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkIfAssignmentIDIsValid(identifier)
                elif lookahead in semantic_datatype:
                    type_conversion_type = lookahead
                    if type_conversion_type != self.datatype_value:
                        self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                        return
                    self.current_token_index += 2
                    lookahead = token[self.current_token_index]
                    if lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkTypeConversion(type_conversion_type, identifier, "id")
                    elif lookahead in literals:
                        self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                elif lookahead in literals:
                    self.checkIfAssignmentIsValid(lookahead)
                elif lookahead == ",":
                    self.clear_all()
                elif lookahead in arithmetic_operator:
                    self.checkOperand()  
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
    
    def handle_foreach_statement(self):
        self.current_token_index += 2
        lookahead = token[self.current_token_index]
        if lookahead in semantic_datatype:
            self.datatype_value = lookahead
            self.current_token_index += 1
            identifier = lexeme[self.current_token_index]
            self.identifier_value = identifier
            self.checkIfIDAlreadyDeclared(identifier)
            self.add_symbol_table()
            self.clear_all()
        elif lookahead.startswith("id"):
            self.checkIDType(lexeme[self.current_token_index])
            identifier = lexeme[self.current_token_index]
            self.checkIfIDNotDeclared(identifier)
        self.current_token_index += 2 #skip in
        identifier = lexeme[self.current_token_index]
        identifier_type = self.getType(identifier)
        identifier_datatype = self.getDatatype(identifier)
        if identifier_type != "array":
            if identifier_datatype != "str":
                self.error_message(f"Identifier {identifier} is not iterable. ")
                return
        

    def handle_for_statement(self):
        print("For statement")
        self.current_token_index += 2 #skip for(
        lookahead = token[self.current_token_index]
        if lookahead in semantic_datatype:
            self.datatype_value = lookahead
            self.current_token_index += 1
            identifier = lexeme[self.current_token_index]
            self.identifier_value = identifier
            self.checkIfIDAlreadyDeclared(identifier)
            if self.getState("next", "token", self.current_token_index+1) == "[":
                self.error_message(f"For declaration only allows scalar variable. Array is not allowed")
                return
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
            while True:
                print(f"FOR INITIALIZATION: {lookahead}")
                if errorflag[0] == True:
                    return
                if lookahead == ";":
                    self.add_symbol_table()
                    self.clear_all()
                    break
                elif lookahead.startswith("id"):
                    self.checkIDType(lexeme[self.current_token_index])
                    #Function call
                    if self.getState("next", "token", self.current_token_index+1) == "(":
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        paren = 1
                        args_type = []
                        
                        while True:
                            print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                            if errorflag[0] == True:
                                return
                            if paren == 0:
                                self.check_function_arguments(identifier, args_type)
                                return
                            elif lookahead == "(":
                                paren += 1
                            elif lookahead == ")":
                                paren -= 1
                            elif lookahead in semantic_datatype:
                                args_type.append(lookahead)
                                self.current_token_index+=3
                                lookahead = token[self.current_token_index]
                            elif lookahead.startswith("id"):
                                self.checkIDType(lexeme[self.current_token_index])
                                args_id = lexeme[self.current_token_index]
                                datatype_arguments = self.getDatatype(args_id)
                                args_type.append(datatype_arguments)
                            elif lookahead in literals:
                                datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                args_type.append(datatype_arguments)
                            self.current_token_index += 1
                            lookahead = token[self.current_token_index]
                    else:
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkIfAssignmentIDIsValid(identifier)
                elif lookahead in semantic_datatype:
                    type_conversion_type = lookahead
                    if type_conversion_type != self.datatype_value:
                        self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                        return
                    self.current_token_index += 2
                    lookahead = token[self.current_token_index]
                    if lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkTypeConversion(type_conversion_type, identifier, "id")
                    elif lookahead in literals:
                        self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                elif lookahead in literals:
                    self.checkIfAssignmentIsValid(lookahead)
                elif lookahead in assignment_number:
                    if self.datatype_value not in ["int", "dec"]:
                        self.error_message(f"Compound Assignment is only allowed for number identifier")
                        return
                elif lookahead in arithmetic_operator:
                    self.checkOperand()
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
        elif lookahead.startswith("id"):
            rhs_identifier = lexeme[self.current_token_index]
            self.checkIfIDNotDeclared(rhs_identifier)
            identifier_type = self.getType(rhs_identifier)
            lookahead = token[self.current_token_index]
            self.checkIDType(lexeme[self.current_token_index])
            #Function Call
            if self.getState("next", "token", self.current_token_index+1) == "[":
                self.datatype_value = self.getDatatype(rhs_identifier)
                dimension = self.getDimension(rhs_identifier)
                dimension_found = 1
                print(f"DATATYPE {semantic_datatype}")
                while True:
                    print(f"=lookahead {lookahead}")
                    if errorflag[0] == True:
                        return
                    if lookahead == ";":
                        self.clear_all()
                        break
                    elif lookahead == "[":
                        #Index checker
                        while True:
                            print(f"== {lookahead}")
                            if errorflag[0] == True:
                                return
                            if lookahead == "]":
                                if dimension_found != dimension:
                                    self.error_message(f"Array dimension mismatch. Expected {dimension}D but found {dimension_found}D")
                                    return
                                break
                            elif lookahead == ",":
                                dimension_found = 2
                            elif lookahead in literals:
                                if lookahead != "int_lit":
                                    self.error_message(f"Array index must only be integer.")
                                    return
                            elif lookahead.startswith("id"):
                                self.checkIDType(lexeme[self.current_token_index])
                                index_id = lexeme[self.current_token_index]
                                datatype = self.getDatatype(index_id)
                                if datatype != "int":
                                    self.error_message(f"Array index must only be integer.")
                                    return
                            self.current_token_index +=1
                            lookahead = token[self.current_token_index]
                    elif lookahead in assignment_number:
                        if self.datatype_value not in ["dec", "int"]:
                            self.error_message(f"Compound Assignment is only allowed for number identifier")
                            return
                        elif lookahead == "=" and identifier_type == "const":
                            self.error_message(f"Constant variable '{rhs_identifier}' can only be initialized once.")
                            return
                    elif lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        #Function call
                        if self.getState("next", "token", self.current_token_index+1) == "(":
                            identifier = lexeme[self.current_token_index]
                            self.checkIfIDNotDeclared(identifier)
                            self.current_token_index += 2
                            lookahead = token[self.current_token_index]
                            paren = 1
                            args_type = []
                            
                            while True:
                                print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                                if errorflag[0] == True:
                                    return
                                if paren == 0:
                                    self.check_function_arguments(identifier, args_type)
                                    break
                                elif lookahead == "(":
                                    paren += 1
                                elif lookahead == ")":
                                    paren -= 1
                                elif lookahead in semantic_datatype:
                                    args_type.append(lookahead)
                                    self.current_token_index+=3
                                    lookahead = token[self.current_token_index]
                                elif lookahead.startswith("id"):
                                    self.checkIDType(lexeme[self.current_token_index])
                                    args_id = lexeme[self.current_token_index]
                                    datatype_arguments = self.getDatatype(args_id)
                                    args_type.append(datatype_arguments)
                                elif lookahead in literals:
                                    datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                    args_type.append(datatype_arguments)
                                self.current_token_index += 1
                                lookahead = token[self.current_token_index]
                        else:
                            identifier = lexeme[self.current_token_index]
                            self.checkIfIDNotDeclared(identifier)
                            self.checkIfAssignmentIDIsValid(identifier)
                    elif lookahead in semantic_datatype:
                        type_conversion_type = lookahead
                        if type_conversion_type != self.datatype_value:
                            self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                            return
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        if lookahead.startswith("id"):
                            self.checkIDType(lexeme[self.current_token_index])
                            identifier = lexeme[self.current_token_index]
                            self.checkIfIDNotDeclared(identifier)
                            self.checkTypeConversion(type_conversion_type, identifier, "id")
                        elif lookahead in literals:
                            self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                    elif lookahead in literals:
                        self.checkIfAssignmentIsValid(lookahead)
                    self.current_token_index += 1
                    lookahead = token[self.current_token_index]
            else:
                self.datatype_value = self.getDatatype(rhs_identifier)
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
                if lookahead in assignment_number:
                    if self.datatype_value not in ["dec", "int"]:
                        self.error_message(f"Compound Assignment is only allowed for number identifier")
                        return
                    elif lookahead == "=" and identifier_type == "const":
                        self.error_message(f"Constant variable '{rhs_identifier}' can only be initialized once.")
                        return
                elif lookahead.startswith("id"):
                    self.checkIDType(lexeme[self.current_token_index])
                    #Function call
                    if self.getState("next", "token", self.current_token_index+1) == "(":
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        paren = 1
                        args_type = []
                        
                        while True:
                            print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                            if errorflag[0] == True:
                                return
                            if paren == 0:
                                self.check_function_arguments(identifier, args_type)
                                break
                            elif lookahead == "(":
                                paren += 1
                            elif lookahead == ")":
                                paren -= 1
                            elif lookahead in semantic_datatype:
                                args_type.append(lookahead)
                                self.current_token_index+=3
                                lookahead = token[self.current_token_index]
                            elif lookahead.startswith("id"):
                                self.checkIDType(lexeme[self.current_token_index])
                                args_id = lexeme[self.current_token_index]
                                datatype_arguments = self.getDatatype(args_id)
                                args_type.append(datatype_arguments)
                            elif lookahead in literals:
                                datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                args_type.append(datatype_arguments)
                            self.current_token_index += 1
                            lookahead = token[self.current_token_index]
                    else:
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkIfAssignmentIDIsValid(identifier)
                elif lookahead in semantic_datatype:
                    type_conversion_type = lookahead
                    if type_conversion_type != self.datatype_value:
                        self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                        return
                    self.current_token_index += 2
                    lookahead = token[self.current_token_index]
                    if lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        identifier = lexeme[self.current_token_index]
                        self.checkIfIDNotDeclared(identifier)
                        self.checkTypeConversion(type_conversion_type, identifier, "id")
                    elif lookahead in literals:
                        self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                elif lookahead in literals:
                    self.checkIfAssignmentIsValid(lookahead)
                elif lookahead == ",":
                    self.clear_all()
                    rhs_identifier = lexeme[self.current_token_index+1]
                    self.datatype_value = self.getDatatype(rhs_identifier)
                self.current_token_index += 1
                lookahead = token[self.current_token_index]
                while True:
                    if errorflag[0] == True:
                        return
                    if lookahead == ";":
                        self.clear_all()
                        break
                    elif lookahead in assignment_number:
                        if self.datatype_value not in ["dec", "int"]:
                            self.error_message(f"Compound Assignment is only allowed for number identifier")
                            return
                    elif lookahead.startswith("id"):
                        self.checkIDType(lexeme[self.current_token_index])
                        if self.getState("next", "token", self.current_token_index+1) == "(":
                            #Function call
                            identifier = lexeme[self.current_token_index]
                            self.checkIfIDNotDeclared(identifier)
                            self.current_token_index += 2
                            lookahead = token[self.current_token_index]
                            paren = 1
                            args_type = []
                            
                            while True:
                                print(f"param {lookahead}/{paren}/{lexeme[self.current_token_index]}/{self.current_token_index}")
                                if errorflag[0] == True:
                                    return
                                if paren == 0:
                                    self.check_function_arguments(identifier, args_type)
                                    break
                                elif lookahead == "(":
                                    paren += 1
                                elif lookahead == ")":
                                    paren -= 1
                                elif lookahead in semantic_datatype:
                                    args_type.append(lookahead)
                                    self.current_token_index+=3
                                    lookahead = token[self.current_token_index]
                                elif lookahead.startswith("id"):
                                    self.checkIDType(lexeme[self.current_token_index])
                                    args_id = lexeme[self.current_token_index]
                                    datatype_arguments = self.getDatatype(args_id)
                                    args_type.append(datatype_arguments)
                                elif lookahead in literals:
                                    datatype_arguments = self.getDatatypeOnLiterals(lookahead)
                                    args_type.append(datatype_arguments)
                                self.current_token_index += 1
                                lookahead = token[self.current_token_index]
                        else:
                            identifier = lexeme[self.current_token_index]
                            self.checkIfIDNotDeclared(identifier)
                            self.checkIfAssignmentIDIsValid(identifier)
                    elif lookahead in semantic_datatype:
                        type_conversion_type = lookahead
                        if type_conversion_type != self.datatype_value:
                            self.error_message("Type Mismatch: The declared data type and the initialization value type must match.")
                            return
                        self.current_token_index += 2
                        lookahead = token[self.current_token_index]
                        if lookahead.startswith("id"):
                            self.checkIDType(lexeme[self.current_token_index])
                            identifier = lexeme[self.current_token_index]
                            self.checkIfIDNotDeclared(identifier)
                            self.checkTypeConversion(type_conversion_type, identifier, "id")
                        elif lookahead in literals:
                            self.checkTypeConversion(type_conversion_type, lookahead, "literals")
                    elif lookahead in literals:
                        self.checkIfAssignmentIsValid(lookahead)
                    elif lookahead == ",":
                        self.clear_all()
                        rhs_identifier = lexeme[self.current_token_index+1]
                        self.datatype_value = self.getDatatype(rhs_identifier)
                        
                    self.current_token_index += 1
                    lookahead = token[self.current_token_index]
        #Condition 
        print("For Condition")
        self.current_token_index += 1
        lookahead = token[self.current_token_index]
        condition_valid = False
        while True:
            print(f"FOR CONDITION: {lookahead}")
            if errorflag[0] == True:
                return
            if lookahead == ";":
                if not condition_valid:
                    self.error_message(f"For condition must evaluate to boolean values")
                    return
                print("Breaking")
                break
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype == "bln":
                    condition_valid = True
            elif lookahead in ["true", "false"]:
                condition_valid = True
            elif lookahead in booleanValue:
                condition_valid = True
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
        #Iteration
        print("For Iteration")
        param = 0
        while True:
            if errorflag[0] == True:
                return
            if lookahead == ")" and param == 0:
                return
            elif lookahead == "(":
                param +=1
            elif lookahead == ")":
                param -= 1
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype not in ["int", "dec"]:
                    self.error_message("For iteration only allow number.")
                    return
            elif lookahead in arithmetic_operator:
                    self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
    
    def handle_condition_statement(self):
        self.current_token_index += 2
        lookahead = token[self.current_token_index]
        param = 1
        condition_valid = False
        while True:
            print(f"CONDITION VALUE: {lookahead}/{condition_valid}")
            if errorflag[0] == True:
                return
            if param == 0:
                if not condition_valid:
                    self.error_message(f"Expressions used in conditional statements must result in a boolean value.")
                    return
                return
            elif lookahead == "(":
                param += 1
            elif lookahead == ")":
                param -= 1
            elif lookahead in assignment_number:
                self.error_message("Compound Assignment is only allowed for number identifier. ")
                return
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype == "bln":
                    condition_valid = True
            elif lookahead in ["true", "false"]:
                condition_valid = True
            elif lookahead in booleanValue:
                condition_valid = True
            elif lookahead == "bln" and self.getState("next", "token", self.current_token_index+1) == "(":
                condition_valid = True
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
    
    #Checker
    def checkIfIDAlreadyDeclared(self, id):
        if errorflag[0] == True:
            return
        identifier_exists = any(
            entry["identifier"].split("[")[0]== id and #Check if id exist
            entry["level"]["parent"] == self.parent #Check if same scope
            for entry in self.symbol_table
        )

        if identifier_exists:
            self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared in the same scope")
            return
    
    def checkIfIDNotDeclared(self, id):
        print(f"Check if id not declared {id}/{self.isDeclaredInParent(id, self.parent)}")
        if errorflag[0] == True:
            return
        identifier_not_found = not any(
            entry["identifier"] == id and #Check if id exist
            self.isDeclaredInParent(id, self.parent) #Check if id already declared in parent scope
            for entry in self.symbol_table
        )
        if identifier_not_found:
            print(f"Identifier {id} not declared")
            self.error_message(f"Identifier {id} not declared")
            return
         
    def checkIfAssignmentIsValid(self, lookahead):
        if errorflag[0] == True:
            return
        Expected = self.getLiterals(self.datatype_value)
        Found = self.getLiterals(lookahead)
        print(f"Assignment Valid: {lookahead}, {self.datatype_value}")
        if Expected != Found:
            if Expected == "decimal number" and Found == "integer":
                pass
            elif Expected == "string" and Found == "character":
                pass
            else:
                print(f"Assignment type mismatch. Expected {Expected} but found {Found}.")
                self.error_message(f"Assignment type mismatch. Expected {Expected} but found {Found}.")
                return
    def checkIfAssignmentIDIsValid(self, identifier):
        if errorflag[0] == True:
            return
        Expected = self.getLiterals(self.datatype_value)
        datatype = self.getDatatype(identifier)
        Found = self.getLiterals(datatype)
        if Expected != Found:
            if Expected == "decimal number" and Found == "integer":
                pass
            elif Expected == "string" and Found == "character":
                pass
            else:
                print(f"Assignment ID type mismatch. Expected {Expected} but found {Found}.")
                self.error_message(f"Assignment type mismatch. Expected {Expected} but found {Found}.")
                return
    
    def checkTypeConversion(self, type_conversion_type, type_conversion_value, state):
        if errorflag[0] == True:
            return
        if state == "id":
            datatype = self.getDatatype(type_conversion_value) #The datatype of id int(id)
            type_literal = self.getLiteralTypeconversion(datatype)
            literal = self.getLiterals(type_literal)
            valid_types = valid_conversion.get(type_conversion_type, [])
            if type_conversion_value not in valid_types:
                self.error_message(f"Type Mismatch: {literal} cannot be converted to {type_conversion_type}. Expected literals: {valid_types}")
                return
        else:
            valid_types = valid_conversion.get(type_conversion_type, [])
            literal = self.getLiterals(type_conversion_value)
            if type_conversion_value not in valid_types:
                self.error_message(f"Type Mismatch: {literal} cannot be converted to {type_conversion_type}. Expected literals: {valid_types}")
                return
    
    def checkOperand(self):
        print("checking operand")
        #Semantic For Zero Value
        prev = next = nextLexeme = prev4 = ""
        lookahead = token[self.current_token_index]
        if self.current_token_index < len(token) and self.current_token_index > 0:
            prev = token[self.current_token_index-1]
            next = token [self.current_token_index+1]
            nextLexeme = lexeme[self.current_token_index+1]
            if self.current_token_index > 4:
                prev4 = token[self.current_token_index-4]
        if nextLexeme == "0":
            print("0")
            if lookahead == "/":
                self.error_message(f"Division by Zero is not allowed")
                return
            elif lookahead == "%":
                self.error_message(f"Modulo by Zero is not allowed")
                return
        if prev.startswith("id"):
            identifier = lexeme[self.current_token_index-1]
            datatype = self.getDatatype(identifier)
            prev = self.getLiteralTypeconversion(datatype)
        if next.startswith("id"):
            identifier = lexeme[self.current_token_index+1]
            datatype = self.getDatatype(identifier)
            next = self.getLiteralTypeconversion(datatype)
        if prev4.startswith("id"):
            identifier = lexeme[self.current_token_index-4]
            datatype = self.getDatatype(identifier)
            prev4 = self.getLiteralTypeconversion(datatype)
        print(f"check operand {prev}/{next}/{prev4}")
        if lookahead in arithmetic_operator:
            if next in {"str_lit", "chr_lit", "true", "false"}:
                self.error_message(f"Use of arithmetic operation '{lookahead}' is not valid for {next}. Use proper type conversion")
                return
            elif prev in {"str_lit", "chr_lit", "true", "false"}:
                self.error_message(f"Use of arithmetic operation '{lookahead}' is not valid for {prev}. Use proper type conversion")
                return
            elif prev4 in {"str", "chr", "bln"}:
                self.error_message(f"Use of arithmetic operation '{lookahead}' is not valid for type conversion {prev4}. Use proper type conversion")
                return
            elif next in {"str", "chr", "bln"}:
                self.error_message(f"Use of arithmetic operation '{lookahead}' is not valid for type conversion {next} . Use proper type conversion")
                return
    
    def checkPreUnary(self):
        self.current_token_index += 1
        identifier = lexeme[self.current_token_index]
        lookahead = token[self.current_token_index]
        self.checkIfIDNotDeclared(identifier)
        identifier_datatype = self.getDatatype(identifier)
        found_literal = self.getLiteralBasedOnDatatype(identifier_datatype)
        identifier_type = self.getType(identifier)
        if identifier_type == "const":
            self.error_message(f"Unary statements must not be a constant")
            return
        if identifier_datatype not in ["int", "dec"]:
            self.error_message(f"Unary statement requires a number. Found: {found_literal}")
            return
    def checkPostUnary(self, identifier):
        self.checkIfIDNotDeclared(identifier)
        identifier_datatype = self.getDatatype(identifier)
        found_literal = self.getLiteralBasedOnDatatype(identifier_datatype)
        identifier_type = self.getType(identifier)
        if identifier_type == "const":
            self.error_message(f"Unary statements must not be a constant")
            return
        if identifier_datatype not in ["int", "dec"]:
            self.error_message(f"Unary statement requires a number. Found: {found_literal}")
            return
    
    def checkBooleanAssignment(self):
        lookahead = token[self.current_token_index]
        print(f"Boolean Assignment: ")
        identifier_bln = ""
        condition_valid = False
        while True:
            print(f"BOOLEAN VALUE: {lookahead}/{condition_valid}")
            if errorflag[0] == True:
                return
            if lookahead == ";" or lookahead == ",":
                if not condition_valid:
                    self.error_message(f"Assignment type mismatch. Boolean assignment must return a boolean value")
                    return
                
                return
            elif identifier_bln == "" and lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier_bln = lexeme[self.current_token_index]
            elif lookahead in assignment_number:
                self.error_message("Compound Assignment is only allowed for number identifier. ")
                return
            elif self.getType(identifier_bln) == "const":
                self.error_message(f"A constant identifier can only be declared in a declaration statement")
                return
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype == "bln":
                    condition_valid = True
            elif lookahead in ["true", "false"]:
                condition_valid = True
            elif lookahead in booleanValue:
                condition_valid = True
            elif lookahead == "bln" and self.getState("next", "token", self.current_token_index+1) == "(":
                condition_valid = True
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
        
    def checkBooleanDeclaration(self):
        print(f"BOOLDEC {self.identifier_value}")
        self.identifier_value = ""
        lookahead = token[self.current_token_index]
        condition_valid = False
        while True:
            print(f"BOOLEAN DECLARATION VALUE: {lookahead}/")
            if errorflag[0] == True:
                return
            if lookahead == ";":
                if not condition_valid:
                    self.error_message(f"Assignment type mismatch. Boolean assignment '{self.identifier_value}' must return a boolean value")
                    return
                self.add_symbol_table()
                self.clear_all()
                return
            elif self.identifier_value == "" and lookahead.startswith("id"):
                self.identifier_value = lexeme[self.current_token_index]
                self.checkIfIDAlreadyDeclared(self.identifier_value)
                if self.getState("next", "token", self.current_token_index+1) in [",", ";"]:
                    condition_valid = True
            elif lookahead in assignment_number:
                self.error_message(f"Compound assignment is only allowed for number types")
                return
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype == "bln":
                    condition_valid = True
            elif lookahead in ["true", "false"]:
                condition_valid = True
            elif lookahead in booleanValue:
                condition_valid = True
            elif lookahead == "bln" and self.getState("next", "token", self.current_token_index+1) == "(":
                condition_valid = True
            elif lookahead == ",":
                if not condition_valid:
                    self.error_message(f"Assignment type mismatch. Boolean assignment '{self.identifier_value}' must return a boolean value")
                    return
                condition_valid = False
                self.add_symbol_table()
                self.identifier_value = ""
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
    
    def checkStringAssignment(self):
        lookahead = token[self.current_token_index]
        print(f"String Assignment: ")
        identifier_bln = ""
        string_valid = False
        while True:
            print(f"STRING VALUE: {lookahead}/{string_valid}")
            if errorflag[0] == True:
                return
            if lookahead == ";" or lookahead == ",":
                if not string_valid:
                    self.error_message(f"Assignment type mismatch. String assignment must return a string value")
                return
            elif identifier_bln == "" and lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier_bln = lexeme[self.current_token_index]
            elif lookahead in assignment_number:
                self.error_message("Compound Assignment is only allowed for number identifier. ")
                return
            elif self.getType(identifier_bln) == "const":
                self.error_message(f"A constant identifier can only be declared in a declaration statement")
                return
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype in ["chr", "str"]:
                    string_valid = True
            elif lookahead in ["&", "str_lit", "chr_lit"]:
                string_valid = True
            elif lookahead == "str" and self.getState("next", "token", self.current_token_index+1) == "(":
                string_valid = True
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
        
    def checkStringDeclaration(self):
        print(f"StringDec {self.identifier_value}")
        self.identifier_value = ""
        lookahead = token[self.current_token_index]
        string_valid = False
        while True:
            print(f"String DECLARATION VALUE: {lookahead}/")
            if errorflag[0] == True:
                return
            if lookahead == ";":
                if not string_valid:
                    self.error_message(f"Assignment type mismatch. String assignment '{self.identifier_value}' must return a string")
                    return
                self.add_symbol_table()
                self.clear_all()
                return
            elif self.identifier_value == "" and lookahead.startswith("id"):
                self.identifier_value = lexeme[self.current_token_index]
                self.checkIfIDAlreadyDeclared(self.identifier_value)
                if self.getState("next", "token", self.current_token_index+1) in [",", ";"]:
                    string_valid = True
            elif lookahead in assignment_number:
                self.error_message(f"Compound assignment is only allowed for number types")
                return
            elif lookahead.startswith("id"):
                self.checkIDType(lexeme[self.current_token_index])
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                datatype = self.getDatatype(identifier)
                if datatype in ["str", "chr"]:
                    string_valid = True
            elif lookahead in ["&", "str_lit", "chr_lit"]:
                string_valid = True
            elif lookahead == "str" and self.getState("next", "token", self.current_token_index+1) == "(":
                string_valid = True
            elif lookahead == ",":
                if not string_valid:
                    self.error_message(f"Assignment type mismatch. String assignment '{self.identifier_value}' must return a string")
                    return
                string_valid = False
                self.add_symbol_table()
                self.identifier_value = ""
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index += 1
            lookahead = token[self.current_token_index]
    
    def checkIDType(self, id):
        identifier_type = self.getType(id)
        next_token = self.getState("next", "token", self.current_token_index+1)
        if identifier_type == "segm":
            if next_token != "(":
                self.error_message(f"Type mismatch. {id} is declared as a function.")
                return
        elif identifier_type == "array":
            if next_token != "[":
                self.error_message(f"Type mismatch. {id} is declared as an array")
                return
    
    def checkDisp(self):
        param = 1
        self.current_token_index +=2
        lookahead = token[self.current_token_index]
        while True:
            if errorflag[0] == True:
                return
            if param == 0:
                return
            elif lookahead == ")":
                param -= 1
            elif lookahead == "(":
                param += 1
            elif lookahead.startswith("id"):
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                if self.getState("prev", "token", self.current_token_index-1) in ["++", "--"]:
                    self.checkPostUnary(identifier)
            elif lookahead in arithmetic_operator:
                self.checkOperand()
            self.current_token_index +=1
            lookahead = token[self.current_token_index]
    
    #Getter
    def getState(self, pointer, state, index):
        if pointer == "prev":
            if index < 0:
                if state == "token":
                    return token[index]
                else:
                    return lexeme[index]
        else:
            if index < len(token):
                if state == "token":
                    return token[index]
                else:
                    return lexeme[index]
    
    def getDatatype(self, id):
        print(f"Get datatype: {id}")
        for entry in self.symbol_table:
            if entry["identifier"].split("[")[0] == id:
                return entry["datatype"] 
        return ""
    def getDatatypeOnLiterals(self, literals):
        if literals == "int_lit":
            return "int"
        elif literals == "dec_lit":
            return "dec"
        elif literals == "str_lit":
            return "str"
        elif literals == "chr_lit":
            return "chr"
        elif literals in {"true", "false"}:
            return "bln"
    def getLiterals(self, lookahead):
        if lookahead == "int" or lookahead == "int_lit":
            return "integer"
        elif lookahead == "dec" or lookahead == "dec_lit":
            return "decimal number"
        elif lookahead == "str" or lookahead == "str_lit":
            return "string"
        elif lookahead == "chr" or lookahead == "chr_lit":
            return "character"
        elif lookahead == "bln" or lookahead in {"true", "false"}:
            return "boolean value"
    def getLiteralBasedOnDatatype(self, datatype):
        if datatype == "int":
            return "integer"
        elif datatype == "dec":
            return "decimal"
        elif datatype == "str":
            return "string"
        elif datatype == "chr":
            return "character"
        elif datatype == "bln":
            return "boolean value"
    def getLiteralTypeconversion(self, datatype):
        if datatype == "int":
            return "int_lit"
        elif datatype == "dec":
            return "dec_lit"
        elif datatype == "str":
            return "str_lit"
        elif datatype == "chr":
            return "chr_lit"
        elif datatype == "bln":
            return "false"
    def check_function_arguments(self, segment_id, actual_arg_types):
        print(actual_arg_types)
        for entry in self.parameterList:
            if entry['Segment ID'] == segment_id:
                if len(actual_arg_types) != entry['total_args']:
                    self.error_message(f"Argument count mismatch for Segment '{segment_id}'. Expected {entry['total_args']}, got {len(actual_arg_types)}.")
                    return 
                for i in range(len(actual_arg_types)):
                    expected_type = entry['args'][i]['datatype']
                    actual_type = actual_arg_types[i]
                    expected_literal = self.getLiteralBasedOnDatatype(expected_type)
                    actual_literal = self.getLiteralBasedOnDatatype(actual_type)
                    if expected_type != actual_type:
                        self.error_message(f"Type mismatch for argument {i+1} in Segment '{segment_id}'. Expected {expected_literal} literal, got {actual_literal} literal.")
                        return 
                return 
        
        self.error_message(f"No function with Segment ID '{segment_id}' found.")
        return False
    def getType(self, id):
        print(f"Get Type: {id}")
        for entry in self.symbol_table:
            if entry["identifier"].split("[")[0] == id:
                return entry["type"] 
        return ""
    def getDimension(self, id):
        print(f"Get Type: {id}")
        for entry in self.symbol_table:
            if entry["identifier"].split("[")[0] == id:
                return entry["dimension"] 
        return ""
    #Parent Checker
    def isDeclaredInParent(self, variable_id, current_scope):
        while current_scope is not None:
            for symbol in self.symbol_table:
                if symbol["identifier"] == variable_id and symbol["level"]["parent"] == current_scope:
                    return True  # Variable is already declared parent node
            # Traverse parent scope
            for symbol in self.symbol_table:
                if symbol["identifier"] == current_scope:
                    current_scope = symbol["level"]["parent"]
                    break
            else:
                break  # End node
        return False  # Variable is not declared in parent node
    
    #Proccesor
    def updateDatatype(self, identifier, new_datatype):
        print(f"UPDATING DATATYPE {identifier}/{self.parent}/{new_datatype}")
        for entry in self.symbol_table:
            print(entry)
            print(f"ID FOUND: {entry["identifier"] == identifier }")
            print(f"PARENT FOUND: {entry["level"]["parent"] == self.parent}")
            print(f"ALL {entry["identifier"] == identifier and entry["level"]["parent"] == self.parent}")
            if (
                entry["identifier"] == identifier and 
                entry["level"]["parent"] == self.parent
            ):
                entry["datatype"] = new_datatype
                print("MATCH FOUND")
                break
    def clear_all(self):
        self.type_value = ""
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.dimension_value = ""
       
       
    def update_param_symbol(self, segment_id, datatype_value, parameter_id):
        new_arg = {"datatype": datatype_value, "ID": parameter_id}

        # Check if an entry with the same Segment ID exists
        for entry in self.parameterList:
            if entry["Segment ID"] == segment_id:
                entry["args"].append(new_arg)
                entry["total_args"] = len(entry["args"])
                break
        else:
            # If no existing entry, create a new one
            self.argsData = {
                "Segment ID": segment_id,
                "args": [new_arg],
                "total_args": 1,
            }
            self.parameterList.append(self.argsData)
        
        self.type_value = "parameter"
        self.literal_value = literal_types.get(self.datatype_value, "")
        self.add_symbol_table()
    def add_symbol_table(self):
        print("updating symbolo")
        data = {
            "type": self.type_value,
            "datatype": self.datatype_value,
            "identifier": self.identifier_value,
            "literals": self.literal_value,
            "scope": self.scope_value,
            "dimension": self.dimension_value,
            "level": {"parent": self.parent, "level": self.level_value}
        }
        self.symbol_table.append(data)
        self.printSymbolTable()
    def printSymbolTable(self):
        for entry in self.symbol_table:
            print(entry)
        print("----PARAMETER-----")
        for entry in self.parameterList:
            print(entry)
        print("----PARAMETER-----")
    def semantic_nonterminal(self, top):
        if top == "<type_conversion>":
            self.is_typeconversion = True
        else:
            self.top = top