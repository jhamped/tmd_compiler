from definitions import *

# Parsing table based on the provided grammar
parsing_table = {
    "<program>": {
        "segm": ["<global_dec>", "main", "{", "<statements>", "}"],
        "main": ["<global_dec>", "main", "{", "<statements>", "}"], 
        "str": ["<global_dec>", "main", "{", "<statements>", "}"],
        #(lahat ng nasa predict set)
    },
    "<global_dec>": {
        "segm": ["<segm>", "<global_dec>"],
        "main": ["null"],
        "str": ["<declaration_statement>", "<global_dec>"]
        #(lahat ng nasa predict set)
    },
    "<segm>": {
        "segm": ["segm", "id1", "(", "<parameter>", ")", "{", "<statements>", "}", "<segm>"],
        "null": ["null"]
    },
    "<declaration_statement>": {
				"str": ["<identifier_declaration>", "<declaration_statement>"],
				"main": ["null"]
				#(“const”, “var”, “int”, “dec”, “chr”, “bln”, “var”, “strc”)
    },
    "<identifier_declaration>": {
		    "str": ["<datatype>", "<iden_dec_tail>"],
		    #( “const”, “var”, “int”, “dec”, “chr”, “bln”, “var” )
    },
    "<datatype>": {
		    "str": ["str"]
    },
    "<iden_dec_tail>": {
		    "id1": ["<variable_declaration>"],
		    "[": ["<array_declaration>"]
    },
    "<variable_declaration>": {
		    "id1": ["id1", "<init_statement>", "<mul_init>", ";"]
    },
    "<init_statement>": {
		    ";": ["null"],
		    "=": ["<assignment_op>", "<value>"]
		    #( “;”, “,”, "+=", etc )
    },
    "<assignment_op>": {
		    "=": ["="]
    },
    "<value>": {
		    "str_lit": ["<text_format>"],
		    #(int_lit, dec_lit, true, false, id, int, dec, chr, str, bln, ++, --, (, none, str_lit, chr_lit)
    },
    "<text_format>": {
		    "str_lit": ["str_lit", "<concat_string>"]
    },
    "<concat_string>": {
		    ";": ["null"]
		    #(“;“, “)“, “&“, “,“)
    },
    "<mul_init>": {
		    ";": ["null"]
    },
    "<statements>": {
		    "disp": ["<other_statements>"],
		    "}": ["null"]
    },
    "<other_statements>": {
		    "disp": ["<output_statement>", "<statements>"]
    },
    "<output_statement>": {
		    "disp": ["disp", "(", "<output_value>", ")", ";"]
    },
    "<output_value>": {
		    "id1": ["<tail_operand>", "<more_output>"]
    },
    "<tail_operand>": {
		    "id1": ["<operand>", "<expression>"]
    },
    "<operand>": {
		    "id1": ["id1", "<id_tail>"]
    },
    "<id_tail>": {
		    ")": ["null"]
    },
    "<expression>": {
		    ")": ["null"]
    },
    "<more_output>": {
		    ")": ["null"]
    }
}

def parse():
    stack = ["$", "<program>"]  # Initialize stack with start symbol and end marker
    current_token_index = 0

    def get_lookahead():
        return token[current_token_index] if current_token_index < len(token) else None

    while stack:
        top = stack.pop()
        lookahead = get_lookahead()

        if top == lookahead:
            # Terminal matches lookahead, consume the token
            print(f"Match: {lookahead}")
            current_token_index += 1
        elif top in parsing_table:
            # Non-terminal: use the parsing table
            rule = parsing_table[top].get(lookahead)
            if rule:
                print(f"Apply rule: {top} -> {' '.join(rule)}")
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
