import string

errorflag = [False]

state = []
lexeme = []
token = []
idens = []
rows = []
col = []

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
    'paren1_delim' : whitespace + arithmetic_operator + relational_operator + ['&', '|', '{', ')', ';', ',', '=', '!'],
    'brace_delim' : whitespace + alphanumeric + [';', '(', "'", '"', '{', '}', '+', '-', '.', '~'],
    'semicolon_delim' : whitespace + alphanumeric + ['~', '(', '}', '+', '-', None],
    'bracket_delim' : whitespace + alphanumeric + [']', ',', '+', '-', '.', '('],
    'bracket1_delim' : whitespace + number_operator + [')', '=', ';', '&', '.', ','],
    'concat_delim' : whitespace + alphanumeric + ['(', '"', "'", '#', '~'],
    'data_delim' : whitespace + ['[', '('],
    'val_delim' : whitespace + [';', ',', ')', '}', '!', '&', '=', '|'],
    'colon_delim' : whitespace + alphanumeric + ['(', '+', '-'],
    'jmp_delim' : whitespace + [';'],
    'key_delim' : whitespace + alphanumeric + ["'", '"', '~', '(', '.'],
    'num_delim' : whitespace + all_operators + [':', ';', ')', '}', ']', ','],
    'not_delim' : whitespace + alpha + ['(']
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
    "<global_dec>": {},
    "<segm>": {"segm": ["segm", "id", "(", "<parameter>", ")", "{", "<statements>", "}", "<segm>"]},
    "<parameter>": {")": ["null"]},
    "<mul_parameter>": {")": ["null"], ",": [",", "<vartype>", "<id_declare>", "<mul_parameter>"]},
    "<declaration_statement>": {},
    "<identifier_declaration>": {"var": ["var", "<variable_declaration>"], "const": ["const", "<const_dec_tail>"]},
    "<iden_dec_tail>": {"[": ["<array_declaration>"]},
    "<const_dec_tail>": {"var": ["var", "<const_declaration>"]},
    "<const_dec_in>": {"[": ["<array_declaration>"]},
    "<variable_declaration>": {},
    "<const_declaration>": {},
    "<init_statement>": {},
    "<mul_init>": {";": ["null"], ",": [",", "<id_declare>", "<init_statement>", "<mul_init>"]},
    "<cons_mul>": {";": ["null"], ",": [",", "<id_declare>", "=", "<value>", "<mul_init>"]},
    "<id_declare>": {"(": ["(","<id_declare>",")"], "id": ["id"]},
    "<array_declaration>": {"[": ["[", "<array_dimension>", ";"]},
    "<array_dimension>": {"]": ["]", "<id_declare>", "<array_init>", "<more_array_init>"], ",": [",", "]", "<id_declare>", "<two_array_init>", "<more_two_array_init>"]},
    "<array_init>": {"=": ["=", "{", "<array_elements>", "<more_lit>","}"]},
    "<more_lit>": {"}": ["null"], ",": [",", "<array_elements>", "<more_lit>"]},
    "<more_array_init>": {";": ["null"], ",": [",", "id", "<array_init>", "<more_array_init>"]},
    "<two_array_init>": {"=": ["=", "{", "{", "<array_elements>", "<more_lit>", "}", "<two_more_lit>", "}"]},
    "<two_more_lit>": {"}": ["null"], ",": [",", "{", "<array_elements>", "<more_lit>", "}", "<two_more_lit>"]},
    "<more_two_array_init>": {";": ["null"], ",": [",", "id", "<two_array_init>", "<more_two_array_init>"]},
    "<array_elements>": {"(":["(","<array_elements>",")"],"none": ["none"]},
    #"<struct_declaration>": {"strc": ["strc", "id", "<struct_declaration_tail>"]},
    #"<struct_declaration_tail>": {"{": ["<struct_define>"]},
    #"<struct_define>": {"{": ["{", "<members_declaration>", "<more_members>", "}", "<instance>", "<more_instance>", ";"]},
    #"<members_declaration>": {},
    #"<more_members>": {"}": ["null"]},
    #"<instance>": {},
    #"<more_instance>": {";": ["null"], ",": [",", "<struct_id>", "<more_instance>"]},
    #"<instance_declaration>": {},
    #"<more_instance_declaration>": {";": ["null"], ",": [",", "<struct_id>", "<more_instance_declaration>"]},
    #"<struct_id>": {},
    #"<struct_id_tail>": {"[": ["[", "]"]}, 
    "<statements>": {"id": ["<assignment_statements>", "<statements>"], "disp": ["<output_statement>", "<statements>"],
        "insp": ["<input_statement>", "<statements>"], "ret": ["<return_statement>", "<statements>"], "exit": ["exit", ";", "<statements>"], "segm": ["<segm_statements>","<statements>"]},
    "<segm_statements>": {"segm": ["segm", "id", "(", "<parameter>", ")", "{", "<statements>", "}"]},
    "<assignment_statements>": {"id": ["id", "<assignment_tail>", ";"]},
    "<assignment_tail>": {"(": ["(", "<args>", ")"]},
    "<assignment_id_tail>": {"[": ["[", "<index>", "]"]},
    "<more_assignment>": {";": ["null"], ",": [",", "id", "<assignment_tail>"]},
    "<output_statement>": {"disp": ["disp", "(", "<value>", ")", ";"]},
    "<value>": {"(": ["(","<value>",")", "<expression>"], "none": ["none"]},
    "<bln_value>": {"id": ["id", "<id_tail>", "<expression>"]},
    "<init_value>": {"(": ["(","<value>",")", "<expression>"], "none": ["none"]},
    #"<more_value>": {"&": ["&", "<value>"]},
    "<input_statement>": {"insp": ["insp", "(", "<id_holder>", ")", ";"]},
    "<id_holder>": {"id": ["id", "<hold_id_tail>"]},
    "<hold_id_tail>": {"[": ["[", "<index>", "]"]},
    "<hold_id_tail_next>": {"[": ["[", "<index>", "]"]},
    #"<more_hold_id_tail>": {".": [".","id","<hold_id_tail_next>"]},
    "<pre_unary_statement>": {},
    "<pre_unary_paren>": {},
    "<unary_statement>": {"id": ["<post_unary>", "<more_unary>"]},
    "<more_unary>": {",": [",", "<unary_statement>"]},
    "<pre_unary>": {},
    "<post_unary>": {"id": ["<unary_id>", "<unary_op>"]},
    "<unary_id>": {"id": ["<id_holder>"]},
    "<return_statement>": {"ret": ["ret", "<return_value>", ";"]},
    "<return_value>": {"(": ["(", "<return_value>", ")", "<ret_expression>"], "id": ["id", "<ret_id_tail>","<ret_expression>"], "none": ["none"]},
    "<ret_expression>": {},
    "<ret_id_tail>": {"[": ["[", "<index>", "]"], "(": ["(", "<args>", ")"]},
    "<conditional_statement>": {"if": ["<if_statement>"], "switch": ["<switch_statement>"]},
    "<if_statement>": {"if": ["if", "(", "<condition>", ")", "{", "<conditional_body>", "}", "<elif_statement>", "<else_statement>"]},
    "<elif_statement>": {"elif": ["elif", "(", "<condition>", ")", "{", "<conditional_body>", "}", "<elif_statement>"]},
    "<else_statement>": {"else": ["else", "{", "<conditional_body>", "}"]},
    "<switch_statement>": {"switch": ["switch", "(", "id", "<id_tail>", ")", "{", "<key_block>", "<def_block>", "}"]},
    "<key_block>": {"key": ["key", "<literals>", ":", "<conditional_body>", "<more_key>"]},
    "<more_key>": {"key": ["<key_block>", "<more_key>"]},
    "<def_block>": {"}": ["null"], "def": ["def", ":", "<conditional_body>"]},
    "<conditional_body>": {},
    "<brk>": {"brk": ["brk", ";"]},
    "<looping_statement>": {"for": ["<for_statement>"], "while": ["<while_statement>"], "do": ["<do_statement>"], "foreach": ["<foreach_statement>"]},
    "<for_statement>": {"for": ["for", "(", "<initialization>", ";", "<condition>", ";", "<iteration>", ")", "{", "<looping_body>", "}"]},
    "<while_statement>": {"while": ["while", "(", "<condition>", ")", "{", "<looping_body>", "}"]},
    "<do_statement>": {"do": ["do", "{", "<looping_body>", "}", "while", "(", "<condition>", ")", ";"]},
    "<foreach_statement>": {"foreach": ["foreach", "(", "<for_datatype>", "id", "in", "id", ")", "{", "<nested_foreach_body>", "}"]},
    "<nested_foreach_body>": {"foreach": ["foreach", "(", "id", "in", "id", ")", "{", "<foreach_body>", "}"]},
    "<foreach_body>": {"}": ["null"],"for": ["<for_statement>", "<foreach_body>"], "do": ["<do_statement>", "<foreach_body>"], "while": ["<while_statement>", "<foreach_body>"],
        "insp": ["<input_statement>", "<foreach_body>"], "disp": ["<output_statement>", "<foreach_body>"], "id": ["<assignment_statements>", "<foreach_body>"],
        "ret": ["<return_statement>", "<foreach_body>"], "exit": ["exit", ";", "<foreach_body>"], "brk": ["brk", ";", "<foreach_body>"], "rsm": ["rsm", ";", "<foreach_body>"]},
    "<looping_body>": {},
    "<rsm>": {"}": ["null"], "rsm": ["rsm", ";"]},
    "<initialization>": {},
    "<for_datatype>": {"id": ["null"], "int": ["int"], "dec": ["dec"], "chr": ["chr"], "var": ["var"]},
    "<initial_value>": {"(": ["(","<initial_value>",")"],"chr_lit": ["chr_lit"], "int_lit": ["int_lit", "<expression_num>"], "dec_lit": ["dec_lit", "<expression_num>"],"id":["id","<id_tail>","<expression_num>"]},
    "<condition>": {},
    "<con_value>": {"(": ["(", "<con_value>",")","<con_operand_tail>","<con_expression>"], "bln": ["bln", "(", "<type_value>", ")", "<con_expression>"]},
    "<con_expression>": {},
    "<con_operand>": {"id": ["id","<id_tail>","<con_operand_tail>"],"dec_lit": ["dec_lit", "<con_operand_tail>"], "int_lit": ["int_lit", "<con_operand_tail>"]},
    "<con_type_conversion>": {"str": ["str","(","<type_value>",")"], "chr": ["chr","(","<type_value>",")"], "int": ["int","(","<type_value>",")","<con_operand_tail>"],
                              "dec": ["dec","(","<type_value>",")","<con_operand_tail>"]},
    "<con_operand_tail>": {},
    "<con_operand_paren>": {"(": ["(","<con_operand_paren>",")", "<con_operand_tail>"]},
    "<comparison_operator>": {},
    "<iteration>": {},
    "<iteration_statement>": {"id": ["id", "<iteration_statement_tail>"], "(": ["(","<iteration_statement>",")"]},
    "<iteration_statement_tail>": {},
    "<iteration_expression>": {},
    "<iteration_value>": {},
    "<iteration_value_tail>": {"(": ["(","<not_op>","<iteration_value_tail>",")", "<iteration_value>"]},
    "<iteration_id>": {"int_lit": ["int_lit"], "dec_lit": ["dec_lit"], "id": ["id", "<id_tail>"]},
    "<more_iteration>": {")": ["null"], ",": [",", "<iteration>"]},
    "<expression>": {},
    "<expression_num>": {},
    "<expression_not_num>": {},
    "<tail_operand>": {"(": ["(", "<not_op>", "<tail_operand>", ")", "<expression>"]},
    "<number_tail_operand>": {"(": ["(", "<number_tail_operand>", ")", "<expression_num>"]},
    "<operand>": {"id": ["id", "<id_tail>"]}, 
    "<spec_operand>": {},
    "<text_operand>": {"str_lit": ["str_lit"], "chr_lit": ["chr_lit"]},
    "<number_operand>": {"id": ["id", "<id_tail>"]},
    "<integer_operand>": {"int_lit": ["int_lit"], "dec_lit": ["dec_lit"]},
    "<bln_id_operand>": {"id": ["id", "<id_tail>"]},
    "<operator>": {},
    "<non_number_operator>": {},
    "<expression_literals>": {"int_lit": ["int_lit"], "dec_lit": ["dec_lit"]},
    "<assignment_op>": {"=": ["="], "+=": ["+="], "-=": ["-="], "*=": ["*="], "/=": ["/="], "%=": ["%="]},
    "<arithmetic_op>": {"+": ["+"], "-": ["-"], "*": ["*"], "/": ["/"], "%": ["%"]},
    "<relational_op>": {"<": ["<"], "<=": ["<="], ">": [">"], ">=": [">="], "!=": ["!="], "==": ["=="]},
    "<unary_op>": {"++": ["++"], "--": ["--"]},
    "<logical_op>": {"&&": ["&&"], "||": ["||"]},
    "<not_op>": {"!": ["!"]},
    "<text_format>": {"str_lit": ["str_lit", "<concat_string>"], "chr_lit": ["chr_lit", "<concat_string>"]},
    "<concat_string>": {"&": ["&", "<concat_value>"]},
    "<concat_value>": {"(": ["(","<concat_value>",")","<concat_string>"]},
    "<type_conversion>": {},
    "<type_value>": {"(": ["(","<type_value>",")"], "id": ["id", "<id_tail>"], "none": ["none"]},
    "<index>": {}, 
    "<more_index>": {",": [",", "<index_value>"], "]": ["null"]},
    "<index_value>": {"(": ["(", "<index_value>", ")", "<index_expression>"]},
    "<index_expression>": {},
    "<index_operand>": {"int_lit": ["int_lit"], "id": ["id"]},
    "<id_tail>": {"[": ["[", "<index>", "]"], "(": ["(", "<args>", ")"]},
    "<id_array_tail>": {"[": ["[", "<index>", "]"]},
    #"<more_id_tail>": {".": [".","id","<id_array_tail>"]},
    "<args>": {},
    "<args_operand>": {"(": ["(","<args_operand>",")"], "id": ["id", "<id_tail>"]},
    "<more_args>": {")": ["null"], ",": [",", "<args>"]},
    "<vartype>": {"var": ["var"]},
    "<datatype>": {"str": ["str"], "bln": ["bln"], "chr": ["chr"], "dec": ["dec"], "int": ["int"]},
    "<literals>": {"str_lit": ["str_lit"], "chr_lit": ["chr_lit"], "int_lit": ["int_lit"], "dec_lit": ["dec_lit"]},
    "<bln>": {"false": ["false"], "true": ["true"]},
}

