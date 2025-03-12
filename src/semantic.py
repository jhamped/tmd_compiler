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
                print(f"Apply rule: {top} -> {' '.join(rule)}")
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
        self.is_typeconversion = False
        self.isVariableDefinition = False
        
        self.is_struct = False
        #self.is_structIDDeclared = False
        self.strcID = ""
        self.isStructElementDec = False
        
        self.total_args = 0
        self.args_declared = False
        
        self.temporary_variable = ""
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
        
        #Nested Function Level
        if lookahead == "{" and not self.isVariableDefinition:
            self.level_value +=1
        elif lookahead in codeblocks:
            temp = self.parent
            self.parent = temp + str(self.level_value)
            self.parentStack.append(self.parent)
        elif lookahead == "}" and not self.isVariableDefinition:
            
            self.parentStack.pop()
            if self.parentStack:
                self.parent = self.parentStack[-1]
            print(self.parent)
        
        
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
        #elif lookahead in id_type : #constant and strc
        #    print("ID type")
        #    self.type_value = lookahead
        elif self.top == "<identifier_declaration>":
            self.handle_declaration()
        elif self.lookahead == "id" and not self.is_assignment : #Assignment and ID declaration
            self.handle_identifier()
        elif self.lookahead == "=" or self.is_assignment:
            self.handle_assignment()
        
        
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
                self.console.insert(tk.END, f"ELEMENT: {self.parent} {self.identifier_value} {self.datatype_value } \n")
                self.type = "strc element"
                self.hasIDBeenDeclared()
                self.add_symbol_table()
            elif self.lookahead == "id":
                self.type = "instance"
                self.hasStructTypeBeenDefined()
                self.hasInstanceIDBeenDeclared()
                self.add_symbol_table()
        elif self.lookahead == "}":
            self.isStructElementDec = False
        elif self.lookahead == ";" and not self.isStructElementDec:
            self.is_struct = False
            self.strcID = ""
            
            
        
            
    def handle_declaration(self):
        self.isVariableDefinition = True
        self.type_value = "identifier"
        print("Declaration")
        if self.lookahead in datatype:
            if self.is_typeconversion:
                self.datatype_conversion = self.lookahead
            else:
                self.datatype_value = self.lookahead
                self.variable_declaration = True
                if self.datatype_value == "var":
                    self.is_var = True
        elif self.datatype_value == "str" and self.lookahead == "&":
            self.is_string = True
        #Array
        elif self.lookahead == "[":
            self.is_array = True
            
        elif self.is_array:
            self.handle_array()
        #Initialization
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
        elif self.lookahead in literals:
            self.literal_value = self.lookahead
            if self.is_typeconversion:
                self.checkTypeConversion()
                self.is_typeconversion = False
                return
            if self.is_var:
                self.findVarKey()
                self.is_var = False
            self.checkLiterals()
        elif self.lookahead == "=":
            self.temporary_variable = self.identifier_value
            self.is_assignment = True
        elif self.lookahead == ",":
            self.is_assignment = False
            if self.temporary_variable != "":
                self.identifier_value = self.temporary_variable
            self.add_symbol_table()
        elif self.lookahead == ";":
            self.is_assignment = False
            if self.temporary_variable != "":
                self.identifier_value = self.temporary_variable
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
            self.is_assignment = True
            self.identifier_value = lexeme[self.current_token_index]
            if self.datatype_value == "":
                self.findDatatype()
            self.hasIDBeenDeclared() 
            
    def handle_assignment(self):
        print("assignment")
        self.isVariableDefinition = True
        if self.is_array:
            print("Assignment Array")
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
            self.clearValue()
            return
    
    
        
            
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
    
    #Finder
    def findDatatype(self):
        for entry in self.symbol_table:
            if entry["identifier"] == self.identifier_value:
                self.datatype_value = entry["datatype"] 
    def findLiterals(self):
        for entry in self.symbol_table:
            if entry["identifier"] == self.identifier_value:
                self.literal_value = entry["literals"] 
                return
        self.literal_value = "None"
    def findType(self):
        for entry in self.symbol_table:
            if entry["identifier"] == self.identifier_value:
                self.type_value = entry["type"] 
                return
            
    def findVarKey(self):
        for key, value in valid_literals.items():
            if value == self.literal_value:
                self.datatype_value = key
                break
    
    #Checker
    def hasStructIDBeenDeclared(self):
        identifier_exists = any(
            entry["identifier"].split("[")[0] == self.strcID and
            entry["level"]["parent"] == self.parent  # Same scope check
            for entry in self.symbol_table
        )

        if identifier_exists:
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
                entry["identifier"].split("[")[0] == self.identifier_value #Check if id exist
                for entry in self.symbol_table
            )

            if identifier_exists:
                self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared in the same scope")
        
        
        elif not self.is_assignment:
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
                self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")

        """if not self.is_assignment:
            if any(entry["identifier"].split("[")[0] == self.identifier_value and (entry["scope"] == self.scope_value or self.scope_value == "global") for entry in self.symbol_table):
                self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared")
        else: 
            if not any(entry["identifier"] == self.identifier_value and (entry["scope"] == self.scope_value or self.scope_value != "global") for entry in self.symbol_table):
                self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")"""
                
    def checkLiterals(self):
        identifier_exists = any(
                entry["identifier"].split("[")[0] == self.identifier_value and #Check if id exist
                entry["level"]["parent"] == self.parent #Check if same scope
                for entry in self.symbol_table
            )
        if not(self.datatype_value in valid_literals and self.literal_value in valid_literals[self.datatype_value]):
            #if not identifier_exists:
            #    self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")
            #else:
            self.error_message(f"{self.identifier_value} cannot be initialized as {self.literal_value}")
    
    def checkTypeConversion(self):
        if self.lookahead == "id":
            self.identifier_value = lexeme[self.current_token_index]
            self.console.insert(tk.END, f"{self.identifier_value}\n")
            self.findDatatype()
            self.findLiterals()
        print(f"----{self.literal_value}{self.lookahead}")
        if self.literal_value == "":
            self.error_message(f"Type Mismatch: None cannot be converted to {self.datatype_conversion}") 
            return
        if not(self.literal_value in valid_conversion[self.datatype_conversion]):
            self.error_message(f"Type Mismatch: {self.literal_value} cannot be converted to {self.datatype_conversion}") 
        elif self.datatype_conversion != self.datatype_value:\
            self.error_message(f"Type Mismatch: datatype conversion {self.datatype_conversion} cannot be assign to {self.datatype_value}") 
    
    
    #Nested Function
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
    
    def add_symbol_table(self):
        if self.error_flag:
            self.error_flag = False
            return
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
        
    
