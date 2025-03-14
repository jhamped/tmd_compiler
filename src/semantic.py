from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def semantic(console):    
    current_token_index = 0
    prevlookahead = ""
    semantic_checker = Semantic(console)
    
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
        console.insert(tk.END,"Input accepted: Syntactically correct.")
        semantic_checker.printSymbolTable()
        
class Semantic:
    def __init__(self, console):
        self.symbol_table = []
        self.parameterList = []
        self.argsData = {}
        self.parentStack = ["global"]
        self.console = console
        self.lookahead = ""
        self.top = ""
        
        self.error_flag = False
        self.current_token_index = 0
        
        self.isTemporary = True
        self.is_segment = False
        self.is_param = False
        self.is_assignment = False
        self.is_array = False
        self.is_idArray = False
        self.is_functionCall = False
        self.is_return = False
        self.is_tempLiteral = ""
        self.declare_flag = False
        
        self.check_idarray = False
        self.is_typeconversion = False
        self.isVariableDefinition = False
        self.checkID = False
        self.idStore = False
        
        self.is_struct = False
        self.strcID = ""
        self.isStructElementDec = False
        self.more_instance = False
        self.isInstance = False
        
        
        self.operator = ""
        self.isBoolean = False
        self.logicalOp = False
        self.leftOperand = ""
        self.rightOperand = ""
        self.datatypeOperand = ""
        self.tempOperandLit = ""
        self.tempOperator =""
        
        self.total_args = 0
        self.args_declared = False
        self.segmID = ""
        self.tempint = 0
        
        self.temporary_variable = ""
        self.temporary_variable2 = ""
        self.is_string = False
        self.is_var = False
        self.array_temp = ""
        self.row = 0
        self.column = 0
        
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.scope_value = "global"
        self.type_value = ""
        self.dimension_value = ""
        self.parent = "global"
        self.level_value = 0
        self.datatype_conversion = ""
        
    def error_message(self, error):
        line = rows[self.current_token_index] if self.current_token_index < len(rows) else "0"
        column = col[self.current_token_index] if self.current_token_index < len(col) else "0"
        self.console.insert(tk.END, "Semantic Error: ", "error")
        self.console.insert(tk.END, f"{error}")
        self.console.insert(tk.END, f"\n           line {line}, col {column}\n", "ln_col")
        self.error_flag = True
        
    def clearValue(self):
        print("Clear Value")
        self.temporary_variable =""
        self.is_string = False
        self.is_var = False
        self.is_array = False
        self.is_typeconversion = False
        
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.type_value = ""
        self.dimension_value = ""
        self.datatype_conversion = ""
        
    def clearAll(self):
        self.clearValue
        self.scope_value = "global"
        self.dimension_value = ""
        
    def semantic_process(self, lookahead, current_token_index):
        self.current_token_index = current_token_index
        self.lookahead = lookahead
        if self.declare_flag and self.lookahead != ";":
            return
        else:
            self.declare_flag = False
        #Nested Function Level
        if lookahead == "{" and not self.isVariableDefinition:
            self.level_value +=1
        elif lookahead in codeblocks:
            temp = self.parent
            self.parent = temp + str(self.level_value)
            temp2 = self.parent
            self.parentStack.append(self.parent)
            self.identifier_value = temp2
            self.parent = temp
            self.add_symbol_table()
            self.parent = temp2
        elif lookahead == "}" and not self.isVariableDefinition and not self.is_struct:
            
            self.parentStack.pop()
            if self.parentStack:
                self.parent = self.parentStack[-1]
            print(self.parent)
        
        """if self.top == "<assignment_statements>" or self.top == "<initialization>":
            self.console.insert(tk.END, f"{self.top}   {lexeme[self.current_token_index]}\n")"""
        if lookahead == "main":
            self.handle_main()
        elif lookahead == "segm":
            self.is_segment = True
    
        #Parameter
        elif self.is_param:
            self.handle_param()
        #Type
        elif lookahead == "const":
            self.type_value = lookahead
        elif lookahead == "strc":
            self.type_value = lookahead
            self.is_struct = True
        elif self.is_struct:
            self.handle_struct()
        elif self.lookahead == "." or self.isInstance:
            print("d2")
            self.process_strcElement()
        elif self.lookahead == "ret" or self.is_return:
            self.handle_return()
        #elif lookahead in id_type : #constant and strc
        #    print("ID type")
        #    self.type_value = lookahead
        elif self.top == "<identifier_declaration>" or self.top == "<initialization>" or self.top == "<foreach_statement>":
            self.handle_declaration()
        elif self.lookahead == "id" and not self.is_assignment : #Assignment and ID declaration
            print("handle identifier")
            self.handle_identifier()
        
        elif self.lookahead in assignment_operator or self.is_assignment:
            print(f"Is Assignment {self.lookahead}/{self.is_assignment}/{self.is_idArray}")
            self.handle_assignment()
        elif self.is_idArray and not self.is_assignment:
            print("isIDarray")
            self.handle_IDarray()
            self.process_IDarray()
            self.hasIDBeenDeclared()
        #Division by zero
        
        if self.lookahead == "/" or self.lookahead == "%":
            self.operator = self.lookahead
        elif lexeme[self.current_token_index] == "0":
            if self.operator == "/":
                self.error_message(f"Division by Zero is not allowed")
            elif self.operator == "%":
                self.error_message(f"Modulo by Zero is not allowed")
        else:
            self.operator = ""
        if self.lookahead in booleanValue:
            self.tempOperator = self.lookahead
            self.findLiterals()
            self.tempOperandLit = self.literal_value
            print(f"Is boolean {self.identifier_value}/{self.lookahead}/{self.literal_value}/{self.datatypeOperand}")
            if self.logicalOp:
                self.rightOperand = True
            self.isBoolean = True
            if self.datatypeOperand != self.literal_value and self.datatypeOperand != "":
                self.error_message(f"Logical Operator cannot be applied to different datatype")
                print(f"1 Logical Operator cannot be applied to different datatype")
            else:
                self.datatypeOperand = self.literal_value
        elif self.lookahead in str_logical_operator:
            print(f"logical boolean {self.identifier_value}/{self.lookahead}/{self.literal_value}")
            self.datatypeOperand = self.literal_value
            self.leftOperand = self.isBoolean
            self.logicalOp = True
        elif self.top == "<condition>":
            if self.lookahead == ";" or self.lookahead == ")":
                self.checkBoolean()
                self.top = ""
        elif self.lookahead == ";":
            print("Reset operator")
            self.datatypeOperand = ""
            self.isBoolean = False
            self.operator = ""
    def update_symbol_table(self):
        if self.lookahead == "," and not self.assignment_declaration:
            print("Update Symbol ,")
            self.add_symbol_table()
        elif self.lookahead == ";" and not self.assignment_declaration:
            print("Update Symbol ;")
            self.top = ""
            if self.isLogical:
                self.checkIfLogicalOperand()
            else:
                self.add_symbol_table()
            self.clearValue()
    def update_param_symbol(self):
        if self.error_flag:
            self.error_flag = False
            return
        segment_id = self.parent
        new_arg = {"datatype": self.datatype_value, "ID": self.identifier_value}

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
        
        
        print("----PARAMETER-----")
        for entry in self.parameterList:
            print(entry)
        print("----PARAMETER-----")
        self.type_value = "parameter"
        self.literal_value = literal_types.get(self.datatype_value, "")
        self.add_symbol_table()
        
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
        
    def handle_param(self):
        if self.lookahead in datatype:
            self.datatype_value = self.lookahead
            if self.datatype_value == "var":
                self.is_var = True
        elif self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.hasIDBeenDeclared()
        elif self.lookahead == ",":
            self.update_param_symbol()
        elif self.lookahead == ")":
            if self.datatype_value != "":
                self.update_param_symbol()
                self.clearValue()
            self.is_param = False
            
    def handle_struct(self):
        #self.console.insert(tk.END, f" lexem {lexeme[self.current_token_index]} STRC {self.strcID} Element {self.isStructElementDec} \n")
        if self.lookahead == "id" and self.strcID == "" :
           self.strcID = lexeme[self.current_token_index]
        elif self.lookahead == "{":
            self.identifier_value = self.strcID
            self.hasStructIDBeenDeclared() #check if strcID already declared
            self.type_value = "struct"
            self.add_symbol_table()
            self.parentStack.append(self.identifier_value)
            self.parent = self.identifier_value #change parent name
            self.scope_value = self.identifier_value  
            #self.is_structIDDeclared = True
            self.isStructElementDec = True
        elif self.lookahead in datatype:
            self.datatype_value = self.lookahead
        elif self.lookahead  == "id":
            self.identifier_value = lexeme[self.current_token_index]
            if self.isStructElementDec:
                print("element")
                #self.console.insert(tk.END, f"ELEMENT: {self.parent} {self.identifier_value} {self.datatype_value } \n")
                self.type_value = "strc element"
                self.hasIDBeenDeclared()
                self.add_symbol_table()
            elif self.more_instance:
                print("instance")
                temp = self.parent
                self.parent = self.strcID
                self.type_value = "instance"
                self.hasInstanceIDBeenDeclared()
                self.add_symbol_table()
                self.parent = temp
            elif self.lookahead == "id":
                print("id")
                self.type_value = "instance"
                self.hasStructTypeBeenDefined()
                self.hasInstanceIDBeenDeclared()
                self.add_symbol_table()
        elif self.lookahead == "}":
            self.isStructElementDec = False
            self.more_instance = True
            self.parentStack.pop()
            if self.parentStack:
                self.parent = self.parentStack[-1]
                print("strc pop")
        elif self.lookahead == ";" and not self.isStructElementDec:
            self.is_struct = False
            self.moreInstance = False
            self.strcID = ""
            
            
            
    def handle_foreach_statement(self):
        if self.lookahead in datatype:
            if self.is_typeconversion:
                self.datatype_conversion = self.lookahead
            else:
                self.datatype_value = self.lookahead
                self.variable_declaration = True
                if self.datatype_value == "var":
                    self.is_var = True
        elif not self.isTemporary and self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.findType()
            if self.type_value != "array":
                print(f"{self.identifier_value} must be an array")
                self.error_message(f"{self.identifier_value} must be an array")
                self.clearValue()
        elif self.datatype_value == "str" and self.lookahead == "&":
            self.is_string = True
        elif self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.hasIDBeenDeclared()
            if self.is_typeconversion:
                self.checkTypeConversion()
                self.is_typeconversion = False
            if self.is_assignment and not self.is_string:
                self.findLiterals()
                if self.is_var:
                    self.findVarKey()
                    self.is_var = False
                self.checkLiterals()
        elif self.lookahead == "in":
            self.is_assignment = False
            if self.identifier_value == "":
                self.identifier_value = self.temporary_variable
            #self.console.insert(tk.END, f"B{self.datatype_value}{self.identifier_value}{self.temporary_variable}\n")
            if self.literal_value == "":
                self.literal_value = literal_types.get(self.datatype_value, "")
            self.add_symbol_table()
            self.isVariableDefinition = False
            self.clearValue()
            self.isTemporary = False
        elif self.lookahead == ")":
            self.top = ""
            return
                
            
    def handle_declaration(self):
        self.isVariableDefinition = True
        print("Declaration")
        if self.top == "<foreach_statement>":
            print(f"Declaration -> foreach")
            self.handle_foreach_statement()
            return
        if self.lookahead == ")" and self.is_functionCall:
            print(f"Declaration -> )")
            self.is_functionCall = False
        elif self.is_functionCall:
            print(f"Declaration -> functioncall")
            self.handleFunctionCall()
            return
        elif self.lookahead in datatype:
            print(f"Declaration -> datatype")
            if self.is_typeconversion:
                self.datatype_conversion = self.lookahead
            else:
                self.datatype_value = self.lookahead
                self.variable_declaration = True
                if self.datatype_value == "var":
                    self.is_var = True
        elif self.datatype_value == "str" and self.lookahead == "&":
            print(f"Declaration -> str and &")
            self.is_string = True
        #Array
        elif self.lookahead == "[":
            print(f"Declaration -> [")
            self.is_array = True
            
        elif self.is_array:
            print(f"Declaration -> handle_array")
            self.handle_array()
        #Initialization
        elif self.lookahead == "id":
            print(f"Declaration -> id")
            self.identifier_value = lexeme[self.current_token_index]
            self.findDatatype
            if self.datatype_value == "":
                print(f"Identifier {self.identifier_value} not declared")
                self.error_message(f"Identifier {self.identifier_value} not declared")
                self.declare_flag = True
            else:
                self.hasIDBeenDeclared()
            self.findType()
            if self.type_value == "segm":
                print(f"Function call declaration{self.datatype_value}") 
                self.is_functionCall = True
                self.segmID = self.identifier_value
                #self.findDatatype()
                self.checkLiterals()
                print(f"---{self.datatype_value}/{self.literal_value}/Function call declaration") 
                return
            if not self.idStore:
                self.temporary_variable = self.identifier_value
                self.idStore = True
            if self.is_typeconversion:
                self.checkTypeConversion()
                self.is_typeconversion = False
            if self.is_assignment and not self.is_string:
                #self.identifier_value = self.temporary_variable
                if self.datatype_value == "bln":
                    self.findLiterals()
                    return
                self.findLiterals()
                if self.is_var:
                    self.findVarKey()
                    self.is_var = False
                self.checkLiterals()
        elif self.lookahead in literals:
            self.literal_value = self.lookahead
            if self.datatype_value == "bln":
                return
            if self.is_typeconversion:
                self.checkTypeConversion()
                self.is_typeconversion = False
                return
            if self.is_var:
                self.findVarKey()
                self.is_var = False
            self.checkLiterals()
        elif self.lookahead == "=":
            self.is_assignment = True
        elif self.lookahead == ",":
            if self.datatype_value == "bln":
                self.checkBoolean()
            self.is_assignment = False
            self.identifier_value = self.temporary_variable
            self.idStore= False
            self.literal_value = literal_types.get(self.datatype_value, "")
            self.add_symbol_table()
        elif self.lookahead == ";":
            print(f"adding dec {self.is_assignment}")
            if self.datatype_value == "bln" and self.is_assignment:
                self.checkBoolean()
            self.is_assignment = False
            self.identifier_value = self.temporary_variable
            self.idStore = False
            #self.console.insert(tk.END, f"B{self.datatype_value}{self.identifier_value}{self.temporary_variable}\n")
            self.literal_value = literal_types.get(self.datatype_value, "")
            self.add_symbol_table()
            self.isVariableDefinition = False
            self.clearValue()
            self.top = ""
            
    def handle_identifier(self): 
        if self.is_segment: 
            self.identifier_value = lexeme[self.current_token_index]
            self.type_value = "segm"
            self.hasIDBeenDeclared()
            self.add_symbol_table() 
            self.parentStack.append(self.identifier_value)
            self.parent = self.identifier_value #change parent name
            self.scope_value = self.identifier_value  
            self.is_param = True
            self.is_segment = False  
        else:
            self.checkID = True
            self.identifier_value = lexeme[self.current_token_index]
            self.temporary_variable = self.identifier_value
            self.findType()
            if self.literal_value == "":
                self.literal_value = literal_types.get(self.datatype_value, "")
            self.findDatatype()
            print(f"id not segm: {self.type_value}/{self.lookahead}")
            if self.type_value == "array":
                self.check_idarray = True
                self.is_idArray = True
            elif self.type_value == "struct" or self.type_value == "instance":
                self.strcID = lexeme[self.current_token_index]
                print(f"struct {self.strcID}")
            else:
                self.hasIDBeenDeclared() 
            self.checkID = False
    """def handle_assignment_statement(self):
        if not self.is_assignment and self.lookahead == "id": #Store assignment variable
            self.temporary_variable = lexeme[self.current_token_index]
            self.is_assignment = True
            self.hasIDBeenDeclared()
        elif self.is_array:
            self.array_temp = self.identifier_value
        elif self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.hasIDBeenDeclared()
            self.findLiterals()
            if self.is_var:
                self.findVarKey()
                self.is_var = False
            self.checkLiterals()
        elif self.lookahead in literals:
            self.literal_value = self.lookahead
            if self.is_var:
                self.findVarKey()
                self.is_var = False
            self.checkLiterals()
        elif self.lookahead == ";": 
            self.top = ""
            self.is_assignment = False
            self.isVariableDefinition = False
            self.temporary_variable = ""
            self.clearValue()
            return"""
            
    def handle_assignment(self):
        print(f"Handle assignment")
        self.is_assignment = True
        self.findDatatype()
        #self.console.insert(tk.END, f"ASSIGNMENT {self.lookahead}")
        self.isVariableDefinition = True
        self.findType()
        if self.type_value == "const":
            print("Constant can only be declared")
            self.error_message("Constant can only be declared")
            self.top = ""
            self.is_assignment = False
            self.isVariableDefinition = False
            self.clearValue()
            return
            
        if self.is_idArray:
            print("assignment -> idarray")
            self.process_IDarray()
            if not self.is_idArray: #if nahandle na ung id array
                self.hasIDBeenDeclared
                self.is_idArray = False
            else:
                return
        if self.is_array:
            print("assignment -> Array")
            self.array_temp = self.identifier_value
        elif self.lookahead == "id":
            print(f"assignment -> id")
            self.identifier_value = lexeme[self.current_token_index]
            self.findType()
            if self.datatype_value == "bln":
                return
            if self.type_value == "array":
                self.check_idarray = True
                self.is_idArray=True
                return
            else:
                self.is_idArray=False
            self.hasIDBeenDeclared()
            self.findLiterals()
            if self.is_var:
                self.findVarKey()
                self.is_var = False
            self.checkLiterals()
        elif self.lookahead in literals and not self.is_idArray:
            print(f"assignment -> literals")
            self.literal_value = self.lookahead
            self.findDatatype()
            if self.datatype_value == "bln":
                return
            self.literal_value = self.lookahead
            if self.is_var:
                self.findVarKey()
                self.is_var = False
            self.checkLiterals()
        elif self.lookahead == ";" or self.lookahead == ",": 
            print(f"assignment -> end ; ,")
            self.top = ""
            if self.datatype_value == "bln":
                self.checkBoolean()
            if self.type_value == "array":
                self.handle_IDarray()
            self.is_assignment = False
            self.isVariableDefinition = False
            self.clearValue()
        
    
    
    def handle_IDarray(self):
        print("handle id array")
        if self.check_idarray and self.lookahead != "[":
            print(f"1 Invalid ID: {self.identifier_value} is an array")
            self.error_message(f"Invalid ID: {self.identifier_value} is an array")
            self.is_idArray = False
            return
        else:
            self.check_idarray = False
        
            
    def handle_literals(self):
        self.literal_value = self.lookahead
        if self.isArray:
                print("Literals Array")
                self.processArray()
        if not self.type_conversion:
            print("Literals Not Type Conversion")
            self.checkLiterals() 
        if not self.variable_declaration and self.assignment_declaration:
            self.findType()
            if self.type_value == "const":
                print(f"Constant {self.identifier_value} can only be assigned once")
                self.error_message(f"Constant {self.identifier_value} can only be assigned once")
    
    def handle_array(self):
        self.type_value = "array"
        if self.lookahead in literals:
            self.processArray()
            self.literal_value = self.lookahead
            self.checkLiterals()
        elif self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.temporary_variable = self.identifier_value
            self.hasIDBeenDeclared()
            self.is_assignment = True
        elif self.lookahead == "}":
            self.processArrayEnd()
        elif self.lookahead == "=":
            self.is_assignment = False
        elif self.lookahead == "," and self.dimension_value != "":
            self.add_symbol_table()
        elif self.lookahead == ";":
            if self.is_assignment:
                self.processArray()
                self.is_assignment = False
            self.add_symbol_table()
            self.clearValue()
            self.top = ""
            return
        else: #Get array dimension
            self.handle_array_dimension()
    def handle_array_dimension(self):
        print("Array Dimension")
        if self.lookahead == "]":
            self.dimension_value = "1"
        elif self.lookahead == ",":
            self.dimension_value = "2"
            
    def handle_typeconversion(self):
        print("Type Conversion")
    def handle_typevalue(self):
        print("Type Conversion Check")
        
    def handle_return(self):
        self.is_return = True
        if self.parent == "main":
            self.error_message("Illegal Return Statement")
            self.is_return = False
            return
        if self.lookahead in literals:
            self.literal_value = self.lookahead
            self.retCheckValue()
                
        elif self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.findLiterals()
            print(f"-------------{self.literal_value}/{self.identifier_value}")
            self.retCheckValue()
        elif self.lookahead == ";":
            datatype_value = reverse_literal_types.get(self.is_tempLiteral, "")
            print(f"returning {self.parent} {datatype_value} {self.is_tempLiteral}")
            self.updateDatatype(self.parent,datatype_value)
            self.is_return = False
            
    def handleFunctionCall(self):
        if self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            
            self.findLiterals()
            argsCompatible = any(
                entry["Segment ID"] == self.segmID and
                entry["args"][self.tempint]["datatype"] == self.datatype_value
                for entry in self.parameterList
            )
            if not argsCompatible:
                print(f"Arguments incompatible")
                self.error_message(f"Arguments incompatible")
           
        elif self.lookahead in literals:
            self.datatype_value = reverse_literal_types.get(self.lookahead, "")
            print(f"a {self.datatype_value} segmid {self.segmID} {self.lookahead}")
            argsCompatible = any(
                entry["Segment ID"] == self.segmID and
                entry["args"][self.tempint]["datatype"] == self.datatype_value
                for entry in self.parameterList
            )
            if not argsCompatible:
                print(f"Arguments incompatible")
                self.error_message(f"Arguments incompatible")
           
        elif self.lookahead == ",":
            self.tempint += 1
            
            
    """def handleArgs(self):
        self.checkArgs()
        self.checkTotalArgs()
            
        print("args passed")
        
    def checkArgs(self):
        argsCompatible = any(
            entry["Segment ID"] == self.segmID and
            entry["args"][self.tempint]["datatype"] == self.datatype_value
            for entry in self.parameterList
        )
        if not argsCompatible:
            self.error_message(f"Argument incompatible datatype")
    def checkTotalArgs(self):
        print(f"checkARGS {self.segmID}")
        for entry in self.parameterList:
            if entry["Segment ID"] == self.segmID:
                total = entry["total_args"]
                if self.tempint != total:
                    self.error_message(f"Number of argument is not true")
    """
    #Finder
    def findDatatype(self):
        for entry in self.symbol_table:
            if entry["identifier"] == self.identifier_value:
                self.datatype_value = entry["datatype"] 
                return
        self.datatype_value = ""
    def findLiterals(self):
        print("finding literals")
        for entry in self.symbol_table:
            if entry["identifier"].split("[")[0] == self.identifier_value:
                self.literal_value = entry["literals"] 
                return
        self.literal_value = "None"
    def findType(self):
        for entry in self.symbol_table:
            if entry["identifier"].split("[")[0] == self.identifier_value:
                self.type_value = entry["type"] 
                return
        self.type_value = ""
        
    def findScope(self, scope):
        for entry in self.symbol_table:
            if entry["identifier"].split("[")[0] == scope:
                return entry["scope"]
        self.type_value = ""
            
    def findVarKey(self):
        for key, value in valid_literals.items():
            if value == self.literal_value:
                self.datatype_value = key
                break
    def findDatatypeWLiterals(self):
        self.reverse_literal_types = {
            v: k if k != "bln" else "bln" for k, v in literal_types.items()
        }

        # Ensure both "False" and "True" map to "bln"
        self.reverse_literal_types["True"] = "bln"
    #Checker
    def hasStructIDBeenDeclared(self):
        identifier_exists = any(
            entry["identifier"].split("[")[0] == self.strcID and
            entry["level"]["parent"] == self.parent  # Same scope check
            for entry in self.symbol_table
        )

        if identifier_exists:
            print(f"Structure {self.strcID} is already declared in the same scope")
            self.error_message(f"Structure {self.strcID} is already declared in the same scope")
    def hasStructTypeBeenDefined(self):
        struct_defined = any(
            entry["identifier"].split("[")[0] == self.strcID and
            entry["type"] == "struct"  and # Ensure it is a struct
            not entry["level"]["parent"] == self.parent
            for entry in self.symbol_table
        )

        if not struct_defined:
            same_scope = any(
                entry["level"]["parent"] == self.parent
                for entry in self.symbol_table
            )
            if same_scope:
                self.error_message(f"Structure {self.strcID} is already declared")
            else:
                self.error_message(f"Structure {self.strcID} is not declared")
                self.declare_flag = True
    def hasInstanceIDBeenDeclared(self):
        identifier_exists = any(
            entry["identifier"].split("[")[0] == self.identifier_value and
            entry["level"]["parent"] == self.parent  # Same scope check
            for entry in self.symbol_table
        )

        if identifier_exists:
            self.error_message(f"Instance {self.identifier_value} already declared in the same scope")

    def hasIDBeenDeclared(self):
        if self.is_segment:
            identifier_exists = any(
                entry["identifier"] == self.identifier_value #Check if id exist
                for entry in self.symbol_table
            )

            if identifier_exists:
                self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared in the same scope")
        
        
        elif not self.is_assignment and not self.checkID:
            identifier_exists = any(
                entry["identifier"].split("[")[0] == self.identifier_value and #Check if id exist
                entry["level"]["parent"] == self.parent #Check if same scope
                for entry in self.symbol_table
            )

            if identifier_exists:
                self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared in the same scope")
       
        else:
            current_scope = self.parent 
            identifier_not_found = not any(
                entry["identifier"] == self.identifier_value and #Check if id exist
                self.isDeclaredInParent(self.identifier_value, self.parent) #Check if id already declared in parent scope
                for entry in self.symbol_table
            )
            if identifier_not_found:
                print(f"Identifier {lexeme[self.current_token_index]} not declared")
                self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")
                self.declare_flag = True
        """if not self.is_assignment:
            if any(entry["identifier"].split("[")[0] == self.identifier_value and (entry["scope"] == self.scope_value or self.scope_value == "global") for entry in self.symbol_table):
                self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared")
        else: 
            if not any(entry["identifier"] == self.identifier_value and (entry["scope"] == self.scope_value or self.scope_value != "global") for entry in self.symbol_table):
                self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")"""
                
    def checkLiterals(self):
        #self.console.insert(tk.END, f"a {self.identifier_value}{self.datatype_value}\n")
        identifier_exists = any(
                entry["identifier"].split("[")[0] == self.identifier_value and #Check if id exist
                entry["level"]["parent"] == self.parent #Check if same scope
                for entry in self.symbol_table
            )
        if not(self.datatype_value in valid_literals and self.literal_value in valid_literals[self.datatype_value]):
            #if not identifier_exists:
            #    self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")
            #else:
            if self.is_assignment and self.lookahead == "id":
                print(f"Type Error: {self.identifier_value} cannot be initialized to {self.temporary_variable}")
                self.error_message(f"Type Error: {self.identifier_value} cannot be initialized to {self.temporary_variable}")
            else:
                print(f"Type Error: {self.identifier_value} cannot be initialized as {self.literal_value}")
                self.error_message(f"Type Error: {self.identifier_value} cannot be initialized as {self.literal_value}")

            
    
    def checkTypeConversion(self):
        if self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.findDatatype()
            self.findLiterals()
        if self.literal_value == "":
            self.error_message(f"Type Mismatch: None cannot be converted to {self.datatype_conversion}") 
            return
        if not(self.literal_value in valid_conversion[self.datatype_conversion]):
            self.error_message(f"Type Mismatch: {self.literal_value} cannot be converted to {self.datatype_conversion}") 
        elif self.datatype_conversion != self.datatype_value:\
            self.error_message(f"Type Mismatch: datatype conversion {self.datatype_conversion} cannot be assign to {self.datatype_value}") 
    
    def checkBoolean(self):
        
        if self.lookahead == id:
            self.findLiterals()
            self.findDatatype()
        print(f"Checking boolean... {self.lookahead}/{self.top}/{self.literal_value}/{self.identifier_value}/{self.datatypeOperand}")
        if self.top == "<condition>":
            if self.logicalOp and (not self.leftOperand or not self.rightOperand):
                if self.top == "<condition>":
                    print(f"1 Condition must result to a boolean value")
                    self.error_message(f"Condition must result to a boolean value")
                    return
                print(f"{self.temporary_variable} must be initialize to a boolean value")
                self.error_message(f"{self.temporary_variable} must be initialize to a boolean value")
            elif not self.isBoolean and self.datatype_value != "bln":
                if self.top == "<condition>":
                    print(f"2 Condition must result to a boolean value")
                    self.error_message(f"Condition must result to a boolean value")
                    return
                print(f"{self.temporary_variable} must be initialize to a boolean value")
                self.error_message(f"{self.temporary_variable} must be initialize to a boolean value")
        else:
            if self.is_assignment and self.datatypeOperand == "":
                print(f"{self.temporary_variable} cannot be initialized as {self.literal_value}")
                self.error_message(f"{self.temporary_variable} cannot be initialized as {self.literal_value}")
            elif self.tempOperator in relate1_op:
                if self.literal_value not in {"int_lit", "dec_lit"} or self.datatypeOperand not in {"int_lit", "dec_lit"}:
                    print(f"Relational operator is only possible with number literals")
                    self.error_message(f"Relational operator is only possible with number literals")
            elif self.datatypeOperand != self.literal_value:
                print(f"Logical Operator cannot be applied to different datatype{self.datatypeOperand}/{self.literal_value}")
                self.error_message(f"Logical Operator cannot be applied to different datatype")
           
    #Nested Function
    def isDeclaredInParent(self, variable_id, current_scope):
        while current_scope is not None:
            for symbol in self.symbol_table:
                if symbol["identifier"].split("[")[0] == variable_id and symbol["level"]["parent"] == current_scope:
                    return True  # Variable is already declared parent node
            # Traverse parent scope
            for symbol in self.symbol_table:
                if symbol["identifier"].split("[")[0] == current_scope:
                    current_scope = symbol["level"]["parent"]
                    break
            else:
                break  # End node
        return False  # Variable is not declared in parent node
    
    def retCheckValue(self):
        if self.is_tempLiteral == "":
            self.is_tempLiteral = self.literal_value
        else:
            if self.is_tempLiteral != self.literal_value:
                self.error_message("Incompatible expression when returning")
            self.is_tempLiteral = self.literal_value
    def updateDatatype(self, identifier, new_datatype):
        for entry in self.symbol_table:
            if entry["identifier"] == identifier:
                entry["datatype"] = new_datatype
                break
    #Array
    def processArray(self):
        if self.dimension_value == "1":
            self.identifier_value = f"{self.temporary_variable}[{self.row}]"
            self.row += 1
        elif self.dimension_value == "2":
            self.identifier_value = f"{self.temporary_variable}[{self.column},{self.row}]"
            self.row += 1
    def processArrayEnd(self):
        if self.dimension_value == "2":
            self.column+=1
            return
        self.row = 0
        self.column = 0
        
    def process_IDarray(self):
        print("process_IDarrray")
        if self.lookahead == "[":
            self.identifier_value = f"{self.identifier_value}["
        elif self.lookahead == "id":
            self.identifier_value = f"{self.identifier_value}0"
        elif self.lookahead in literals:     
            self.identifier_value = f"{self.identifier_value}0"
        elif self.lookahead == ",":
            self.identifier_value = f"{self.identifier_value},"
        elif self.lookahead == "]":
            self.identifier_value = f"{self.identifier_value}]"
            self.is_idArray = False
        
        elif self.lookahead != "=" and self.lookahead != ";" and self.lookahead != "}":
            print(f"2 {self.identifier_value} {self.lookahead }is an array")
            self.error_message(f"{self.identifier_value} is an array")
            self.is_idArray = False
        print(f"ID array = {self.identifier_value}")
            
    def process_strcElement(self):        
        if self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            scope = self.findScope(self.strcID)
            inStruct = self.isDeclaredInParent(self.identifier_value, self.strcID)
            print(f"--process strcElement: {self.identifier_value}/{scope}/{self.strcID}")
            if not inStruct:
                print(f"Structure {self.strcID} have no {self.identifier_value}")
                self.error_message(f"Structure {self.strcID} have no {self.identifier_value}")
            self.strcID = ""
            self.isInstance = False
        else:
            self.isInstance = True
    def add_symbol_table(self):
        if self.error_flag:
            self.error_flag = False
            return
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
            filtered_entry = {
                key: value for key, value in entry.items() 
                if value != "" and not (isinstance(value, dict) and all(v == "" for v in value.values()))
            }
            
            print(filtered_entry)
    
    #Operator
    def checkIfLogicalOperand(self):
        
        self.error_message("")
        
    #Nonterminal check
    def semantic_nonterminal(self, top):
        if top == "<type_conversion>":
            self.is_typeconversion = True
        else:
            self.top = top
    
    def checkParameter(self):
        print()
    
    def checkArgs(self):
        print()
        
    
