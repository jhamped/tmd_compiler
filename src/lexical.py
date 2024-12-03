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
        nonlocal col
        while(char := next_char()) in whitespace:
            if char == '\n':
                new_line()
            elif char == '\t':
                col += 3
            get_char()

    def skip_single_comment():  
        while get_char() not in ['\n', None]:
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
        console.insert(tk.END, f"       line {line}, column {col-(len(error_key)-1)}\n", "ln_col")

    def get_string():
        string = '"'
        while True:
            char = get_char()
            if char is None:  
                error_message("Expected: \"", string)
                break

            if char == '"': 
                string += char
                lexeme.append(string)
                token.append('str_lit')
                break
            elif char == '\\': 
                esc = get_char()
                if esc in ['\\', '"', 'n', 't']: 
                    string += '\\' + esc
                else:
                    error_message(f"Invalid escape sequence: \\{esc}", string)
            else:
                string += char


    def get_character():
        character = "'"
        while True:
            char = get_char()
            if char is None:  
                error_message("Expected: '", character)
                break

            if char == "'":
                character += char
                if (len(key) == 3):
                    lexeme.append(character)
                    token.append('chr_lit')
                else:
                    error_message("Character literals must only contain one character", character)
                break
            else:
                character += char
                continue
                
    def get_num():
        nonlocal key
        def check_num(num):
            if num.isdigit():
                if len(num) <= 10:
                    lexeme.append(key)
                    token.append('int_lit')
                else:
                    error_message(f"{key} exceeds maximum length of 10 digits", key)
            elif '.' in num:
                literal = num.split('.')
                if len(literal) == 2 and literal[0].isdigit() and literal[1].isdigit():
                    if len(literal[0]) > 10:
                        error_message(f"{key} exceeds maximum length of 10 integers", key)
                    if len(literal[1]) > 7:
                        error_message(f"{key} exceeds maximum length of 7 decimal places", key)
                    if len(literal[0]) <= 10 and len(literal[1]) <= 7:
                        lexeme.append(key)
                        token.append('dec_lit')
            else:
                error_message(f"Invalid: {key}", key)
            return

        if key.startswith('~'):
            check_num(key[1:])
        else:
            check_num(key)
        
    def get_id():
        if len(key) > 30:
            error_message(f"Identifier {key} exceeds maximum length of 30 characters", key)
        elif key.isalnum() or '_' in key:
            lexeme.append(key)
            token.append('id')
        else:
            error_message(f"Invalid identifier: {key}", key)
    
    def append_key():
        lexeme.append(key) 
        token.append(key)

    def get_key():
        nonlocal key
        while next_char() not in whitespace:
            key += get_char()

    def check_delim(delim, expected):
        nonlocal key
        skip_whitespace()
        append_key()
        if next_char() not in delim:
            #change color of expected
            error_message(f"Expected: {expected} after {key}", key)
        return
    
    def check_sequence(sequence):
        nonlocal key, matched
        key += sequence[0]
        get_char()
        matched = True
        for seq_char in sequence[1:]:
            if next_char() == seq_char:
                key += seq_char
                get_char()
            else:
                matched = False
                break

    def check_transition_words(transition):
        nonlocal key, matched
        ctr = len(transition)

        for sequence, delim in transition.items():
            if isinstance(delim, dict):
                if next_char() == sequence[0]:
                    check_sequence(sequence)
                    check_transition_words(delim)
                else:
                    continue
            else:   
                if len(sequence) > 0:
                    if next_char() == sequence[0]:
                        check_sequence(sequence)
                    elif ctr == 1:
                        matched = False
                    else:
                        ctr -= 1
                        continue
                else:
                    if next_char() not in whitespace and (next_char().isalnum() or next_char() == '_'):
                        continue
                
                if next_char() not in whitespace and (next_char().isalnum() or next_char() == '_'):
                    matched = False
                    get_key()
                    get_id()
                if matched:
                    check_delim(delim[0], delim[1])
                    break

    def check_transition_symbols(transition):
        nonlocal key, matched
        ctr = len(transition)

        for sequence, delim in transition.items():
            if len(sequence) > 0:
                if next_char() == sequence[0]:
                    key += sequence[0]
                    get_char()
                    matched = True
                elif ctr == 1:
                    matched = False
                else:
                    ctr -= 1
                    continue
            else:
                matched = True

            if next_char() not in whitespace and next_char() in punc_symbols:
                matched = False
                get_key()
                error_message(f"{key} => invalid operator", key)
            if matched:
                check_delim(delim)

#---------------------------------------------------------------------------------------
        
    while (char := get_char()) is not None:
        if char == '/' and next_char() == '/': #single-line comments
            get_char() 
            skip_single_comment()

        elif char == '/' and next_char() == '*': #multi-line comments
            get_char() 
            skip_multi_comment()

        elif char == '\n': #get new line
            new_line()
        
        elif char == '"': #string literal
            get_string()

        elif char == "'": #char literal
            get_character()

        elif char == '_': #invalid iden (remove)
            key = char
            get_key()
            error_message(f"Invalid identifier: {key}", key)
        
        elif char.isdigit() or char == '~': #int and dec literals
            key = char
            get_key()
            get_num()

        elif char in transition_map_words: #reserved words
            key = char
            matched = False
            check_transition_words(transition_map_words[char])

        elif char in transition_map_symbols: #reserved symbols
            key = char
            matched = False
            check_transition_symbols(transition_map_symbols[char])        

    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i])) 
