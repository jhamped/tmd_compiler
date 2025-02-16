from definitions import *

def semantic():
    add_all_set()
    stack = ["<program>"]  # Initialize stack with start symbol and end marker
    current_token_index = 0
    def get_lookahead():
        curr_token = token[current_token_index]
        if current_token_index < len(token):
            if curr_token.startswith("id"):
                curr_token = "id"
            return curr_token
        else:
            None
    
    #NEW!
    symbol_table = []
    def add_symbol_table(datatype, identifier, literals):
        data = {
            "datatype": datatype,
            "identifier": identifier,
            "literals": literals
        }
        symbol_table.append(data)
        
    def printSymbolTable():
        for data in symbol_table:
            print(data)

       
    #END NEW!
    literal_value = "null"
    datatype_value = "null"
    try:
        while stack:
            top = stack.pop()
            lookahead = get_lookahead()
            if top == lookahead:
                print(f"lookahead {lookahead}")
                if lookahead in datatype:
                    datatype_value = lookahead
                    print(f"-Datatype: {datatype_value}")
                elif lookahead == "id":
                    id_value = token[current_token_index] 
                    print(f"-ID: {id_value} datatype: {datatype_value}")
                    #check if ID already declared
                    if datatype_value !="null":
                        if any(entry["identifier"] == id_value for entry in symbol_table):
                            raise Exception(f"SEMANTIC ERROR: Identifier {id_value} already declared")
                    elif datatype_value =="null":
                        if not any(entry["identifier"] == id_value for entry in symbol_table):
                            raise Exception(f"SEMANTIC ERROR: Identifier {id_value} not declared{ token[current_token_index]}")
                elif lookahead in literals:
                    literal_value = lookahead
                    print(f"-Literal: {literal_value}")
                    if datatype_value == "null":
                        for entry in symbol_table:
                            print(f"entry: {entry["identifier"]}")
                            if entry["identifier"] == id_value:
                                datatype_value = entry["datatype"] #makukuha datatype ng identifier nayon
                                print(F"Found {datatype_value}")
                    if datatype_value in valid_literals and literal_value in valid_literals[datatype_value]:
                        print("")
                    else:
                        raise Exception(f"{datatype_value} cannot be initialized as {literal_value}")
                elif lookahead == ",":
                    print("-Symbol: ,")
                    print(datatype_value)
                    if any(entry["identifier"] == id_value for entry in symbol_table):
                        for entry in symbol_table:
                            if entry["identifier"] == id_value:
                                entry["literals"] = literal_value
                    else: 
                        add_symbol_table(datatype_value, id_value, literal_value)
                    print("------------------------------------------------------------------")
                    print(f"Symbol Table Updated")
                    print("------------------------------------------------------------------")
                elif lookahead == ";":
                    print("-Symbol: ;")
                    if any(entry["identifier"] == id_value for entry in symbol_table):
                        for entry in symbol_table:
                            if entry["identifier"] == id_value:
                                entry["literals"] = literal_value
                    else: 
                        add_symbol_table(datatype_value, id_value, literal_value)
                    datatype_value = "null"
                    id_value = "null"
                    literal_value ="null"
                    print("------------------------------------------------------------------")
                    print(f"Symbol Table Updated")
                    print("------------------------------------------------------------------")
                print()
                # Terminal matches lookahead, consume the token
                current_token_index += 1
                
                
            elif top in parsing_table:
                # Non-terminal: use the parsing table
                rule = parsing_table[top].get(lookahead)
                if rule:
                    #print(f"Apply rule: {top} -> {' '.join(rule)}")
                    if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                        stack.extend(reversed(rule))
                else:
                    raise Exception(f"Syntax error: No rule for {top} with lookahead {lookahead}")

            else:
                raise Exception(f"Syntax error: Unexpected symbol {top}")
                break


        if stack or current_token_index < len(token):
            raise Exception("Input rejected: Syntax error.")
        else:
            print("Input accepted: Syntactically correct.")
    except Exception as e:
        print("------------------------------------------------------------------")
        print(e)
        print("------------------------------------------------------------------")
    print("------------------------------------------------------------------")
    printSymbolTable()
    print("------------------------------------------------------------------")
    """while stack:
        top = stack.pop()
        lookahead = get_lookahead()
        if top == lookahead:
            print(f"lookahead: {lookahead}")
            if lookahead in datatype:
                datatype_value = lookahead
            elif lookahead == "id":
                id_value = token[current_token_index] 
            elif lookahead in literals:
                literal_value = lookahead
            elif lookahead == ",":
                add_symbol_table(datatype_value, id_value, literal_value)
                print(f"Symbol Table Updated")
            elif lookahead == ";":
                add_symbol_table(datatype_value, id_value, literal_value)
                datatype_value = None
                print(f"Symbol Table Updated")
            #NEW smantic variable declaration
            if lookahead in datatype:
                datatype_value = lookahead
                
            elif lookahead == "id":
                id_value = token[current_token_index]
                print(f"Datatype: {datatype_value}")
                print(f"ID: {id_value}")
                #check if ID already declared
                if any(entry["identifier"] == id_value for entry in symbol_table):
                    print("-------------------------------------------------------")
                    print(f"SEMANTIC ERROR: Identifier {id_value} already declared")
                    print("-------------------------------------------------------")
                    break #nagsyntax error later problem
                else:
                    checklookahead = token[current_token_index+1]
                    if checklookahead == "=":
                        literal_value = token[current_token_index+2]
                        for entry in symbol_table:
                            if entry["identifier"] == identifier:
                                temp_datatype = entry[datatype] #makukuha datatype ng identifier nayon
                                if temp_datatype == "int" and literal_value != "int_lit":
                                    print("---------------------------------------------------------")
                                    print(f"{temp_datatype} cannot be initialized to {literal_value}")
                                    print("---------------------------------------------------------")
                                    break
                    else:
                        #if not initialized then null
                        literal_value = "null"
                    if datatype_value != "null":
                        add_symbol_table(datatype_value, id_value, literal_value)
                        print(f"Symbol Table Updated")
                    else:
                        print("-------------------------------------------------------")
                        print(f"SEMANTIC ERROR: Identifier {id_value} already declared")
                        print("-------------------------------------------------------")
            elif lookahead == ";":
                datatype_value = "null"
                print(f"---------Terminated---------")
                print()
                
            #NEW END
                
            # Terminal matches lookahead, consume the token
            current_token_index += 1
            
            
        elif top in parsing_table:
            # Non-terminal: use the parsing table
            rule = parsing_table[top].get(lookahead)
            if rule:
                #print(f"Apply rule: {top} -> {' '.join(rule)}")
                if rule != ["null"]:  # Push right-hand side of rule onto stack (in reverse)
                    stack.extend(reversed(rule))
            else:
                print(f"Syntax error: No rule for {top} with lookahead {lookahead}")
                break
        
        else:
            print(f"Syntax error: Unexpected symbol {top}")
            break


    if stack or current_token_index < len(token):
        print("Input rejected: Syntax error.")
    else:
        print("Input accepted: Syntactically correct.")
    printSymbolTable()"""
