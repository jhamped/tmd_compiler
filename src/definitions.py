import string

state = []
lexeme = []
token = []
idens = []

arithmetic_operator = ['+', '-', '*', '/', '%']
relational_operator = ['==', '!=', '<', '<=', '>', '>=']
logical_operator = ['&', '|', '!']
unary_operator = ['+', '-']
assignment_operator = ['=', '+=', '-=', '*=', '/=', '%=']
number_operator = arithmetic_operator + relational_operator + logical_operator + unary_operator
all_operators = number_operator + assignment_operator

punc_symbols = ['=', '+', '-', '*', '/', '%', '&', '|', '!', '<', '>', '[', ']', '{', '}', '(', ')', ',', ';', ':', '#', '~', '.', '@', '$', '^', '_', '?', '\\']
quote_symbols = ["'", '"']

alpha = list(string.ascii_letters)
digit = list(string.digits)
alphanumeric = list(string.ascii_letters + string.digits)
ascii_def = alphanumeric + punc_symbols + quote_symbols
identifier = alphanumeric + ['_']

# Regular expression
keywords = ['strc', 'segm', 'main', 'bln', 'chr', 'int', 'dec', 'str', 'var', 'const', 'true', 'false', 'disp', 'insp', 'if', 
            'elif', 'else', 'switch', 'key', 'def', 'for', 'foreach', 'in', 'do', 'while', 'brk', 'rsm', 'exit', 'ret', 'none']

whitespace = [' ', '\t', '\n']

# Delimiters
key1_delims = {
    'state_delim' : whitespace + ['('], 
    'block_delim' : whitespace + ['{'],    
    'def_delim' : whitespace + [':'],
    'comma_delim' : whitespace + [']', '(', '{', '"', '\'', '+', '-', '.', '~'] + alphanumeric,
    'iden_delim' : whitespace + all_operators + ['<', '>', '=', ';', '&', '>', '(', ')', '[', ']', '{', '}', '.', ','],
    'lit_delim' : whitespace + [';', ',', '&', ')', '}', '!', '=', '|', ':'],
    'op_delim' : whitespace + alphanumeric + ['(', '~', '.', '+', '-'],
    'unary_delim' : whitespace + alphanumeric + number_operator + ['(', ')', ';', ',', '~'],
    'paren_delim' : whitespace + alphanumeric + [';', '!', '#', "'", '"', '(', ')', '+', '-', '.', '~'],
    'paren1_delim' : whitespace + arithmetic_operator + relational_operator + ['=', '&', '|', '{', ')', ';', ','],
    'brace_delim' : whitespace + alphanumeric + [';', '(', "'", '"', '{', '}', '+', '-', '.', '~'],
    'semicolon_delim' : whitespace + alphanumeric + ['~', '(', '}', '+', '-', None],
    'bracket_delim' : whitespace + alphanumeric + [']', ',', '+', '-', '.'],
    'bracket1_delim' : whitespace + number_operator + [')', '=', ';', '&'],
    'concat_delim' : whitespace + alpha + ['(', '"', "'", '#'],
    'data_delim' : whitespace + ['[', '('],
    'val_delim' : whitespace + [';', ',', ')', '}', '!', '&', '=', '|'],
    'colon_delim' : whitespace + alphanumeric + ['(', '+', '-'],
    'jmp_delim' : whitespace + [';'],
    'key_delim' : whitespace + alphanumeric + ["'", '"', '~', '(', '.'],
    'num_delim' : whitespace + all_operators + [':', ';', ')', '}', ']', ','],
}

key2_delims = {
    'relate_delim' : key1_delims['op_delim'] + ['!', "'", '"'],
    'relate1_delim' : key1_delims['op_delim'] + ['!'],
    'brace1_delim' : key1_delims['semicolon_delim'] + unary_operator + [';', ',']
}

key3_delims = {
    'asn_delim' : key2_delims['relate_delim'] + ['{', '#', '.']
}

key_delims = key1_delims | key2_delims | key3_delims


#-------------------------------------Parsing Table-----------------------------------------

