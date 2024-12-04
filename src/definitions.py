import string

arithmetic_operator = ['+', '-', '*', '/', '%']
relational_operator = ['==', '!=', '<', '<=', '>', '>=']
logical_operator = ['&&', '||', '!']
unary_operator = ['++', '--']
assignment_operator = ['=', '+=', '-=', '*=', '/=', '%=']
number_operator = arithmetic_operator + relational_operator + logical_operator + unary_operator
all_operators = number_operator + assignment_operator

symbols = ['!', '#', '%', '&', '*', '(', ')', '-', '=', '+', '[', ']', '{', '}', ':', ';', ',', '<', '>', '.', '/', '~', '|']
more_symbols = ['@', '$', '^', '_', '?']
punc_symbols = more_symbols + symbols
quote_symbols = ["'", '"']

alpha = list(string.ascii_letters)
alphanumeric = list(string.ascii_letters + string.digits)
ascii_def = alphanumeric + punc_symbols + quote_symbols
identifier = alphanumeric + ['_']

# Regular expression
keywords = ['strc', 'segm', 'main', 'bln', 'chr', 'int', 'dec', 'str', 'var', 'const', 'true', 'false', 'disp', 'insp', 'if', 
            'elif', 'else', 'switch', 'key', 'def', 'for', 'foreach', 'in', 'do', 'while', 'brk', 'rsm', 'exit', 'ret', 'none']
reg_symbols =  number_operator + assignment_operator + symbols

whitespace = [' ', '\t', '\n']

# Delimiters
key1_delims = {
    'state_delim' : whitespace + ['(', '/'], 
    'block_delim' : whitespace + ['{', '/'],
    'def_delim' : whitespace + [':', '/'],
    'comma_delim' : [']', '(', '{', '"', '\'', '/'] + whitespace + alphanumeric + unary_operator,
    'iden_delim' : whitespace + all_operators + [';', '&', '>', '(', ')', '[', ']', '{', '.', ',', '/'],
    'lit_delim' : whitespace + [';', ',', '&', '/'],
    'op_delim' : whitespace + alphanumeric + ['(', '~', '/'],
    'unary_delim' : whitespace + alphanumeric + ['(', ')', ';', ',', '~', '/'],
    'paren_delim' : whitespace + alphanumeric + unary_operator + [';', '!', '#', "'", '"', '(', ')', '/'],
    'paren1_delim' : whitespace + arithmetic_operator + relational_operator + ['&', '|', '{', ')', ';', '/'],
    'brace_delim' : whitespace + alphanumeric + unary_operator + [';', '(', "'", '"', '{', '}', '/'],
    'semicolon_delim' : whitespace + alphanumeric + unary_operator + whitespace + ['(', '}', '/', None],
    'bracket_delim' : whitespace + alphanumeric + unary_operator + [']', ',', '/'],
    'bracket1_delim' : whitespace + number_operator + alpha + [')', '=', ';', '&', '/'],
    'var_delim' : whitespace + alpha + unary_operator + ['(', '/'],
    'var1_delim' : whitespace + ascii_def,
    'concat_delim' : whitespace + alpha + ['(', '"', "'", '#', '/'],
    'interpol_delim' : whitespace + ['"', '/'],
    'data_delim' : whitespace + alpha + ['[', '(', '/'],
    'val_delim' : whitespace + [';', ',', ')', '}', '/'],
    'colon_delim' : whitespace + alphanumeric + unary_operator + ['(', '/'],
    'jmp_delim' : whitespace + [';', '/'],
    'key_delim' : whitespace + alphanumeric + ["'", '"', '~', '/', '('],
    'empty_delim' : whitespace + ['']
}

key2_delims = {
    'num_delim' : number_operator + key1_delims['comma_delim'],
    'relate_delim' : key1_delims['op_delim'] + ['!', "'", '"'],
    'relate1_delim' : key1_delims['op_delim'] + ['!'],
    'brace1_delim' : key1_delims['semicolon_delim'] + unary_operator + [';', ',']
}

key3_delims = {
    'asn_delim' : key2_delims['relate_delim'] + ['{', '#']
}

key_delims = key1_delims | key2_delims | key3_delims

