import string

state = []
lexeme = []
token = []

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
    'state_delim' : ['('], 
    'block_delim' : ['{'],    
    'def_delim' : [':'],
    'comma_delim' : [']', '(', '{', '"', '\'', '+', '-', '.'] + alphanumeric,
    'iden_delim' : all_operators + [';', '&', '>', '(', ')', '[', ']', '{', '}', '.', ','],
    'lit_delim' : [';', ',', '&', ')', '}', '!', '=', '|', ':'],
    'op_delim' : alphanumeric + ['(', '~', '/', '.', '+', '-'],
    'unary_delim' : alphanumeric + number_operator + ['(', ')', ';', ',', '~'],
    'paren_delim' : alphanumeric + [';', '!', '#', "'", '"', '(', ')', '+', '-', '.'],
    'paren1_delim' : arithmetic_operator + relational_operator + ['&', '|', '{', ')', ';', ','],
    'brace_delim' : alphanumeric + [';', '(', "'", '"', '{', '}', '+', '-', '.'],
    'semicolon_delim' : alphanumeric + ['(', '}', '+', '-', None],
    'bracket_delim' : alphanumeric + [']', ',', '+', '-', '.'],
    'bracket1_delim' : number_operator + alpha + [')', '=', ';', '&', '.'],
    'var_delim' : alpha + ['(', '+', '-'],
    'var1_delim' : ascii_def,
    'concat_delim' : alpha + ['(', '"', "'", '#'],
    'interpol_delim' : ['"'],
    'data_delim' : ['[', '('],
    'val_delim' : [';', ',', ')', '}', '!', '&', '=', '|'],
    'colon_delim' : alphanumeric + ['(', '+', '-'],
    'jmp_delim' : [';'],
    'key_delim' : alphanumeric + ["'", '"', '~', '(', '.'],
    'num_delim' : all_operators + [':', ';', ')', '}', ']', ','],
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