parsing_table = {
    "<program>": {},
    "<global_dec>": {"main": [], "segm": ["<segm>", "<global_dec>"]},
    "<segm>": {"segm": ["segm", "id", "(", "<parameter>", ")", "{", "<statements>", "}", "<segm>"]},
    "<parameter>": {")": []},
    "<mul_parameter>": {")": [], ",": [",", "<vartype>", "id", "<mul_parameter>"]},
    "<declaration_statement>": {"strc": ["<struct_declaration>", "<declaration_statement>"]},
    "<identifier_declaration>": {"var": ["var", "<variable_declaration>"], "const": ["const", "<const_dec_tail>"]},
    "<iden_dec_tail>": {"id": ["<variable_declaration>"], "[": ["<array_declaration>"]},
    "<const_dec_tail>": {"var": ["var", "<const_declaration>"]},
    "<const_dec_in>": {"id": ["<const_declration>"], "[": ["<array_declaraton>"]},
    "<variable_declaration>": {"id": ["id", "<init_statement>", "<mul_init>", ";"]},
    "<const_declaration>": {"id": ["id", "=", "<value>", "<cons_mul>", ";"]},
    "<init_statement>": {},
    "<mul_init>": {";": [], ",": [",", "id", "<init_statement>", "<mul_init>"]},
    "<cons_mul>": {";": [], ",": [",", "id", "=", "<value>", "<mul_init>"]},
    "<value>": {"(": ["(", "<value>", ")", "<expression>"], "none": ["none"]},
    "<array_declaration>": {"[": ["[", "<array_dimension>", ";"]},
    "<array_dimension>": {"]": ["]", "id", "<array_init>"], ",": [",", "]", "id", "<two_array_init>"]},
    "<array_init>": {";": [], "=": ["=", "{", "<array_elements>", "<more_lit>}"]},
    "<more_lit>": {"}": [], ",": [",", "<array_elements>", "<more_lit>"]},
    "<two_array_init>": {";": [], "=": ["=", "{", "{", "<array_elements>", "<more_lit>", "}", "<two_more_lit>", "}"]},
    "<two_more_lit>": {"}": [], ",": [",", "{", "<array_elements>", "<more_lit>", "}", "<two_more_lit>"]},
    "<array_elements>": {"none": ["none"]},
    "<struct_declaration>": {"strc": ["strc", "id", "<struct_declaration_tail>"]},
    "<struct_declaration_tail>": {"{": ["<struct_define>"]},
    "<struct_define>": {"{": ["{", "<members_declaration>", "<more_members>", "}", "<instance>", "<more_instance>", ";"]},
    "<members_declaration>": {},
    "<more_members>": {"}": []},
    "<instance>": {"id": ["id"]},
    "<more_instance>": {";": [], ",": [",", "id", "<more_instance>"]},
    "<instance_declaration>": {"id": ["<struct_id>", "<more_instance_declaration>", ";"]},
    "<more_instance_declaration>": {";": [], ",": [",", "<struct_id>", "<more_instance_declaration>"]},
    "<struct_id>": {"id": ["id", "<struct_id_tail>"]},
    "<struct_id_tail>": {"[": ["[", "<index>", "]"]}, 
    "<statements>": {"}": []},
    "<other_statements>": {"id": ["<assignment_statements>", "<statements>"], "disp": ["<output_statement>", "<statements>"],
        "insp": ["<input_statement>", "<statements>"], "ret": ["<return_statement>", "<statements>"], "exit": ["exit", ";", "<statements>"]},
    "<assignment_statement>": {"id": ["id", "<assignment_tail>", ";"]},
    "<assignment_tail>": {"(": ["(", "<args>", ")"]},
    "<assignment_id_tail>": {"[": ["[", "<index>", "]"], ".": [".", "id", "<id_array_tail>"]},
    "<more_assignment>": {";": [], ",": [",", "id", "<assignment_tail>"]},
    "<output_statement>": {"disp": ["disp", "(", "<output_value>", ")", ";"]},
    "<output_value>": {"none": ["none"]},
    "<more_output>": {")": [], "&": ["&", "<output_value>", "<more_output>"]},
    "<input_statement>": {"insp": ["insp", "(", "<id_holder>", ")", ";"]},
    "<id_holder>": {"id": ["id", "<hold_id_tail>"]},
    "<hold_id_tail>": {"[": ["[", "<index>", "]"], ".": [".", "id", "<hold_id_tail2>"]},
    "<hold_id_tail2>": {"[": ["[", "<index>", "]"]},
    "<unary_statement>": {"id": ["<post_unary>", "<more_unary>", ";"]},
    "<more_unary>": {";": [], ",": [",", "<unary_statement>"]},
    "<pre_unary>": {},
    "<post_unary>": {"id": ["<unary_id>", "<unary_op>"]},
    "<unary_id>": {"id": ["<id_holder>"]},
    "<return_statement>": {"ret": ["ret", "<return_value>", ";"]},
    "<return_value>": {"(": ["(", "<return_value>", ")"], "id": ["id", "<ret_id_tail>"], "none": ["none"]},
    "<ret_id_tail>": {";": [], "[": ["[", "<index>", "]"], "(": ["(", "<parameter>", ")"], ".": [".", "id", "<id_array_tail>"]},
    "<conditional_statement>": {"if": ["<if_statement>"], "switch": ["<switch_statement>"]},
    "<if_statement>": {"if": ["if", "(", "<condition>", ")", "{", "<conditional_body>", "}", "<elif_statement>", "<else_statement>"]},
    "<elif_statement>": {"elif": ["elif", "(", "<condition>", ")", "{", "<conditional_body>", "}", "<elif_statement>", "<else_statement>"]},
    "<else_statement>": {"else": ["else", "{", "<conditional_body>", "}"]},
    "<switch_statement>": {"switch": ["switch", "(", "id", "<id_tail>", ")", "{", "<key_block>", "<def_block>}"]},
    "<key_block>": {"key": ["key", "<literals>", ":", "<conditional_body>", "<more_key>"]},
    "<more_key>": {"key": ["<key_block>", "<more_key>"]},
    "<def_block>": {"}": [], "def": ["def", ":", "<conditional_body>"]},
    "<conditional_body>": {"brk": ["brk", ";", "<conditional_body>"]},
    "<looping_statement>": {"for": ["<for_statement>"]},
    "<looping_statement>": {"while": ["<while_statement>"]},
    "<looping_statement>": {"do": ["<do_statement>"]},
    "<looping_statement>": {"foreach": ["<foreach_statement>"]},
    "<for_statement>": {"for": ["for", "(", "<initialization>", ";", "<condition>", ";", "<iteration>", ")", "{", "<looping_body>", "}"]},
    "<while_statement>": {"while": ["while", "(", "<condition>", ")", "{" "<looping_body>", "}"]},
    "<do_statement>": {"do": ["do", "{", "<looping_body>", "}", "while", "(", "<condition>", ")", ";"]},
    "<foreach_statement>": {"foreach": ["foreach", "(", "<initialization>", "in", "id", ")", "{" "<nested_foreach_body>", "}"]}
}