def add_set(set, production, prod_set):
    for terminal in set:
        if terminal not in parsing_table:
            parsing_table[production][terminal] = []
        parsing_table[production][terminal].extend(prod_set)


def add_all_set():
    add_set(["segm", "const", "var", "int", "dec", "chr", "str", "bln", "main"], "<program>", ["<global_dec>", "<segm>", "main", "{", "<statements>", "}"])
    add_set(["segm", "main"], "<global_dec>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln"], "<global_dec>", ["<declaration_statement>", "<global_dec>"])
    add_set(["main"], "<segm>", ["null"])
    add_set(["str", "bln", "chr", "dec", "int", "var"], "<parameter>", ["<vartype>", "<id_declare>", "<mul_parameter>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln"], "<declaration_statement>", ["<identifier_declaration>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<identifier_declaration>", ["<datatype>", "<iden_dec_tail>"])
    add_set(["id", "("], "<iden_dec_tail>", ["<variable_declaration>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<const_dec_tail>", ["<datatype>", "<const_dec_in>"])
    add_set(["id", "("], "<const_dec_in>", ["<const_declaration>"])
    add_set(["id", "("], "<variable_declaration>", ["<id_declare>","<init_statement>","<mul_init>", ";"])
    add_set(["id", "("], "<const_declaration>", ["<id_declare>", "=", "<value>", "<cons_mul>", ";"])
    add_set([";", ","], "<init_statement>", ["null"])
    add_set(["=", "+=", "-=", "*=", "/=", "%="], "<init_statement>", ["<assignment_op>", "<value>"])
    add_set([";", ","], "<array_init>", ["null"])
    add_set([";", ","], "<two_array_init>", ["null"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<array_elements>", ["<literals>"])
    #add_set(["id", "("], "<struct_declaration_tail>", ["<instance_declaration>"])
    #add_set(["str", "bln", "chr", "dec", "int", "var"], "<members_declaration>", ["<vartype>", "<id_declare>", ";"])
    #add_set(["int", "dec", "chr", "str", "bln", "var"], "<more_members>", ["<members_declaration>", "<more_members>"])
    #add_set([";", ","], "<instance>", ["null"])
    #add_set(["id", "("], "<instance>", ["<struct_id>"])
    #add_set(["id", "("], "<instance_declaration>", ["<struct_id>", ";"])
    #add_set(["id", "("], "<struct_id>", ["<id_declare>","<struct_id_tail>"])
    #add_set([",", ";"], "<struct_id_tail>", ["null"])
    add_set(["brk", "rsm", "key", "def","}"], "<statements>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln"], "<statements>", ["<declaration_statement>", "<statements>"])
    add_set(["++", "--"], "<statements>", ["<pre_unary_statement>", "<statements>"])
    add_set(["if", "switch"], "<statements>", ["<conditional_statement>", "<statements>"])
    add_set(["for", "while", "do", "foreach"], "<statements>", ["<looping_statement>", "<statements>"])
    add_set(["++", "--"], "<assignment_tail>", ["<unary_op>", "<more_unary>"])
    add_set(["[",  "=", "+=", "-=", "*=", "/=", "%="], "<assignment_tail>", ["<assignment_id_tail>", "<assignment_op>", "<value>", "<more_assignment>"])
    add_set(["=", "+=", "-=", "*=", "/=", "%="], "<assignment_id_tail>", ["null"])
    add_set(["str_lit", "chr_lit"], "<value>", ["<text_format>"])
    add_set(["true", "false", "id", "!"], "<value>", ["<not_op>","<bln_value>"])
    #add_set(["str_lit", "chr_lit"], "<value>", ["<text_operand>", "<expression_not_num>"])
    add_set(["int_lit", "dec_lit"], "<value>", ["<integer_operand>", "<expression>"])
    add_set(["int", "dec", "chr", "str", "bln", "++", "--"], "<value>", ["<spec_operand>", "<expression>"])
    add_set(["true", "false"], "<bln_value>", ["<bln>", "<expression_not_num>"])
    #add_set([")", ";", ","], "<more_value>", ["null"])
    add_set(["=", "+=", "-=", "/=", "*=", "%=", "++", "--", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";",","], "<hold_id_tail>", ["null"])
    add_set(["=", "+=", "-=", "/=", "*=", "%=","++", "--", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<hold_id_tail_next>", ["null"])
    #add_set(["=", "+=", "-=", "/=", "*=", "%=","++", "--", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<more_hold_id_tail>", ["null"])
    add_set(["++", "--"], "<pre_unary_statement>", ["<pre_unary_paren>", "<more_unary>", ";"])
    add_set(["++", "--"], "<pre_unary_paren>", {"<pre_unary>"})
    add_set(["++", "--"], "<unary_statement>", ["<pre_unary>", "<more_unary>"])
    add_set([")", ";" ], "<more_unary>", ["null"])
    add_set(["++", "--"], "<pre_unary>", ["<unary_op>", "<unary_id>"])
    #add_set(["int_lit", "dec_lit", "true", "false"], "<return_value>", ["<expression_literals>","<ret_expression>"])
    add_set(["int_lit", "dec_lit"], "<return_value>", ["<integer_operand>", "<expression_num>"])
    add_set(["true", "false"], "<return_value>", ["<bln>", "<expression_not_num>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<return_value>", ["<type_conversion>", "<ret_expression>"])
    add_set(["str_lit", "chr_lit"], "<return_value>", ["<text_format>"])
    add_set(["++", "--"], "<return_value>", ["<pre_unary>"])
    add_set([";", ")"], "<ret_expression>", ["null"])
    add_set(["+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=", "&&", "||"], "<ret_expression>", ["<operator>","<not_op>","<tail_operand>"])
    add_set([")", ";","+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=", "&&", "||"], "<ret_id_tail>", ["null"])
    add_set(["++", "--"], "<ret_id_tail>", ["<unary_op>"])
    add_set(["segm", "const", "var", "int", "dec", "chr", "str", "bln", "id", "disp", "insp", "++", "--", "ret", "exit", "if", "switch", "for", "while", 
             "do", "foreach", "brk", "rsm", "key", "def", "else","}"], "<elif_statement>", ["null"])
    add_set(["segm","const", "var", "int", "dec", "chr", "str", "bln", "id", "disp", "insp", "++", "--", "ret", "exit", "if", "switch", "for", 
             "while", "do", "foreach", "brk", "rsm", "key", "segm", "def", "}" ], "<else_statement>", ["null"])
    add_set(["def", "}"], "<more_key>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "id", "disp", "insp", "++", "--", "ret", "exit", "if", "switch", "for", "while", 
             "do", "foreach", "segm", "brk", "def", "key", "}"], "<conditional_body>", ["<statements>", "<brk>"])
    add_set(["def","rsm", "key", "}"], "<brk>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "id", "disp", "insp", "++", "--", 
        "ret", "exit", "if", "switch", "for", "while", "do", "brk", "rsm", "}"], "<nested_foreach_body>", ["<foreach_body>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln"], "<foreach_body>", ["<declaration_statement>", "<foreach_body>"])
    add_set(["if", "switch"], "<foreach_body>", ["<conditional_statement>", "<foreach_body>"])
    add_set(["++", "--"], "<foreach_body>", ["<pre_unary_statement>", "<foreach_body>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "id", "disp", "insp", "++", 
        "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "segm", "brk", "rsm","}"], "<looping_body>", ["<statements>", "<brk>","<rsm>"])
    add_set(["int", "dec", "chr", "var", "id"], "<initialization>", ["<for_datatype>", "id", "<hold_id_tail>", "=", "<initial_value>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<initial_value>", ["<type_conversion>", "<expression_num>"]) 
    add_set(["!", "(", "str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<condition>", ["<not_op>", "<con_value>"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "id", "int", "dec", "chr", "str", "++", "--"], "<con_value>", ["<con_operand>", "<con_expression>"])
    add_set(["true", "false"], "<con_value>", ["<bln>", "<con_expression>"])
    add_set([")", ";"], "<con_expression>", ["null"])
    add_set(["<", "<=", ">", ">=", "==", "!=", "&&", "||"], "<con_expression>", ["<comparison_operator>", "<not_op>","<con_value>"])
    add_set(["str", "chr", "int", "dec"], "<con_operand>", ["<con_type_conversion>"])
    add_set(["++", "--"], "<con_operand>", ["<pre_unary>","<con_operand_tail>"])
    add_set([ "str_lit", "chr_lit"], "<con_operand>", ["<text_format>"])
    add_set(["<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";" ], "<con_operand_tail>", ["null"])
    add_set(["+", "-", "*", "/", "%"], "<con_operand_tail>", ["<arithmetic_op>", "<con_operand_paren>"])
    add_set(["int_lit", "dec_lit", "str_lit", "chr_lit", "id", "int", "dec", "chr", "str", "++", "--"],"<con_operand_paren>", ["<con_operand>"])
    add_set(["<", "<=", ">", ">=", "==", "!="], "<comparison_operator>", ["<relational_op>"])
    add_set(["&&", "||"], "<comparison_operator>", ["<logical_op>"])
    add_set(["++", "--", "id"], "<iteration>", ["<iteration_statement>", "<more_iteration>"])
    add_set(["++", "--"], "<iteration_statement>", ["<pre_unary>"])
    add_set(["++", "--"],"<iteration_statement_tail>", ["<unary_op>"])
    add_set(["[", "=", "+=", "-=", "*=", "/=", "%=", ")", "," ],"<iteration_statement_tail>", ["<hold_id_tail>","<iteration_expression>"])
    add_set([")", "," ],"<iteration_expression>", ["null"])
    add_set(["=", "+=", "-=", "*=", "/=", "%=" ],"<iteration_expression>", ["<assignment_op>","<iteration_id>","<iteration_value>"])
    add_set([")", ","], "<iteration_value>", ["null"])
    add_set(["+", "-", "*", "/", "%"], "<iteration_value>", ["<arithmetic_op>", "<iteration_id>"])
    add_set(["int_lit", "dec_lit", "id", "++", "--" ], "<iteration_value_tail>", ["<iteration_id>", "<iteration_value>"])
    add_set(["++", "--"], "<iteration_id>", ["<pre_unary>"])
    add_set([")", ";", "&", ","], "<expression>", ["null"])
    add_set(["+", "-", "*", "/", "%"], "<expression>", ["<arithmetic_op>", "<number_tail_operand>"])
    add_set(["<", "<=", ">", ">=", "==", "!=", "&&", "||"], "<expression>", ["<non_number_operator>", "<not_op>", "<tail_operand>"])
    add_set(["&", ")", ";", ","], "<expression_num>", ["null"])
    add_set(["+", "-", "*", "/", "%" ], "<expression_num>", ["<arithmetic_op>", "<number_tail_operand>"])
    add_set([";", ")", ","], "<expression_not_num>", ["null"])
    add_set(["<", "<=", ">", ">=", "==", "!=", "&&", "||"], "<expression_not_num>", ["<non_number_operator>", "<tail_operand>"])
    add_set(["int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<tail_operand>", ["<operand>", "<expression>"])
    add_set(["int_lit", "dec_lit", "id", "++", "--"], "<number_tail_operand>", ["<number_operand>", "<expression_num>"])
    add_set(["int_lit", "dec_lit", "true", "false"], "<operand>", ["<expression_literals>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<operand>", ["<type_conversion>"])
    add_set(["++", "--"], "<operand>", ["<pre_unary>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<spec_operand>", ["<type_conversion>"])
    add_set(["++", "--"], "<spec_operand>", ["<pre_unary>"])
    add_set(["int_lit", "dec_lit"], "<number_operand>", ["<integer_operand>"])
    add_set(["++", "--"], "<number_operand>", ["<pre_unary>"])
    add_set(["true", "false"], "<bln_id_operand>", ["<bln>"])
    add_set(["+", "-", "*", "/", "%"], "<operator>", ["<arithmetic_op>"])
    add_set(["<", "<=", ">", ">=", "==", "!="], "<operator>", ["<relational_op>"])
    add_set(["&&", "||"], "<operator>", ["<logical_op>"])
    add_set(["<", "<=", ">", ">=", "==", "!="], "<non_number_operator>", ["<relational_op>"])
    add_set(["&&", "||"], "<non_number_operator>", ["<logical_op>"])
    add_set(["true", "false"], "<expression_literals>", ["<bln>"])
    add_set(["int_lit", "dec_lit", "str_lit", "chr_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--", "("], "<not_op>", ["null"])
    add_set([";", ")", ","], "<concat_string>", ["null"])
    add_set(["str_lit", "chr_lit"], "<concat_value>", ["<text_format>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<concat_value>", ["<type_conversion>"])
    add_set(["int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<concat_value>", ["<operand>", "<expression>", "<concat_string>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<type_conversion>", ["<datatype>", "(", "<type_value>", ")"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<type_value>", ["<literals>"])
    add_set(["int_lit", "id", "("], "<index>", ["<index_value>","<more_index>"])
    add_set(["int_lit", "id"], "<index_value>", ["<index_operand>","<index_expression>"])
    add_set([ ")", "]", ","], "<index_expression>", ["null"])
    add_set(["+", "-", "*", "/", "%"], "<index_expression>", ["<arithmetic_op>","<index_value>"])
    add_set(["=", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<id_tail>", ["null"])
    add_set(["++", "--"], "<id_tail>", ["<unary_op>"])
    add_set(["=", "+=", "-=", "*=", "/=", "%=", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<id_array_tail>", ["null"])
    #add_set(["=", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<more_id_tail>", ["null"])
    add_set([")", ","], "<args>", ["null"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "str", "bln", "chr", "dec", "int", "id", "(", "++", "--"], "<args>", ["<args_operand>","<expression>","<more_args>"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<args_operand>", ["<literals>"])
    add_set(["++", "--"], "<args_operand>", ["<pre_unary>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<args_operand>", ["<type_conversion>"])
    add_set(["int", "dec", "chr", "str", "bln"], "<vartype>", ["<datatype>"])
    add_set(["true", "false"], "<literals>", ["<bln>"])
#SEMANTIC
datatype = ["var", "str", "chr", "int", "dec", "bln"]
semantic_datatype = ["var", "str", "chr", "int", "dec", "bln"]
bool_lit = ["true", "false"]
literals = ["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"]
valid_literals = {"str": "str_lit","chr": "chr_lit", "int": "int_lit","dec": ["dec_lit", "int_lit"],"bln": ["true", "false"], "var":literals} 
var_literals = {"str": "str_lit","chr": "chr_lit", "int": "int_lit","dec": "dec_lit"} 
id_type = ["const"]
valid_conversion = {"bln": ["int_lit", "str_lit"], "chr": ["int_lit", "str_lit"], "int": ["true", "false", "chr_lit", "dec_lit", "str_lit"],
                    "dec": ["int_lit", "str_lit"], "str": ["chr_lit", "int_lit", "dec_lit", "true", "false"]}
literal_types = {"str": "str_lit","chr": "chr_lit","int": "int_lit","dec": "dec_lit","bln": "false"}
reverse_literal_types = {"str_lit": "str", "chr_lit": "chr", "int_lit": "int", "dec_lit": "dec", ("true", "false"): "bln"}
semantic_logical = ["||", "&&"]
non_terminal_check = ["<parameter>", "<identifier_declaration>", "<assignment_statements>", "<segm>", 
                      "<segm_statements>", "<pre_unary>", "<return_value>", "<initialization>", "<condition>", "<iteration>",
                      "<type_conversion>", "<initialization>", "<foreach_statement>",
                      "<condition>"
                      ]
codeblocks = ["if", "elif" ,"else", "for", "while", "do", "foreach", "switch"]
booleanValue = ["==", "!=", "<", "<=", ">", ">=", "true", "false"]
relate1_op = ["<", "<=", ">", ">="]
str_logical_operator = ["&&", "||"]
logicalValue = ["+", "-", "*", "/", "%","str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false", "(",")"]
assignment_number = ["+=", "-=", "*=", "/=", "%="]
