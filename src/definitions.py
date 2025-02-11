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
    "<global_dec>": {"main": ["null"], "segm": ["<segm>", "<global_dec>"]},
    "<segm>": {"segm": ["segm", "id", "(", "<parameter>", ")", "{", "<statements>", "}", "<segm>"]},
    "<parameter>": {")": ["null"]},
    "<mul_parameter>": {")": ["null"], ",": [",", "<vartype>", "id", "<mul_parameter>"]},
    "<declaration_statement>": {},
    "<identifier_declaration>": {"var": ["var", "<variable_declaration>"], "const": ["const", "<const_dec_tail>"]},
    "<iden_dec_tail>": {"id": ["<variable_declaration>"], "[": ["<array_declaration>"]},
    "<const_dec_tail>": {"var": ["var", "<const_declaration>"]},
    "<const_dec_in>": {"id": ["<const_declaration>"], "[": ["<array_declaration>"]},
    "<variable_declaration>": {"id": ["id", "<init_statement>", "<mul_init>", ";"]},
    "<const_declaration>": {"id": ["id", "=", "<value>", "<cons_mul>", ";"]},
    "<init_statement>": {},
    "<mul_init>": {";": ["null"], ",": [",", "id", "<init_statement>", "<mul_init>"]},
    "<cons_mul>": {";": ["null"], ",": [",", "id", "=", "<value>", "<mul_init>"]},
    "<value>": {"(": ["(", "<value>", ")", "<expression>"]},
    "<array_declaration>": {"[": ["[", "<array_dimension>", ";"]},
    "<array_dimension>": {"]": ["]", "id", "<array_init>"], ",": [",", "]", "id", "<two_array_init>"]},
    "<array_init>": {";": ["null"], "=": ["=", "{", "<array_elements>", "<more_lit>","}"]},
    "<more_lit>": {"}": ["null"], ",": [",", "<array_elements>", "<more_lit>"]},
    "<two_array_init>": {";": ["null"], "=": ["=", "{", "{", "<array_elements>", "<more_lit>", "}", "<two_more_lit>", "}"]},
    "<two_more_lit>": {"}": ["null"], ",": [",", "{", "<array_elements>", "<more_lit>", "}", "<two_more_lit>"]},
    "<array_elements>": {"none": ["none"]},
    "<struct_declaration>": {"strc": ["strc", "id", "<struct_declaration_tail>"]},
    "<struct_declaration_tail>": {"{": ["<struct_define>"]},
    "<struct_define>": {"{": ["{", "<members_declaration>", "<more_members>", "}", "<instance>", "<more_instance>", ";"]},
    "<members_declaration>": {},
    "<more_members>": {"}": ["null"]},
    "<instance>": {"id": ["id"]},
    "<more_instance>": {";": ["null"], ",": [",", "id", "<more_instance>"]},
    "<instance_declaration>": {"id": ["<struct_id>", "<more_instance_declaration>", ";"]},
    "<more_instance_declaration>": {";": ["null"], ",": [",", "<struct_id>", "<more_instance_declaration>"]},
    "<struct_id>": {"id": ["id", "<struct_id_tail>"]},
    "<struct_id_tail>": {"[": ["[", "<index>", "]"]}, 
    "<statements>": {"}": ["null"]},
    "<other_statements>": {"id": ["<assignment_statements>", "<statements>"], "disp": ["<output_statement>", "<statements>"],
        "insp": ["<input_statement>", "<statements>"], "ret": ["<return_statement>", "<statements>"], "exit": ["exit", ";", "<statements>"], "brk": ["brk", ";", "<statements>"]},
    "<assignment_statements>": {"id": ["id", "<assignment_tail>", ";"]},
    "<assignment_tail>": {"(": ["(", "<args>", ")"]},
    "<assignment_id_tail>": {"[": ["[", "<index>", "]"], ".": [".", "id", "<id_array_tail>"]},
    "<more_assignment>": {";": ["null"], ",": [",", "id", "<assignment_tail>"]},
    "<output_statement>": {"disp": ["disp", "(", "<output_value>", ")", ";"]},
    "<output_value>": {"none": ["none"]},
    "<more_output>": {")": ["null"], "&": ["&", "<output_value>", "<more_output>"]},
    "<input_statement>": {"insp": ["insp", "(", "<id_holder>", ")", ";"]},
    "<id_holder>": {"id": ["id", "<hold_id_tail>"]},
    "<hold_id_tail>": {"[": ["[", "<index>", "]"], ".": [".", "id", "<hold_id_tail2>"]},
    "<hold_id_tail2>": {"[": ["[", "<index>", "]"]},
    "<unary_statement>": {"id": ["<post_unary>", "<more_unary>", ";"]},
    "<more_unary>": {";": ["null"], ",": [",", "<unary_statement>"]},
    "<pre_unary>": {},
    "<post_unary>": {"id": ["<unary_id>", "<unary_op>"]},
    "<unary_id>": {"id": ["<id_holder>"]},
    "<return_statement>": {"ret": ["ret", "<return_value>", ";"]},
    "<return_value>": {"(": ["(", "<return_value>", ")"], "id": ["id", "<ret_id_tail>","<ret_expression>"], "none": ["none"]},
    "<ret_id_tail>": {"[": ["[", "<index>", "]"], "(": ["(", "<ret_args>", ")"], ".": [".", "id", "<id_array_tail>"]},
    "<conditional_statement>": {"if": ["<if_statement>"], "switch": ["<switch_statement>"]},
    "<if_statement>": {"if": ["if", "(", "<condition>", ")", "{", "<conditional_body>", "}", "<elif_statement>", "<else_statement>"]},
    "<elif_statement>": {"elif": ["elif", "(", "<condition>", ")", "{", "<conditional_body>", "}", "<elif_statement>", "<else_statement>"]},
    "<else_statement>": {"else": ["else", "{", "<conditional_body>", "}"]},
    "<switch_statement>": {"switch": ["switch", "(", "id", "<id_tail>", ")", "{", "<key_block>", "<def_block>", "}"]},
    "<key_block>": {"key": ["key", "<literals>", ":", "<conditional_body>", "<more_key>"]},
    "<more_key>": {"key": ["<key_block>", "<more_key>"]},
    "<def_block>": {"}": ["null"], "def": ["def", ":", "<conditional_body>"]},
    "<conditional_body>": {"brk": ["brk", ";", "<conditional_body>"]},
    "<looping_statement>": {"for": ["<for_statement>"], "while": ["<while_statement>"], "do": ["<do_statement>"], "foreach": ["<foreach_statement>"]},
    "<for_statement>": {"for": ["for", "(", "<initialization>", ";", "<condition>", ";", "<iteration>", ")", "{", "<looping_body>", "}"]},
    "<while_statement>": {"while": ["while", "(", "<condition>", ")", "{", "<looping_body>", "}"]},
    "<do_statement>": {"do": ["do", "{", "<looping_body>", "}", "while", "(", "<condition>", ")", ";"]},
    "<foreach_statement>": {"foreach": ["foreach", "(", "<for_datatype>", "id", "in", "id", ")", "{", "<nested_foreach_body>", "}"]},
    "<nested_foreach_body>": {"}": ["null"], "foreach": ["foreach", "(", "id", "in", "id", ")", "{", "<foreach_body>", "}"]},
    "<foreach_body>": {"}": ["null"], "for": ["<for_statement>", "<foreach_body>"], "do": ["<do_statement>", "<foreach_body>"], "while": ["<while_statement>", "<foreach_body>"],
        "insp": ["<input_statement>", "<foreach_body>"], "disp": ["<output_statement>", "<foreach_body>"], "id": ["<assignment_statements>", "<foreach_body>"],
        "ret": ["<return_statement>", "<foreach_body>"], "exit": ["exit", ";", "<foreach_body>"], "brk": ["brk", ";", "<foreach_body>"], "rsm": ["rsm", ";", "<foreach_body>"]},
    "<looping_body>": {"}": ["null"], "brk": ["brk", ";", "<looping_body>"], "rsm": ["rsm", ";", "<looping_body>"]},
    "<initialization>": {},
    "<for_datatype>": {"id": ["null"], "int": ["int"], "dec": ["dec"], "chr": ["chr"], "var": ["var"]},
    "<initial_value>": {"chr_lit": ["chr_lit", "<expression>"], "int_lit": ["int_lit", "<expression>"], "dec_lit": ["dec_lit", "<expression>"],"id":["id","<id_tail>","<expression>"]},
    "<condition>": {},
    "<con_value>": {"(": ["(", "<con_operand>", "<con_expression>",")","<con_expression>"]},
    "<con_expression>": {},
    "<con_operand>": {"str_lit": ["str_lit"], "chr_lit": ["chr_lit"]},
    "<comparison_operator>": {},
    "<iteration>": {},
    "<iteration_statement>": {"id": ["id", "<id_tail>", "<iteration_value>"]},
    "<iteration_value>": {},
    "<iteration_id>": {"int_lit": ["int_lit"], "dec_lit": ["dec_lit"], "id": ["id", "<id_tail>"]},
    "<more_iteration>": {")": ["null"], ",": [",", "<iteration>"]},
    "<expression>": {},
    "<tail_operand>": {"(": ["(", "<not_op>", "<operand>", "<expression>", ")", "<expression>"]},
    "<operand>": {"id": ["id", "<id_tail>"]}, 
    "<operator>": {},
    "<expression_literals>": {"int_lit": ["int_lit"], "dec_lit": ["dec_lit"], "chr_lit": ["chr_lit"]},
    "<assignment_op>": {"=": ["="], "+=": ["+="], "-=": ["-="], "*=": ["*="], "/=": ["/="], "%=": ["%="]},
    "<arithmetic_op>": {"+": ["+"], "-": ["-"], "*": ["*"], "/": ["/"], "%": ["%"]},
    "<relational_op>": {"<": ["<"], "<=": ["<="], ">": [">"], ">=": [">="], "!=": ["!="], "==": ["=="]},
    "<unary_op>": {"++": ["++"], "--": ["--"]},
    "<logical_op>": {"&&": ["&&"], "||": ["||"]},
    "<not_op>": {"!": ["!"]},
    "<text_format>": {"str_lit": ["str_lit", "<concat_string>"], "chr_lit": ["chr_lit", "<concat_string>"]},
    "<concat_string>": {"&": ["&", "<concat_value>"]},
    "<concat_value>": {"id": ["id", "<id_tail>","<concat_string>"], "(": ["(","id", "<id_tail>", "<expression>",")","<concat_string>"]},
    "<type_conversion>": {},
    "<type_value>": {"id": ["id", "<id_tail>"]},
    "<index>": {"int_lit": ["int_lit", "<more_index>"], "id": ["id", "<more_index>"]}, 
    "<more_index>": {",": [",", "<index_value>"], "]": ["null"]},
    "<index_value>": {"int_lit": ["int_lit"], "id": ["id"]},
    "<id_tail>": {"[": ["[", "<index>", "]"], "(": ["(", "<args>", ")"], ".": [".", "id", "<id_array_tail>"]},
    "<id_array_tail>": {"[": ["[", "<index>", "]"]},
    "<function_call>": {"id": ["id", "(", "<args>", ")", ";"]},
    "<args>": {"id": ["id", "<id_tail>", "<expression>", "<more_args>"]},
    "<more_args>": {")": ["null"], ",": [",", "<args>", "<more_args>"]},
    "<vartype>": {"var": ["var"]},
    "<datatype>": {"str": ["str"], "bln": ["bln"], "chr": ["chr"], "dec": ["dec"], "int": ["int"]},
    "<literals>": {"str_lit": ["str_lit"], "chr_lit": ["chr_lit"], "int_lit": ["int_lit"], "dec_lit": ["dec_lit"]},
    "<bln>": {"false": ["false"], "true": ["true"]},
    #"con_operand": {},
    "<ret_expression>":{},
    "<ret_args>":{"(":["(","<ret_args>",")"]}
}