def add_set(set, production, prod_set):
    for terminal in set:
        parsing_table[production][terminal].extend = prod_set

add_set(["segm", "str", "main"], "<program>", ["<global_dec>", "main", "{", "<statements>", "}"])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc"], "<global_dec>", ["<declaration_statement>", "<global_dec>"])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "main"], "<segm>", [])
add_set(["str", "bln", "chr", "dec", "int", "var"], "<parameter>", ["<vartype>", "id", "<mul_parameter>"])
add_set(["const", "var", "int", "dec", "chr", "str", "bln"], "<declaration_statement>", ["<identifier_declaration>", "<declaration_statement>"])
add_set(["str", "bln", "chr", "dec", "int"], "<identifier_declaration>", ["<datatype>", "<iden_dec_tail>"])
add_set(["str", "bln", "chr", "dec", "int"], "<const_dec_tail>", ["<datatype>", "<const_dec_in>"])
add_set([";", ","], "<init_statement>", [])
add_set(["=", "+=", "-=", "*=", "/=", "%="], "<init_statement>", ["<assignment_op>", "<value>"])
add_set(["int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<value>", ["<operand>", "<expression>"])
add_set(["str_lit", "chr_lit"], "<value>", ["<text_format>"])
add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<array_elements>", ["<literals>"])
add_set(["id", ",", ";"], "<struct_declaration_tail>", ["<instance_declaration>"])
add_set(["str", "bln", "chr", "dec", "int"], "<members_declaration>", ["<vartype>", "<struct_id>", "<struct_id_tail>", ";"])
add_set(["int", "dec", "chr", "str", "bln", "var"], "<more_members>", ["<members_declaration>", "<more_members>"])
add_set(["int", "dec", "chr", "str", "bln", "var"], "<instance_declaration>", ["<members_declaration>", "<more_members>"])
add_set([",", ";"], "<struct_id_tail>", [])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
    "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach"], "<statements>", ["<other_statements>"])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "var", "strc"], "<other_statements>", ["<declaration_statement>", "<statements>"])
add_set(["++", "--"], "<other_statements>", ["<pre_unary>", "<statements>"])
add_set(["if", "switch"], "<other_statements>", ["<conditional_statement>", "<statements>"])
add_set(["for", "while", "do", "foreach"], "<other_statements>", ["<looping_statement>", "<statements>"])
add_set(["++", "--"], "<assignment_tail>", ["<unary_op>", "<more_unary>"])
add_set(["[", ".",  "=", "+=", "-=", "*=", "/=", "%="], "<assignment_tail>", ["<assignment_id_tail>", "<assignment_op>", "<value>", "<more_assignment>"])
add_set(["=", "+=", "-=", "*=", "/=", "%="], "<assignment_id_tail>", [])
add_set(["str_lit", "chr_lit"], "<output_value>", ["<text_format>", "<more_output>"])
add_set(["int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--", "("], 
    "<output_value>", ["<text_ftail_operand>", "<more_output>"])
add_set([")", ";"], "<hold_id_tail>", [])
add_set([")", ";"], "<hold_id_tail2>", [])
add_set(["++", "--"], "<unary_statement>", ["<pre_unary>", "<more_unary>", ";"])
add_set(["++", "--"], "<pre_unary>", ["<unary_op>", "<unary_id>"])
add_set(["int_lit", "dec_lit", "true", "false"], "<return_value>", ["<expression_literals>"])
add_set(["str_lit", "chr_lit"], "<return_value>", ["<text_format>"])
add_set(["++", "--"], "<return_value>", ["<pre_unary>"])
add_set(["++", "--"], "<ret_id_tail>", ["<unary_op>"])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
    "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "else", "}"], "<elif_statement>", [])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
    "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "}"], "<else_statement>", [])
add_set(["def", "}"], "<more_key>", [])
add_set(["key", "def", "}"], "<conditional_body>", [])
add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
    "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach"], "<conditional_body>", ["<other_statements>", "<conditional_body>"])



