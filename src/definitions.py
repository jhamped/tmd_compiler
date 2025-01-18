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
