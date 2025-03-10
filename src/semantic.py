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
                semantic_checker.semantic_nonterminal(lookahead, current_token_index)
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
        self.console = console
        self.lookahead = ""
        self.error_flag = False
        self.variable_declaration = False
        self.assignment_declaration = False
        self.segment_declaration = False
        self.isArray = False
        self.type_conversion = False
        self.isBooleanValue =  0
        self.isLogical = False
        self.current_token_index = 0
        self.array_temp = ""
        self.datatype_temp = ""
        self.row = 0
        self.column = 0
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.scope_value = "global"
        self.type_value = ""
        self.dimension_value = ""
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
        self.variable_declaration = False
        self.assignment_declaration = False
        self.segment_declaration = False
        self.isArray = False
        self.type_conversion = False
        self.isBooleanValue =  0
        self.isLogical = False
        self.datatype_value = ""
        self.identifier_value = ""
        self.literal_value = ""
        self.type_value = ""
        self.dimension_value = ""
        self.datatype_conversion = ""
        
    def clearAll(self):
        self.__clearValue__
        self.scope_value = "global"
        self.type_value = ""
        self.dimension_value = ""
        
    def semantic_process(self, lookahead, current_token_index):
        self.current_token_index = current_token_index
        self.lookahead = lookahead
        
        #Scope
        if lookahead == "main":
            self.scope_value = lookahead
            print("main")
        elif lookahead == "segm":
            self.segment_declaration = True
            print("Semg")
        
        #Type
        elif lookahead in id_type:
            print("ID type")
            self.type_value = lookahead
        
        #Declaration and Assignment
        elif lookahead in datatype and not self.type_conversion:
            print("Declaration")
            if lookahead == "bln":
                print("Boolean")
                self.isBooleanValue =  True
            self.variable_declaration = True
            self.datatype_temp = self.datatype_value
            self.datatype_value = lookahead
        elif lookahead == "id" and not self.type_conversion:
            print("Lookahead is ID")
            self.identifier_value = token[self.current_token_index]
            if self.isArray:
                print("Assignment Array")
                self.array_temp = self.identifier_value
            if self.segment_declaration:
                print("Assignment segment")
                self.scope_value = self.identifier_value
            else:
                self.assignment_declaration = True
                self.hasIDBeenDeclared()
        elif lookahead in literals and self.assignment_declaration:
            print("Literals")
            self.literal_value = lookahead
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
        elif lookahead == "const":
            self.type_value = "const"
        
        #Array
        elif lookahead == "[" and self.variable_declaration:
            print("Array")
            self.isArray = True
        elif self.isArray and self.dimension_value == "":
            print("Array Dimension")
            if lookahead == "]":
                self.dimension_value = "1"
            elif lookahead == ",":
                self.dimension_value = "2"
        elif lookahead == "}":
            print("Array end")
            if self.dimension_value == "2":
                self.column+=1
                return
            self.row = 0
            self.column = 0
        
        #Updating Symbol Table
        elif lookahead == "," and self.assignment_declaration:
            print("Update Symbol ,")
            self.add_symbol_table()
        elif lookahead == ";":
            print("Update Symbol ;")
            if self.isLogical:
                self.checkIfLogicalOperand()
            else:
                self.add_symbol_table()
            self.clearValue()
        
        #Type conversion
        elif self.variable_declaration and lookahead == "(":
            print("Type Conversion")
            self.type_conversion = True
            self.datatype_conversion = self.datatype_value
            self.datatype_value = self.datatype_temp
            self.variable_declaration = False
        elif self.type_conversion:
            print("Type Conversion Check")
            if self.lookahead == "id":
                self.identifier_value = token[self.current_token_index]
            self.checkTypeConversion()
            self.type_conversion = False
        
        #Operation
        elif self.lookahead in relational_operator + bool_lit:
            if self.isLogical and self.isBooleanValue:
                self.isBooleanValue = 2
            else:
                self.isBooleanValue =  1
            
        elif self.lookahead in semantic_logical:
            self.isLogical = True
            
    def hasIDBeenDeclared(self):
        if self.variable_declaration:
            if any(entry["identifier"] == self.identifier_value and (entry["scope"] == self.scope_value or self.scope_value == "global") for entry in self.symbol_table):
                self.error_message(f"Identifier {lexeme[self.current_token_index]} already declared")
        elif self.assignment_declaration:
            if not any(entry["identifier"] == self.identifier_value and (entry["scope"] == self.scope_value or self.scope_value != "global") for entry in self.symbol_table):
                self.error_message(f"Identifier {lexeme[self.current_token_index]} not declared")
    
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

    def checkLiterals(self):
        if self.datatype_value == "":
            self.findDatatype()
        if not(self.datatype_value in valid_literals and self.literal_value in valid_literals[self.datatype_value]):
            self.error_message(f"{self.datatype_value} cannot be initialized as {self.literal_value}")
    
    def checkTypeConversion(self):
        if self.lookahead == "id":
            self.findDatatype()
            self.findLiterals()
            
        if not(self.literal_value in valid_conversion[self.datatype_conversion]):
            self.error_message(f"Type Mismatch: {self.literal_value} cannot be converted to {self.datatype_conversion}") 
        elif self.datatype_conversion != self.datatype_value:\
            self.error_message(f"Type Mismatch: datatype conversion {self.datatype_conversion} cannot be assign to {self.datatype_value}") 
    def processArray(self):
        if self.dimension_value == "1":
            self.identifier_value = f"{self.array_temp}[{self.row}]"
            self.row += 1
        elif self.dimension_value == "2":
            self.identifier_value = f"{self.array_temp}[{self.column},{self.row}]"
            self.row += 1
    
    def add_symbol_table(self):
        if self.error_flag:
            self.error_flag = False
            return
        data = {
            "datatype": self.datatype_value,
            "identifier": self.identifier_value,
            "literals": self.literal_value,
            "scope": self.scope_value,
            "type": self.type_value,
            "dimension": self.dimension_value
        }
        self.symbol_table.append(data)
        
    def printSymbolTable(self):
        for entry in self.symbol_table:
            print(entry)
    
    #Operator
    def checkIfLogicalOperand(self):
        
        self.error_message("")
        
    #Nonterminal check
    def semantic_nonterminal(self, lookahead, current_token_index):
        self.lookahead = lookahead
        if lookahead == "<parameter>":
            self.checkParameter()
        elif lookahead == "<args>":
            self.checkArgs()
    
    def checkParameter(self):
        print()
    
    def checkArgs(self):
        print()
        
    
