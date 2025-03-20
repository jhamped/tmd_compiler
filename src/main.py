from definitions import *
import tkinter as tk

# Parsing table based on the provided grammar
def semantic(console):  
    if errorflag[0] == True:  
        return
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
        self.argsData = {}
        self.parentStack = ["global"]
        self.console = console
        self.statement = ""
        self.current_token_index = 0
        self.lookahead = ""
        self.top = ""
        
        self.isBoolean = False
        self.isPassed = False
        
        self.variable_name = ""
        self.is_var =False
        self.is_typeconversion = False
        self.datatype_conversion = ""
        self.isID = False
        self.isProcessing = False
        self.id_type = ""
        #Array
        self.isArray = False
        self.array_id = ""
        self.row = 0
        self.column = 0
        #Segments
        self.segmentID = ""
        self.is_return = False
        self.temp_literal = ""
        self.tempint = 0
        self.functionID = ""
        #Variable for symbol table
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.scope_value = "global"
        self.type_value = ""
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
        
    def clearValue(self):
        pass
        
    def clearAll(self):
        pass
        
    def semantic_process(self, lookahead, current_token_index):
        self.current_token_index = current_token_index
        self.lookahead = lookahead
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
            self.clearIdentifier()
            self.top = temp_top
            self.parent = temp2
        elif lookahead == "}" and self.top != "<identifier_declaration>" and not self.statement != "structure":
            self.parentStack.pop()
            if self.parentStack:
                self.parent = self.parentStack[-1]
            print(f"pop: {self.parent}")
        
        if self.lookahead == "const":
            self.type_value = "const"
        elif lookahead == "main":
            self.handle_main()
        elif self.lookahead == "segm":
            self.statement = "segm"
        elif self.lookahead == "ret" or self.is_return:
            self.handle_return()
        
        #Handle Identifier
        if self.lookahead == "id" or self.isID:
            print("handle_id")
            self.variable_name = lexeme[self.current_token_index]
        
        #Statement Semantic
        if self.statement == "segm":
            self.handle_segment_declaration()
        elif self.statement == "parameter":
            self.handle_parameter()
        elif self.top == "<identifier_declaration>" or self.statement == "identifier_declaration":
            self.handle_declaration()
        elif self.top == "<assignment_statements>" or self.statement == "assignment":
            self.handle_assignment()
        elif lookahead == "strc":
            self.type_value = lookahead
            self.statement = "structure"
        elif self.top == "<foreach_statement>" or self.statement == "foreach_statement":
            self.handle_foreachstatement()
        elif self.top == "<initialization>" or self.statement == "<initialization>":
            self.handle_initialization()
        elif self.lookahead == "id" or self.statement == "identifier":
            self.handle_identifier()
        #Check operator
        if self.lookahead in assignment_number:
            self.checkAssignmentOperator()
        if self.lookahead in arithmetic_operator:
            self.checkOperand()
        elif lexeme[self.current_token_index] == "~0":
            self.error_message("Invalid negative value")
        elif self.lookahead in {"++", "--"}:
            print(f"Unary")
            self.checkUnary()
    def clearIdentifier(self):
        self.datatype_value = ""
        self.identifier_value = ""
        self.type_value = ""
        self.is_var = False
        self.statement = ""
        self.top = ""
        self.isArray = False
        self.segmentID = ""
        self.isPassed = False
        self.isBoolean = False
    
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
        self.clearIdentifier()
   
                
    def handle_declaration(self):
        print("Declaration")
        self.statement = "identifier_declaration"
        
        if self.id_type != "": #Handle Array and Function Call
            self.processIDType()
            
        if self.is_typeconversion:
            self.handle_typeconversion()
            return
        elif self.lookahead == "[" or self.isArray:
            self.isArray = True
            self.handle_array()
            return
        elif self.lookahead in datatype:
            self.datatype_value = self.lookahead
            if self.datatype_value == "var":
                self.is_var = True
        elif self.lookahead == "id":
            self.handle_identifierType()
            
            if self.identifier_value == "":
                self.identifier_value = self.variable_name
                self.checkIfIDAlreadyDeclared(self.variable_name)
            elif self.datatype_value == "bln":
                if not self.isBoolean:
                    self.isPassed = self.checkIfBooleanValue()
                    self.isBoolean = True
                return
            else:
                self.processVar(self.lookahead)
                self.check_identifier()
        elif self.lookahead in literals:
            if self.datatype_value == "bln":
                if not self.isBoolean:
                    self.isPassed = self.checkIfBooleanValue()
                    self.isBoolean = True
                return
            self.processVar(self.lookahead)
            self.checkIfAssignmentIsValid(self.lookahead)
        elif self.lookahead == ",":
            if self.datatype_value == "bln":
                if not self.isPassed:
                    print(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
                    self.error_message(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
                else:
                    self.add_symbol_table()
                    self.clearIdentifier()
            self.add_symbol_table()
            if self.is_var:
                self.datatype_value = "var"
            self.identifier_value = ""
        elif self.lookahead == ";":
            if self.datatype_value == "bln":
                if not self.isPassed:
                    print(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
                    self.error_message(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
                else:
                    print(f"TANGINAAA {self.identifier_value}/{self.variable_name}")
                    self.add_symbol_table()
                    self.clearIdentifier()
            self.add_symbol_table()
            self.clearIdentifier()
    
    def handle_assignment(self):
        print(f"Assignment")
        self.statement = "assignment"
        
        if self.id_type != "null": #Handle Array and Function Call
            self.processIDType() 
            
        if self.identifier_value == "": #get assignment variable #leftest
            self.identifier_value = self.variable_name
            self.datatype_value = self.getDatatype(self.variable_name)
            self.handle_identifierType()
            if self.id_type == "array":
                return
            if self.getType(self.variable_name) == "const":
                self.error_message(f"Constant '{self.variable_name}' cannot be assigned a new value")
            if self.datatype_value == "var":
                self.is_var = True
            self.checkIfIDNotDeclared(self.variable_name)
         
        elif self.is_typeconversion:
            self.handle_typeconversion()
            return
        elif self.lookahead == "id":
            self.handle_identifierType()
            if self.datatype_value == "bln":
                if not self.isBoolean:
                    self.isPassed = self.checkIfBooleanValue()
                    self.isBoolean = True
            if self.is_var:
                self.processVar(self.lookahead)
                self.updateDatatype(self.identifier_value, self.datatype_value)
            self.check_identifier()
        elif self.lookahead in literals:
            if self.datatype_value == "bln":
                if not self.isBoolean:
                    self.isPassed = self.checkIfBooleanValue()
                    self.isBoolean = True
            if not self.isBoolean and self.datatype_value == "bln":
                self.isPassed = self.checkIfBooleanValue()
                self.isBoolean = True
            if self.is_var:
                self.processVar(self.lookahead)
                self.updateDatatype(self.identifier_value, self.datatype_value)
            self.checkIfAssignmentIsValid(self.lookahead)
        elif self.lookahead == ",":
            if self.datatype_value == "bln":
                if not self.isPassed:
                    print(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
                    self.error_message(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
            self.identifier_value == ""
        elif self.lookahead == ";":
            if self.datatype_value == "bln":
                if not self.isPassed:
                    print(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
                    self.error_message(f"{self.variable_name} must be initialized with an expression that evaluates to a boolean value.")
            self.clearIdentifier()
    
    def handle_identifierType(self):
        type = self.getType(self.variable_name)
        dimension = self.getDimension(self.variable_name)
        print(f"handle identifier {type}/{dimension}")
        if dimension in {"1", "2"}:
            self.id_type = "array"
            return
        elif type == "segm":
            self.id_type = "function_call"
            return
    
    def handle_typeconversion(self):
        if self.lookahead in datatype:
            self.datatype_conversion = self.lookahead
        elif self.lookahead in literals or self.lookahead == "id":
            self.checkTypeConversion(self.lookahead)
            self.is_typeconversion = False
    
    def handle_array(self):
        print("ARRAY==")
        if self.lookahead in literals:
            self.checkIfAssignmentIsValid(self.lookahead)
            self.processArrayValue()
        elif self.lookahead == "id":
            identifier = lexeme[self.current_token_index]
            self.array_id = identifier
            self.checkIfIDAlreadyDeclared(identifier)
        elif self.lookahead == "}" and self.dimension_value == "2":
            self.processArrayValueEnd()
        elif self.lookahead == "," and self.dimension_value != "":
            self.add_symbol_table()
        elif self.lookahead == ";":
            print(f"-------{self.identifier_value}")
            #self.processArrayValue()
            if self.identifier_value == "":
                self.identifier_value =  f"{self.array_id}[0]"
            print(f"1-------{self.identifier_value}")
            self.add_symbol_table()
            self.clearIdentifier()
            return
        else: #Get array dimension
            self.handle_array_dimension()
        
    def handle_array_dimension(self):
        print("Array Dimension")
        if self.lookahead == "]":
            self.dimension_value = "1"
        elif self.lookahead == ",":
            self.dimension_value = "2"
           
    def handle_segment_declaration(self):
        print(f"Handle segment declaration")
        
        if self.lookahead == "id":
            identifier = self.variable_name
            self.identifier_value  = identifier
            self.type_value = "segm"
            self.checkIfIDAlreadyDeclared(identifier)
            self.add_symbol_table() 
            self.parentStack.append(identifier)
            self.parent = identifier 
            self.clearIdentifier()
            self.segmentID = identifier
            self.statement = "parameter"
    
    def handle_parameter(self):
        print(f"Handle Parameter {self.segmentID}")
        if self.lookahead in datatype:
            self.datatype_value = self.lookahead
        elif self.lookahead == "id":
            self.identifier_value = self.variable_name
            self.checkIfIDAlreadyDeclared(self.variable_name)
        elif self.lookahead == ",":
            self.update_param_symbol(self.segmentID)
        elif self.lookahead == ")":
            self.update_param_symbol(self.segmentID)
            self.clearIdentifier()
    
    def handle_return(self):
        self.is_return = True
        if self.parent == "main":
            self.error_message("Illegal Return Statement")
            self.is_return = False
            return
        if self.lookahead in literals:
            literal_value = self.lookahead
            self.retCheckValue(literal_value)
                
        elif self.lookahead == "id":
            
            datatype = self.getDatatype(self.variable_name)
            literal_value = self.getLiteralTypeconversion(datatype)
            print(f"---return id {datatype}/{self.variable_name}/{literal_value} ")
            self.retCheckValue(literal_value)
        elif self.lookahead == ";":
            datatype_value = reverse_literal_types.get(self.temp_literal, "")
            print(f"returning {self.parent} {datatype_value} {self.temp_literal}")
            self.updateDatatype(self.parent,datatype_value)
            self.is_return = False
    def retCheckValue(self, literal_value):
        if self.temp_literal == "":
            self.temp_literal = literal_value
        else:
            if self.temp_literal != literal_value:
                self.error_message("Incompatible expression when returning")
            self.temp_literal = literal_value
    
    def handleFunctionCall(self):
        print(f"function call {self.lookahead}/{self.functionID}/{self.variable_name}")
        if self.functionID == "":
            self.functionID = self.variable_name
            return
        elif self.lookahead == "id":
            identifier = lexeme[self.current_token_index]
            datatype_value = self.getDatatype(identifier)
            argsCompatible = any(
                entry["Segment ID"] == self.functionID and
                entry["args"][self.tempint]["datatype"] == datatype_value
                for entry in self.parameterList
            )
            if not argsCompatible:
                print(f"Arguments incompatible")
                self.error_message(f"Arguments incompatible")
            return
        elif self.lookahead in literals:
            datatype_value = self.getDatatypeOnLiterals(self.lookahead)
            print(f"datatype {datatype_value}, segment {self.segmentID}")
            argsCompatible = any(
                entry["Segment ID"] == self.functionID and
                entry["args"][self.tempint]["datatype"] == datatype_value
                for entry in self.parameterList
            )
            if not argsCompatible:
                print(f"Arguments incompatible")
                self.error_message(f"Arguments incompatible")
            return
        elif self.lookahead == ",":
            self.tempint += 1
        elif self.lookahead == ")":
            self.tempint = 0
            self.id_type = ""
            self.isProcessing = False
            self.isID = False
            
        else:
            return

    def handle_foreachstatement(self):
        print(f"Foreach statement {self.identifier_value}")
        self.statement = "foreach_statement"
        if self.lookahead in datatype:
            if self.is_typeconversion:
                self.datatype_conversion = self.lookahead
            else:
                self.datatype_value = self.lookahead
                self.variable_declaration = True
                if self.datatype_value == "var":
                    self.is_var = True
        elif self.lookahead == "id" and self.identifier_value == "":
            self.identifier_value = self.variable_name
            if self.datatype_value == "":
                self.checkIfIDNotDeclared(self.identifier_value)
            else:
                self.checkIfIDAlreadyDeclared(self.identifier_value)
                self.add_symbol_table()
        elif self.lookahead == "id":
            self.variable_name = lexeme[self.current_token_index]
            self.checkIfIDNotDeclared(self.variable_name)
            dimension = self.getDimension(self.variable_name)
            datatype_value = self.getDatatype(self.variable_name)
            if dimension not in {"1", "2"} and datatype_value != "str":
                self.error_message(f"The foreach statement cannot operate on {self.variable_name}. Expected an array or a string.")
            self.clearIdentifier()
    
    def handle_initialization(self):
        if self.lookahead in datatype:
            if self.is_typeconversion:
                self.datatype_conversion = self.lookahead
            else:
                self.datatype_value = self.lookahead
                self.variable_declaration = True
                if self.datatype_value == "var":
                    self.is_var = True
        elif self.lookahead == "id" and self.identifier_value == "":
            self.identifier_value = self.variable_name
            if self.datatype_value == "":
                self.checkIfIDNotDeclared(self.identifier_value)
            else:
                self.checkIfIDAlreadyDeclared(self.identifier_value)
                self.add_symbol_table()
            self.clearIdentifier()
    
    def handle_identifier(self):
        self.statement = "identifier"
        self.handle_identifierType()
        
        if self.id_type != "": #Handle Array and Function Call
            self.processIDType()
        elif self.id_type == "":
            self.statement = ""
            self.checkIfIDNotDeclared(self.variable_name)
    #Processing
    def processIDType(self):
        print(f"Process ID Type")
        if self.id_type == "array":
            self.process_array()
        elif self.id_type == "function_call":
            self.handleFunctionCall()
        
    
    def processVar(self, lookahead):
        if self.is_var:
            if lookahead in literals:
                self.datatype_value = self.getDatatypeOnLiterals(self.lookahead)
                print(f"process var {self.datatype_value}")
            elif lookahead == "id":
                identifier = lexeme[self.current_token_index]
                self.checkIfIDNotDeclared(identifier)
                self.datatype_value = self.getDatatype(identifier)
            
    def processArrayValue(self):
        if self.dimension_value == "1":
            self.identifier_value = f"{self.array_id}[{self.row}]"
            self.row += 1
        elif self.dimension_value == "2":
            self.identifier_value = f"{self.array_id}[{self.column},{self.row}]"
            self.row += 1
    def processArrayValueEnd(self):
        if self.dimension_value == "2":
            self.column+=1
            return
        self.row = 0
        self.column = 0
        
    def process_array(self):
        print("Processing Array")
        if self.lookahead == "[":
            self.variable_name = f"{self.variable_name}["
            return
        elif self.lookahead == "id" and "[" in self.variable_name:
            identifier = lexeme[self.current_token_index]
            self.checkIfIDNotDeclared(identifier)
            self.variable_name = f"{self.variable_name}0"
            return
        elif self.lookahead in literals:     
            index = lexeme[self.current_token_index]
            self.variable_name = f"{self.variable_name}{index}"
            return
        elif self.lookahead == ",":
            self.variable_name = f"{self.variable_name},"
            return
        elif self.lookahead == "]":
            self.variable_name = f"{self.variable_name}]"
            self.checkIfIDNotDeclared(self.variable_name)
            
            self.isID = False
            self.id_type = ""
            self.isProcessing = False
            print(f"Array done {self.variable_name}")
        else:
            return
    
    def updateDatatype(self, identifier, new_datatype):
        for entry in self.symbol_table:
            if entry["identifier"] == identifier:
                entry["datatype"] = new_datatype
                break
    #Checker       
    def check_identifier(self):
        IDdatatype = self.getDatatype(self.variable_name)
        self.checkIfIDNotDeclared(self.variable_name)
        self.checkIfAssignmentIsValid(IDdatatype)
    
    def checkIfAssignmentIsValid(self, lookahead):
        Expected = self.getLiterals(self.datatype_value)
        Found = self.getLiterals(lookahead)
        print(f"Assignment Valid: {lookahead}, {self.datatype_value}")
        if Expected != Found:
            if Expected == "decimal number" and Found == "integer":
                pass
            else:
                self.error_message(f"Assignment type mismatch. Expected {Expected} but found {Found}.")
            
    def checkIfIDAlreadyDeclared(self, id):
        identifier_exists = any(
            entry["identifier"].split("[")[0]== id and #Check if id exist
            entry["level"]["parent"] == self.parent #Check if same scope
            for entry in self.symbol_table
        )

        if identifier_exists:
            self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared in the same scope")
    
    def checkIfIDNotDeclared(self, id):
        print(f"Check if id not declared {id}/{self.isDeclaredInParent(id, self.parent)}")
        identifier_not_found = not any(
            entry["identifier"] == id and #Check if id exist
            self.isDeclaredInParent(id, self.parent) #Check if id already declared in parent scope
            for entry in self.symbol_table
        )
        if identifier_not_found:
            print(f"Identifier {id} not declared")
            self.error_message(f"Identifier {id} not declared")
    
    def checkTypeConversion(self, type_value):
        if type_value == "id":
            print(f"Type conversion -> id")
            identifier = lexeme[self.current_token_index]
            datatype = self.getDatatype(identifier)
            literal_value = self.getLiteralTypeconversion(datatype)
        elif type_value in literals:
            literal_value = type_value
            
        if literal_value == "":
            self.error_message(f"Type Mismatch: None cannot be converted to {self.datatype_conversion}") 
            return
        if not(literal_value in valid_conversion[self.datatype_conversion]):
            self.error_message(f"Type Mismatch: {lexeme[self.current_token_index]} cannot be converted to {self.datatype_conversion}") 
        elif self.datatype_conversion != self.datatype_value:
            print(f"Type Mismatch: datatype conversion {self.datatype_conversion} cannot be assign to {self.identifier_value}. ") 
            self.error_message(f"Type Mismatch: datatype conversion {self.datatype_conversion} cannot be assign to {self.identifier_value}.") 
            
    def checkUnary(self):
        print(f"Unary: {self.current_token_index < len(token) and self.current_token_index > 0}")
        if self.current_token_index < len(token) and self.current_token_index > 0:
            print(f"{token[self.current_token_index-1]}/{token[self.current_token_index+1]}")
            if token[self.current_token_index-1].startswith("id"): #Check if pre unary
                print(f"unary -> preunary")
                unary_id = lexeme[self.current_token_index-1]
                type = self.getType(unary_id)
                datatype = self.getDatatype(unary_id)
                if type == "const":
                    self.error_message("Constant cannot be used in unary statement")
                    return
                if not datatype in {"dec","int","var"}:
                    self.error_message(f"Unary operators (++, --) only apply to numeric type")
                    return
            elif token[self.current_token_index + 1].startswith("id"): #check if post unary
                print(f"unary -> postunary")
                unary_id = lexeme[self.current_token_index+1]
                type = self.getType(unary_id)
                datatype = self.getDatatype(unary_id)
                if type == "const":
                    self.error_message("Constant cannot be used in unary statement")
                    return
                if not datatype in {"dec","int","var"}:
                    self.error_message(f"Unary operators (++, --) only apply to numeric type")
                    return
        else:
            return
    
    def checkIfBooleanValue(self):
        print("checkBooleanValue")
        temporary_index = self.current_token_index
        if temporary_index < len(token) and temporary_index > 0:
            temp_token = token[temporary_index]
            while temp_token not in {";", ","}:
                temp_token = token[temporary_index]
                if temp_token.startswith("id"):
                    id = lexeme[temporary_index]
                    temp = self.getLiteralTypeconversion(id)
                    if temp in {"true", "false"}:
                        print(f"checkifBoolean -> True id")
                        if self.checkBooleanLiteral():
                            return True
                        else:
                            return False
                elif temp_token in booleanValue:
                    print(f"checkifBoolean -> True temp_token")
                    if self.checkBooleanLiteral():
                        return True
                    else:
                        return False
                temporary_index +=1
    def checkBooleanLiteral(self):
        print(f"checkBooleanLiteral")
        temporary_index = self.current_token_index
        if temporary_index < len(token) and temporary_index > 0:
            temp_token = token[temporary_index]
            Literal = ""
            prevLiteral = ""
            while temp_token not in {";", ","}:
                temp_token = token[temporary_index]
                
                if temp_token in literals:
                    prevLiteral = Literal
                    Literal = temp_token
                    if prevLiteral == "" or prevLiteral == None:
                        prevLiteral = Literal
                elif temp_token.startswith("id"):
                    id = lexeme[temporary_index]
                    prevLiteral = Literal
                    Literal = self.getLiteralTypeconversion(id)
                    if prevLiteral == "":
                        prevLiteral = Literal
                if prevLiteral != Literal:
                    print(f"{prevLiteral}/{Literal}")
                    if {prevLiteral, Literal} == {"int_lit", "dec_lit"}:
                        pass
                    elif prevLiteral != Literal:
                        self.error_message(f"Logical Operator cannot be applied to different datatype.")
                        return
                temporary_index += 1
            return True
    #Operator Checker
    def checkAssignmentOperator(self):
        datatype = self.getDatatype(self.identifier_value)
        if datatype not in {"int", "dec", "var"}:
            self.error_message(f"Compound Assignment is only allowed for number identifier. ")
    
    def checkOperand(self):
        print("checking operand")
        #Semantic For Zero Value
        prev = next = nextLexeme = prev4 = ""
        if self.current_token_index < len(token) and self.current_token_index > 0:
            prev = token[self.current_token_index-1]
            next = token [self.current_token_index+1]
            nextLexeme = lexeme[self.current_token_index+1]
            if self.current_token_index > 4:
                prev4 = token[self.current_token_index-4]
        if nextLexeme == "0":
            print("0")
            if self.lookahead == "/":
                self.error_message(f"Division by Zero is not allowed")
            elif self.lookahead == "%":
                self.error_message(f"Modulo by Zero is not allowed")
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
        if self.lookahead in arithmetic_operator:
            if next in {"str_lit", "chr_lit", "true", "false"}:
                self.error_message(f"Use of arithmetic operation '{self.lookahead}' is not valid for {next}. Use proper type conversion")
            elif prev in {"str_lit", "chr_lit", "true", "false"}:
                self.error_message(f"Use of arithmetic operation '{self.lookahead}' is not valid for {prev}. Use proper type conversion")
            elif prev4 in {"str", "chr", "bln"}:
                self.error_message(f"Use of arithmetic operation '{self.lookahead}' is not valid for type conversion {prev4}. Use proper type conversion")
            elif next in {"str", "chr", "bln"}:
                self.error_message(f"Use of arithmetic operation '{self.lookahead}' is not valid for type conversion {next} . Use proper type conversion")
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
    
    #Getter
    def getNextLookahead(self):
        if self.current_token_index < len(token) and self.current_token_index > 0:
            return token[self.current_token_index+1]
        else:
            return
        
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
        
    #TABLE
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
    def update_param_symbol(self, segmentID):
        segment_id = segmentID
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
    

    #Nonterminal check
    def semantic_nonterminal(self, top):
        if top == "<type_conversion>":
            self.is_typeconversion = True
        else:
            self.top = top
    
    