def add_set(set, production, prod_set):
    for terminal in set:
        if terminal not in parsing_table:
            parsing_table[production][terminal] = []
        parsing_table[production][terminal].extend(prod_set)


def add_all_set():
    add_set(["segm", "const", "var", "int", "dec", "chr", "str", "bln", "strc", "main"], "<program>", ["<global_dec>", "main", "{", "<statements>", "}"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc"], "<global_dec>", ["<declaration_statement>", "<global_dec>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "main"], "<segm>", ["null"])
    add_set(["str", "bln", "chr", "dec", "int", "var"], "<parameter>", ["<vartype>", "id", "<mul_parameter>"])
    add_set(["segm", "main", "const", "var", "int", "dec", "chr", "str", "bln", "var", "strc", "id", "disp", "insp", "++", "--", 
             "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "brk", "rsm", "key", "}"], "<declaration_statement>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln"], "<declaration_statement>", ["<identifier_declaration>", "<declaration_statement>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<identifier_declaration>", ["<datatype>", "<iden_dec_tail>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<const_dec_tail>", ["<datatype>", "<const_dec_in>"])
    add_set([";", ","], "<init_statement>", ["null"])
    add_set(["=", "+=", "-=", "*=", "/=", "%="], "<init_statement>", ["<assignment_op>", "<value>"])
    add_set([ "str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--", "(", "none"], "<value>", ["<output_value>"])
    add_set(["str_lit", "chr_lit"], "<value>", ["<text_format>"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<array_elements>", ["<literals>"])
    add_set(["id", ",", ";"], "<struct_declaration_tail>", ["<instance_declaration>"])
    add_set(["str", "bln", "chr", "dec", "int", "var"], "<members_declaration>", ["<vartype>", "<struct_id>", "<struct_id_tail>", ";"])
    add_set(["int", "dec", "chr", "str", "bln", "var"], "<more_members>", ["<members_declaration>", "<more_members>"])
    add_set(["int", "dec", "chr", "str", "bln", "var"], "<instance_declaration>", ["<members_declaration>", "<more_members>"])
    add_set([",", ";"], "<struct_id_tail>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
        "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "brk", "rsm", "key", "def", "}"], "<statements>", ["<other_statements>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "var", "strc"], "<other_statements>", ["<declaration_statement>", "<statements>"])
    add_set(["++", "--"], "<other_statements>", ["<pre_unary>", "<statements>"])
    add_set(["if", "switch"], "<other_statements>", ["<conditional_statement>", "<statements>"])
    add_set(["for", "while", "do", "foreach"], "<other_statements>", ["<looping_statement>", "<statements>"])
    add_set(["def", "key", "}"], "<other_statements>", ["null"])
    add_set(["++", "--"], "<assignment_tail>", ["<unary_op>", "<more_unary>"])
    add_set(["[", ".",  "=", "+=", "-=", "*=", "/=", "%="], "<assignment_tail>", ["<assignment_id_tail>", "<assignment_op>", "<value>", "<more_assignment>"])
    add_set(["=", "+=", "-=", "*=", "/=", "%="], "<assignment_id_tail>", ["null"])
    add_set(["str_lit", "chr_lit"], "<output_value>", ["<text_format>", "<more_output>"])
    add_set(["int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--", "("], 
        "<output_value>", ["<tail_operand>", "<more_output>"])
    add_set([")", ";", ","], "<hold_id_tail>", ["null"])
    add_set([")", ";", ","], "<hold_id_tail2>", ["null"])
    add_set(["++", "--"], "<unary_statement>", ["<pre_unary>", "<more_unary>", ";"])
    add_set(["++", "--"], "<pre_unary>", ["<unary_op>", "<unary_id>"])
    add_set(["int_lit", "dec_lit", "true", "false"], "<return_value>", ["<expression_literals>","<ret_expression>"])
    add_set(["str_lit", "chr_lit"], "<return_value>", ["<text_format>"])
    add_set(["++", "--"], "<return_value>", ["<pre_unary>"])
    add_set([")", ";","+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!="], "<ret_id_tail>", ["null"])
    add_set(["++", "--"], "<ret_id_tail>", ["<unary_op>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
        "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "else", "}","brk"], "<elif_statement>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
        "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "}","brk"], "<else_statement>", ["null"])
    add_set(["def", "}"], "<more_key>", ["null"])
    add_set(["key", "def", "}"], "<conditional_body>", ["null"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
        "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach", "brk"], "<conditional_body>", ["<other_statements>", "<conditional_body>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", "--", 
        "ret", "exit", "if", "switch", "for", "while", "do", "brk", "rsm"], "<nested_foreach_body>", ["<foreach_body>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc"], "<foreach_body>", ["<declaration_statement>", "<foreach_body>"])
    add_set(["if", "switch"], "<foreach_body>", ["<conditional_statement>", "<foreach_body>"])
    add_set(["++", "--"], "<foreach_body>", ["<pre_unary>", "<foreach_body>"])
    add_set(["const", "var", "int", "dec", "chr", "str", "bln", "strc", "id", "disp", "insp", "++", 
        "--", "ret", "exit", "if", "switch", "for", "while", "do", "foreach"], "<looping_body>", ["<other_statements>", "<looping_body>"])
    add_set(["int", "dec", "chr", "var", "id"], "<initialization>", ["<for_datatype>", "id", "<id_tail>", "=", "<initial_value>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<initial_value>", ["<type_conversion>", "<expression>"]) 
    add_set(["!", "(", "str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<condition>", ["<not_op>", "<con_value>"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<con_value>", ["<con_operand>", "<con_expression>"])
    add_set([")", ";"], "<con_expression>", ["null"])
    add_set(["<", "<=", ">", ">=", "==", "!=", "&&", "||"], "<con_expression>", ["<comparison_operator>", "<con_value>"])
    add_set(["int_lit", "dec_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<con_operand>", ["<operand>", "<expression>"])
    add_set(["<", "<=", ">", ">=", "==", "!="], "<comparison_operator>", ["<relational_op>"])
    add_set(["&&", "||"], "<comparison_operator>", ["<logical_op>"])
    add_set(["++", "--", "id"], "<iteration>", ["<iteration_statement>", "<more_iteration>"])
    add_set(["++", "--"], "<iteration_statement>", ["<pre_unary>"])
    add_set([")", ","], "<iteration_value>", ["null"])
    add_set(["+", "-", "*", "/", "%"], "<iteration_value>", ["<arithmetic_op>", "<iteration_id>"])
    add_set(["&&", "||", ")", ";", "&", ","], "<expression>", ["null"])
    add_set(["+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!="], "<expression>", ["<operator>", "<not_op>", "<tail_operand>"])
    add_set(["int_lit", "dec_lit", "true", "false","chr_lit", "id", "int", "dec", "chr", "str", "bln", "++", "--"], "<tail_operand>", ["<operand>", "<expression>"])
    add_set(["int_lit", "dec_lit", "true", "false", "chr_lit"], "<operand>", ["<expression_literals>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<operand>", ["<type_conversion>"])
    add_set(["++", "--"], "<operand>", ["<pre_unary>"])
    add_set(["+", "-", "*", "/", "%"], "<operator>", ["<arithmetic_op>"])
    add_set(["<", "<=", ">", ">=", "==", "!="], "<operator>", ["<relational_op>"])
    add_set(["true", "false"], "<expression_literals>", ["<bln>"])
    add_set(["int_lit", "dec_lit", "str_lit", "chr_lit", "true", "false", "id", "int", "dec", "chr", "str", "bln", "++", "--", "("], "<not_op>", ["null"])
    add_set([";", ")", ","], "<concat_string>", ["null"])
    add_set(["str_lit", "chr_lit"], "<concat_value>", ["<text_format>"])
    add_set(["str", "bln", "chr", "dec", "int"], "<type_conversion>", ["<datatype>", "(", "<type_value>", ")"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<type_value>", ["<literals>"])
    add_set(["=", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<id_tail>", ["null"])
    add_set(["++", "--"], "<id_tail>", ["<unary_op>"])
    add_set(["=", "+=", "-=", "*=", "/=", "%=", "+", "-", "*", "/", "%", "&", "<", "<=", ">", ">=", "==", "!=", "&&", "||", ")", ";", ","], "<id_array_tail>", ["null"])
    add_set([")", ","], "<args>", ["null"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "true", "false"], "<args>", ["<literals>", "<expression>","<more_args>"])
    add_set(["++", "--"], "<args>", ["<pre_unary>", "<more_args>"])
    add_set(["int", "dec", "chr", "str", "bln"], "<vartype>", ["<datatype>"])
    add_set(["true", "false"], "<literals>", ["<bln>"])
    add_set([")", ";", ")", ","], "<more_output>", ["null"])
    add_set(["int", "dec", "chr", "str", "bln"], "<concat_value>", ["<type_conversion>"])
    add_set(["int", "dec", "chr", "str", "bln"], "<args>", ["<type_conversion>", "<expression>", "<more_args>"])
    add_set(["strc"], "<declaration_statement>", ["<struct_declaration>", "<declaration_statement>"])
    add_set([";", ")"],"<ret_expression>",["null"])
    add_set(["+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!="],"<ret_expression>",["<operator>","<not_op>","<tail_operand>"])
    add_set(["str_lit", "chr_lit", "int_lit", "dec_lit", "id", "++", "--", ")"],"<ret_args>",["<args>"])