transition_map_words = {
    'b': {
        'ln': [key_delims['data_delim'], "[letter, '[', '(']"], 
        'rk': [key_delims['jmp_delim'], "[';']"]},
    'c': {
        'hr': [key_delims['data_delim'], "[letter, '[', '(']"], 
        'onst': [alpha, "[letter]"]},
    'd': {
        'e': {
            'c': [key_delims['data_delim'], "[letter, '[', '(']"], 
            'f': [key_delims['def_delim'], "[':']"]},  
        'isp': [key_delims['state_delim'], "['(']"], 
        'o': [key_delims['block_delim'], "['{']"]},
    'e': {
        'l': {
            'if': [key_delims['state_delim'], "['(']"], 
            'se': [key_delims['block_delim'], "['{']"]},
        'xit': [key_delims['jmp_delim'], "[';']"]},
    'f': {
        'alse': [key_delims['val_delim'], "[';', ',', ')', '}']"], 
        'or': {
            '': [key_delims['state_delim'], "['(']"], 
            'each': [key_delims['state_delim'], "['(']"]}},
    'i': {
        'f': [key_delims['state_delim'], "['(']"], 
        'n': {
            '': [alpha, "[letter]"], 'sp': [key_delims['state_delim'], "['(']"], 
            't': [key_delims['data_delim'], "[letter, '[', '(']"]}},
    'k': {
        'ey': [alpha, "[letter]"]},
    'm': {
        'ain': [key_delims['state_delim'], "['(']"]},
    'n': {
        'one': [key_delims['val_delim'], "[';', ',', ')', '}']"]},
    'r': {
        'et': [alpha, "[letter]"], 
        'sm': [key_delims['jmp_delim'], "[';']"]},
    's': {
        'egm': [alpha, "[letter]"],
        'tr': {
            '': [key_delims['data_delim'],  "[letter, '[', '(']"], 
            'c': [alpha,  "[letter]"]},
        'witch': [key_delims['state_delim'],  "['(']"]},
    't': {
        'rue': [key_delims['val_delim'], "[';', ',', ')', '}']"]},
    'v': {
        'ar': [alpha, "[letter]"]},
    'w': {
        'hile': [key_delims['state_delim'], "['(']"]}
}

transition_map_symbols = {
    '=': {
        '': [key_delims['asn_delim'], "[letter, number, '(', '~', '!', "'", '"'. '{']"], 
        '=': [key_delims['relate_delim'], "[letter, number, '(', '~', '!', "'", '"']"]},
    '+': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~']"], 
        '+': [key_delims['unary_delim'], "[letter, number, '(', ')', ';', ',', '~']"], 
        '=': [key_delims['op_delim'], "[letter, number, '(', '~']"]},
    '-': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~']"], 
        '-': [key_delims['unary_delim'], "[letter, number, '(', ')', ';', ',', '~']"], 
        '=': [key_delims['op_delim'], "[letter, number, '(', '~']"]},
    '*': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~']"], 
        '=': [key_delims['op_delim'], "[letter, number, '(', '~']"]},
    '/': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~']"], 
        '=': [key_delims['op_delim'], "[letter, number, '(', '~']"]},
    '%': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~']"], 
        '=': [key_delims['op_delim'], "[letter, number, '(', '~']"]},
    '&': {
        '': [key_delims['concat_delim'], "[letter, '(', '"', "'", '#']"], 
        '&': [key_delims['relate_delim'], "[letter, number, '(', '~', '!', "'", '"']"]},
    '|': {
        '|': [key_delims['relate_delim'], "[letter, number, '(', '~', '!', "'", '"']"]},
    '!': {
        '': [key_delims['relate_delim'], "[letter, number, '(', '~', '!', "'", '"']"], 
        '=': [key_delims['relate_delim'], "[letter, number, '(', '~', '!', "'", '"']"]},
    '<': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~', '!', "'", '"'. '{']"], 
        '<': [key_delims['var_delim'], "[letter, '+', '-', ']', ',']"], 
        '=': [key_delims['relate1_delim'], "[letter, number, '(', '~', '!']"]},
    '>': {
        '': [key_delims['op_delim'], "[letter, number, '(', '~', '!', "'", '"'. '{']"], 
        '>': [key_delims['var1_delim'], "[ASCII Character]"], 
        '=': [key_delims['relate1_delim'], "[letter, number, '(', '~', '!']"]},
    '[': {
        '': [key_delims['bracket_delim'], "[letter, number, ']', ',', '+', '-']"]},
    ']': {
        '': [key_delims['bracket1_delim'], "[operator, ')', '=', ';', '&', '>']"]},
    '{': {
        '': [key_delims['brace_delim'], "[letter, number, '+', '-', ';', '(', ''', '\"', '{', '}']"]},
    '}': {
        '': [key_delims['brace1_delim'], "[letter, number, '+', '-', ';', '(', '}', ';', ',']"]},
    '(': {
        '': [key_delims['paren_delim'], "[letter, number, '+', '-', ';', '!', '#', "'", '"', '(', ')']"]},
    ')': {
        '': [key_delims['paren1_delim'], "['+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', '{', ')', ';']"]},
    ',': {
        '': [key_delims['comma_delim'], "[letter, number, '+', '-', ']', '(', '{', '\"', ''']"]},
    ';': {
        '': [key_delims['semicolon_delim'], "[letter, number, '+', '-', '(', '}']"]},
    ':': {
        '': [key_delims['colon_delim'], "[letter, number, '+', '-', '(']"]},
    '#': {
        '': [key_delims['interpol_delim'], "['\"']"]},
}
