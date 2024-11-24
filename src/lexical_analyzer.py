from definitions import *
import tkinter as tk
import re

lexeme = []
token = []

def lexer(code, console, table):
    pos = 0
    col = 0
    line = 1

    def get_char():  
        nonlocal pos, col
        if pos < len(code):
            curr = code[pos]
            pos += 1
            col += 1
            return curr
        return None 
    
    def next_char():
        if pos < len(code):
            return code[pos]
        return None
    
    def skip_whitespace():  
        while(char := next_char()) in whitespace:
            if char == "\n":
                new_line()
            get_char()

    def skip_single_comment():  
        while(char := get_char()) not in ['\n', None]:
            pass

    def skip_multi_comment():
        while True:
            char = get_char()
            if char == '*' and next_char() == '/':
                get_char() 
                break

    def new_line():
        nonlocal col, line
        col = 0
        line += 1

    def error_message(error, error_key):
        nonlocal line, col
        console.insert(tk.END, "Error: ", "error")
        console.insert(tk.END, f"{error}\n")
        print(col)
        console.insert(tk.END, f"       line {line}, column {col-(len(error_key)-1)}\n", "ln_col")

    def get_string():
        string = "\""
        while True:
            char = get_char()
            if char == '"':
                string += char
                lexeme.append(string)
                token.append('str_lit')
                break
            else:
                string += char
                continue

    def get_character():
        key = "'"
        while True:
            char = get_char()
            if char == '\'':
                key += char
                if (len(key) == 3):
                    lexeme.append(key)
                    token.append('chr_lit')
                else:
                    error_message("Character literals must only contain one character", key)
                break
            else:
                key += char
                continue
                
    def get_num():
        if key.isdigit() or '.' in key or '~' in key:
            if re.match(r'^\d{1,10}$', key):
                lexeme.append(key)
                token.append('int_lit')
            elif re.match(r'^~\d{1,10}$', key):
                lexeme.append(key)
                token.append('int_lit')
            elif re.match(r'^\d{1,10}+\.\d{1,7}+$', key):
                lexeme.append(key)
                token.append('dec_lit')
            elif re.match(r'^\d{11,}$', key):
                error_message(f"{key} exceeds maximum length of 10 digits", key)
            elif re.match(r'^~\d{11,}$', key):
                error_message(f"{key} exceeds maximum length of 10 digits", key)
            elif re.match(r'^\d+\.\d{8,}+$', key):
                error_message(f"{key} exceeds maximum length of 7 decimal places", key)
            else:
                error_message(f"Invalid: {key}", key)     
        else:
            error_message(f"Invalid identifier: {key}", key)
        
    def get_id():
        if re.match(r'[a-zA-Z0-9_]{1,30}$', key):
            lexeme.append(key)
            token.append('id')
        elif len(key) > 30:
            error_message(f"Identifier {key} exceeds maximum length of 30 characters", key)
        else:
            error_message(f"Invalid identifier: {key}", key)

    def get_key(char):
        key = char
        while next_char() not in whitespace:
            key += get_char()
        return key
    
    def check_keyword_delim():
        check = {
            True: lambda: (lexeme.append(key), token.append(key)),
            False: lambda: (lexeme.append(key), token.append(key), error_message(f"{key} => wrong delimiter", key))
        }
        
        skip_whitespace()
        nextchr = next_char()
        match key:
            case 'bln': check[nextchr in key_delims['data_delim']]()
            case 'brk': check[nextchr in key_delims['jmp_delim']]()
            case 'chr': check[nextchr in key_delims['data_delim']]()
            case 'const': check[nextchr in alpha]()
            case 'dec': check[nextchr in key_delims['data_delim']]()
            case 'def': check[nextchr in key_delims['def_delim']]()
            case 'disp': check[nextchr in key_delims['state_delim']]()
            case 'do': check[nextchr in key_delims['block_delim']]()
            case 'elif': check[nextchr in key_delims['state_delim']]()
            case 'else': check[nextchr in key_delims['block_delim']]()
            case 'exit': check[nextchr in key_delims['jmp_delim']]()
            case 'false': check[nextchr in key_delims['val_delim']]()
            case 'for': check[nextchr in key_delims['state_delim']]()
            case 'foreach': check[nextchr in key_delims['state_delim']]()
            case 'if': check[nextchr in key_delims['state_delim']]()
            case 'in': check[nextchr in alpha]()
            case 'insp': check[nextchr in key_delims['state_delim']]()
            case 'int': check[nextchr in key_delims['data_delim']]()
            case 'bln': check[nextchr in key_delims['key_delim']]()
            case 'main': check[nextchr in key_delims['state_delim']]()
            case 'none': check[nextchr in key_delims['val_delim']]()
            case 'ret': check[nextchr in key_delims['key_delim']]()
            case 'rsm': check[nextchr in key_delims['jmp_delim']]()
            case 'segm': check[nextchr in alpha]()
            case 'str': check[nextchr in key_delims['data_delim']]()
            case 'strc': check[nextchr in alpha]()
            case 'switch': check[nextchr in key_delims['state_delim']]()
            case 'true': check[nextchr in key_delims['val_delim']]()
            case 'var': check[nextchr in alpha]()
            case 'while': check[nextchr in key_delims['state_delim']]()

    def check_symbol_delim():
        check = {
            True: lambda: (lexeme.append(key), token.append(key)),
            False: lambda: (lexeme.append(key), token.append(key), error_message(f"{key} => wrong delimiter", key))
        }

        key = char 
        nextchr = next_char()

        def get_next():
            nonlocal key, nextchr
            key += nextchr
            get_char()
            skip_whitespace()
            nextchr = next_char()
            return nextchr

        def check_double(next, a, b):
            nonlocal key, nextchr
            if nextchr == next:
                get_next()
                check[nextchr in key_delims[a]]()
            else:
                check[nextchr in key_delims[b]]()
        
        def check_triple(next, a, next1, b, c):
            nonlocal key, nextchr
            if nextchr == next:
                get_next()
                check[nextchr in key_delims[a]]()
            elif nextchr == next1:
                get_next()
                check[nextchr in key_delims[b]]()
            else:
                check[nextchr in key_delims[c]]()

        match char:
            case '=': check_double('=', 'relate_delim', 'asn_delim') 
            case '+': check_triple('+', 'unary_delim', '=', 'relate2_delim', 'op_delim')
            case '-': check_triple('-', 'unary_delim', '=', 'relate2_delim', 'op_delim')
            case '*': check_double('=', 'relate2_delim', 'op_delim') 
            case '/': check_double('=', 'relate2_delim', 'op_delim') 
            case '%': check_double('=', 'relate2_delim', 'op_delim') 
            case '&': check_double('&', 'relate_delim', 'concat_delim')  
            case '!': check_double('=', 'relate_delim', 'relate_delim')
            case '<': check_triple('<', 'var_delim', '=', 'relate1_delim', 'relate2_delim')
            case '>': check_triple('>', 'var1_delim', '=', 'relate1_delim', 'relate2_delim')
            case '[': check[nextchr in key_delims['bracket_delim']]()
            case ']': check[nextchr in key_delims['bracket1_delim']]()
            case '{': check[nextchr in key_delims['brace_delim']]()
            case '}': check[nextchr in key_delims['brace1_delim']]()
            case '[': check[nextchr in key_delims['bracket_delim']]()
            case '(': check[nextchr in key_delims['paren_delim']]()
            case ')': check[nextchr in key_delims['paren1_delim']]()
            case ',': check[nextchr in key_delims['comma_delim']]()
            case ';': check[nextchr in key_delims['semicolon_delim']]()
            case ':': check[nextchr in key_delims['colon_delim']]()
            case '#': check[nextchr in key_delims['interpol_delim']]()
            case '|': 
                if nextchr == '|':
                    get_next
                    check[nextchr in key_delims['relate_delim']]()
                else:
                    error_message(f"{key} => invalid symbol", key)
            case _:
                error_message(f"{key} => invalid symbol", key)

            
    while (char := get_char()) is not None:
        skip_whitespace()  

        if char == '/' and next_char() == '/':
            get_char() 
            skip_single_comment()

        elif char == '/' and next_char() == '*':
            get_char() 
            skip_multi_comment()

        elif char == '\n':
            new_line()
        
        elif char == '"':
            get_string()

        elif char == '\'':
            get_character()
        
        elif char.isdigit() or char == '~':
            key = get_key(char)
            get_num()

        elif char.isalpha():
            key = get_key(char)
            if key in keywords:
                check_keyword_delim()
            else:
                get_id()

        elif char in reg_symbols:
            check_symbol_delim()

        elif char == '_':
            key = "_"
            while next_char() not in whitespace:
                key += get_char()
            error_message(f"Invalid identifier: {key}", key)

    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i])) 

    
