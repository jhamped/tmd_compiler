from definitions import *
import tkinter as tk
import re

state = []
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
        print(col)
        console.insert(tk.END, f"       line {line}, column {col-(len(error_key)-1)}\n", "ln_col")

    def get_string():
        string = '"'
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
            if char == "'":
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

    def add_key(stateNum, stateNum1):
        nonlocal key
        state.append(f"{next_char()} : {stateNum}-{stateNum1}")
        key += get_char()

    def get_key():
        nonlocal key
        while next_char() not in whitespace:
            key += get_char()

    def get_lexeme():
        nonlocal key
        while next_char() not in whitespace:
            key += get_char()
        get_id()

    def get_symbol(delim, expected, stateNum1, stateNum2):
        nonlocal matched
        if next_char() in whitespace or next_char() in delim:
            matched = True
            check_delim(delim, expected)
            append_state("end", stateNum1, stateNum2)

    def check_delim(delim, expected):
        nonlocal key
        skip_whitespace()
        append_key()
        if next_char() not in delim:
            error_message(f"Expected: {expected} after {key}", key)

    def check_if_id(delim, expected, stateNum, stateNum1, reserved):
        nonlocal matched
        if reserved == "word":
            if next_char() not in whitespace and (next_char().isalnum() or next_char() == '_'):
                matched = False
                return
        else:
            if next_char() not in whitespace and next_char() in punc_symbols:
                matched = False
                return
  
        state.append(f"end : {stateNum}-{stateNum1}")
        check_delim(delim, expected)

    def append_state(stateChar, stateNum, stateNum1):
        state.append(f"{stateChar} : {stateNum}-{stateNum1}")
    
#---------------------------------------------------------------------------------------
            
    while (char := get_char()) is not None:
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

        elif char == "'":
            get_character()

        elif char == '_':
            key = char
            while next_char() not in whitespace:
                key += get_char()
            error_message(f"Invalid identifier: {key}", key)
        
        elif char.isdigit() or char == '~':
            key = char
            while next_char() not in whitespace:
                key += get_char()
            get_num()

        elif char == 'b':
            key = char
            matched = False
            append_state(char, 0, 1)

            if next_char() == 'l':
                add_key(1, 2)
                if next_char() == 'n':
                    add_key(2, 3)
                    matched = True
                    check_if_id(key_delims['data_delim'], "letter, [, (", 3, 4, "word")
            elif next_char() == 'r':
                add_key(1, 5)
                if next_char() == 'k':
                    add_key(5, 6)
                    matched = True
                    check_if_id(key_delims['jmp_delim'], ";", 6, 7, "word")
            if not matched:
                get_lexeme()

        elif char == 'c':
            key = char
            matched = False
            append_state(char, 0, 8)

            if next_char() == 'h':
                add_key(8, 9)
                if next_char() == 'r':
                    add_key(9, 10)
                    matched = True
                    check_if_id(key_delims['data_delim'], "letter, [, (", 10, 11, "word")
            elif next_char() == 'o':
                add_key(8, 12)
                if next_char() == 'n':
                    add_key(12, 13)
                    if next_char() == 's':
                        add_key(13, 14)
                        if next_char() == 't':
                            add_key(14, 15)
                            matched = True
                            check_if_id(alpha, "data type keyword", 15, 16, "word")
            if not matched:
                get_lexeme()

        elif char == 'd':
            key = char
            matched = False
            append_state(char, 0, 17)

            if next_char() == 'e':
                add_key(17, 18)
                if next_char() == 'c':
                    add_key(18, 19)
                    matched = True
                    check_if_id(key_delims['data_delim'], "letter, [, (", 19, 20, "word")
                elif next_char() == 'f':
                    add_key(18, 21)
                    matched = True
                    check_if_id(key_delims['def_delim'], ":", 21, 22, "word")
            elif next_char() == 'i':
                add_key(17, 23)
                if next_char() == 's':
                    add_key(23, 24)
                    if next_char() == 'p':
                        add_key(24, 25)
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 25, 26, "word")
            elif next_char() == 'o':
                add_key(17, 27)
                matched = True
                check_if_id(key_delims['block_delim'], "{", 27, 28, "word")
            if not matched:
                get_lexeme()

        elif char == 'e':
            key = char
            matched = False
            append_state(char, 0, 29)

            if next_char() == 'l':
                add_key(29, 30)
                if next_char() == 'i':
                    add_key(30, 31)
                    if next_char() == 'f':
                        add_key(31, 32)
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 32, 33, "word")
                elif next_char() == 's':
                    add_key(30, 34)
                    if next_char() == 'e':
                        add_key(34, 35)
                        matched = True
                        check_if_id(key_delims['block_delim'], "{", 35, 36, "word")
            elif next_char() == 'x':
                add_key(29, 37)
                if next_char() == 'i':
                    add_key(37, 38)
                    if next_char() == 't':
                        add_key(38, 39)
                        matched = True
                        check_if_id(key_delims['jmp_delim'], ";", 39, 40, "word")
            if not matched:
                get_lexeme()

        elif char == 'f':
            key = char
            matched = False
            append_state(char, 0, 41)

            if next_char() == 'a':
                add_key(41, 42)
                if next_char() == 'l':
                    add_key(42, 43)
                    if next_char() == 's':
                        add_key(43, 44)
                        if next_char() == 'e':
                            add_key(44, 45)
                            matched = True
                            check_if_id(key_delims['val_delim'], ";, ,, ), }", 45, 46, "word")
            elif next_char() == 'o':
                add_key(41, 47)
                if next_char() == 'r':
                    add_key(47, 48)
                    if next_char() != 'e':
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 48, 49, "word")
                    else:
                        add_key(48, 50)
                        if next_char() == 'a':
                            add_key(50, 51)
                            if next_char() == 'c':
                                add_key(51, 52)
                                if next_char() == 'h':
                                    add_key(52, 53)
                                    matched = True
                                    check_if_id(key_delims['state_delim'], "(", 53, 54, "word")  
            if not matched:
                get_lexeme()

        elif char == 'i':
            key = char
            matched = False
            append_state(char, 0, 55)

            if next_char() == 'f':
                add_key(55, 56)
                matched = True
                check_if_id(key_delims['state_delim'], "(", 56, 57, "word")
            elif next_char() == 'n':
                add_key(55, 58)
                if next_char() != 's' or next_char() != 't':
                    matched = True
                    check_if_id(alpha, "identifier", 58, 59, "word")
                elif next_char() == 's':
                    add_key(58, 60)
                    if next_char() == 'p':
                        add_key(60, 61)
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 61, 62, "word")
                elif next_char() == 't':
                    add_key(58, 63)
                    matched = True
                    check_if_id(key_delims['data_delim'], "letter, [, (", 63, 64, "word")
            if not matched:
                get_lexeme()

        elif char == 'k':
            key = char
            matched = False
            append_state(char, 0, 65)

            if next_char() == 'e':
                add_key(65, 66)
                if next_char() == 'y':
                    add_key(66, 67)
                    matched = True
                    check_if_id(key_delims['key_delim'], "letter, number, ', \", ~", 67, 68, "word")
            if not matched:
                get_lexeme()

        elif char == 'm':
            key = char
            matched = False
            append_state(char, 0, 69)

            if next_char() == 'a':
                add_key(69, 70)
                if next_char() == 'i':
                    add_key(70, 71)
                    if next_char() == 'n':
                        add_key(71, 72)
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 72, 73, "word")
            if not matched:
                get_lexeme()

        elif char == 'n':
            key = char
            matched = False
            append_state(char, 0, 74)

            if next_char() == 'o':
                add_key(74, 75)
                if next_char() == 'n':
                    add_key(75, 76)
                    if next_char() == 'e':
                        add_key(76, 77)
                        matched = True
                        check_if_id(key_delims['val_delim'], ";, ,, ), }", 77, 78, "word")
            if not matched:
                get_lexeme()

        elif char == 'r':
            key = char
            matched = False
            append_state(char, 0, 79)

            if next_char() == 'e':
                add_key(79, 80)
                if next_char() == 't':
                    add_key(80, 81)
                    matched = True
                    check_if_id(key_delims['key_delim'], "letter, number, ', \", ~", 81, 82, "word")
            elif next_char() == 's':
                add_key(79, 83)
                if next_char() == 'm':
                    add_key(83, 84)
                    matched = True
                    check_if_id(key_delims['jmp_delim'], ";", 84, 85, "word")
            if not matched:
                get_lexeme()

        elif char == 's':
            key = char
            matched = False
            append_state(char, 0, 86)

            if next_char() == 'e':
                add_key(86, 87)
                if next_char() == 'g':
                    add_key(87, 88)
                    if next_char() == 'm':
                        add_key(88, 89)
                        matched = True
                        check_if_id(alpha, "identifier", 89, 90, "word")
            elif next_char() == 't':
                add_key(86, 91)
                if next_char() == 'r':
                    add_key(91, 92)
                    if next_char() != 'c':
                        matched = True
                        check_if_id(key_delims["data_delim"], "letter, [, (", 92, 93, "word")
                    else:
                        add_key(92, 94)
                        matched = True
                        check_if_id(alpha, "identifier", 94, 95, "word")
            elif next_char() == 'w':
                add_key(86, 96)
                if next_char() == 'i':
                    add_key(96, 97)
                    if next_char() == 't':
                        add_key(97, 98)
                        if next_char() == 'c':
                            add_key(98, 99)
                            if next_char() == 'h':
                                add_key(99, 100)
                                matched = True
                                check_if_id(key_delims['state_delim'], "(", 100, 101, "word")
            if not matched:
                get_lexeme()

        elif char == 't':
            key = char
            matched = False
            append_state(char, 0, 102)

            if next_char() == 'r':
                add_key(102, 103)
                if next_char() == 'u':
                    add_key(103, 104)
                    if next_char() == 'e':
                        add_key(104, 105)
                        matched = True
                        check_if_id(key_delims['val_delim'], ";, ,, ), }", 105, 106, "word")
            if not matched:
                get_lexeme()

        elif char == 'v':
            key = char
            matched = False
            append_state(char, 0, 107)

            if next_char() == 'a':
                add_key(107, 108)
                if next_char() == 'r':
                    add_key(108, 109)
                    matched = True
                    check_if_id(alpha, "identifier", 109, 110, "word")
            if not matched:
                get_lexeme()

        elif char == 'w':
            key = char
            matched = False
            append_state(char, 0, 111)

            if next_char() == 'h':
                add_key(111, 112)
                if next_char() == 'i':
                    add_key(112, 113)
                    if next_char() == 'l':
                        add_key(113, 114)
                        if next_char() == 'e':
                            add_key(114, 115)
                            matched = True
                            check_if_id(key_delims['state_delim'], "(", 115, 116, "word")
            if not matched:
                get_lexeme()

        elif char == '=':
            key = char 
            matched = False
            append_state(char, 0, 117)

            if next_char() == '=':
                add_key(117, 119)
                matched = True
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 119, 120, "symbol")
            else:
                get_symbol(key_delims['asn_delim'], "letter, number, (, ~, !, ', \", {, #", 117, 118)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '+':
            key = char     
            matched = False
            append_state(char, 0, 121)

            if next_char() == '+':
                add_key(121, 123)
                matched = True
                check_if_id(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 123, 124, "symbol")
            elif next_char() == '=':
                add_key(121, 125)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 125, 126, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 121, 122)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '-':
            key = char     
            matched = False
            append_state(char, 0, 127)

            if next_char() == '-':
                add_key(127, 129)
                matched = True
                check_if_id(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 129, 130, "symbol")
            elif next_char() == '=':
                add_key(127, 131)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 131, 132, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 127, 128)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)
                    
        elif char == '*':
            key = char     
            matched = False
            append_state(char, 0, 133)

            if next_char() == '=':
                add_key(133, 135)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 135, 136, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 133, 134)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '/':
            key = char     
            matched = False
            append_state(char, 0, 137)

            if next_char() == '=':
                add_key(137, 139)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 139, 140, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 137, 138)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '%':
            key = char     
            matched = False
            append_state(char, 0, 141)

            if next_char() == '=':
                add_key(141, 143)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 143, 144, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 141, 142)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '&':
            key = char  
            matched = False
            append_state(char, 0, 145)

            if next_char() == '&':
                add_key(145, 147)
                matched = True
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 147, 148, "symbol")
            else:
                get_symbol(key_delims['concat_delim'], "letter, (, \", ', #", 145, 146)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)
                
        elif char == '|':
            key = char
            matched = False
            append_state(char, 0, 149)

            if next_char() == '|':
                add_key(149, 150)
                matched = True
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 150, 151, "symbol")
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '!':
            key = char    
            matched = False
            append_state(char, 0, 152)

            if next_char() == '=':
                add_key(152, 154)
                matched = True
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 154, 155, "symbol")
            else:
                get_symbol(key_delims['relate_delim'], "letter, (, \", ', #", 152, 153)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '<':
            key = char  
            matched = False
            append_state(char, 0, 156)

            if next_char() == '<':
                add_key(156, 158)
                matched = True
                check_if_id(key_delims['var_delim'], "letter, +, -, ], ,", 158, 159, "symbol")
            elif next_char() == '=':
                add_key(156, 160)
                matched = True
                check_if_id(key_delims['relate1_delim'], "letter, number, (, ~, !", 160, 161, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 156, 157)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '>':
            key = char    
            matched = False
            append_state(char, 0, 162)

            if next_char() == '>':
                add_key(162, 164)
                matched = True
                check_if_id(key_delims['var1_delim'], "ASCII Character", 164, 164, "symbol")
            elif next_char() == '=':
                add_key(162, 166)
                matched = True
                check_if_id(key_delims['relate1_delim'], "letter, number, (, ~, !", 166, 167, "symbol")
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 162, 163)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '[':
            key = char
            matched = False
            append_state(char, 0, 168)

            get_symbol(key_delims['bracket_delim'], "letter, number, ], ,, +, -", 168, 169)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ']':
            key = char
            matched = False
            append_state(char, 0, 170)

            get_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '>'", 170, 171)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '{':
            key = char
            matched = False
            append_state(char, 0, 172)

            get_symbol(key_delims['brace_delim'], "letter, number, +, -, ;, (, ', \", {, }", 172, 173)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '}':
            key = char
            matched = False
            append_state(char, 0, 174)

            get_symbol(key_delims['brace1_delim'], "letter, number, +, -, ;, (, }, ;, ,", 174, 175)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '(':
            key = char
            matched = False
            append_state(char, 0, 176)

            get_symbol(key_delims['paren_delim'], "letter, number, +, -, ;, !, #, ', \", (, )", 176, 177)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ')':
            key = char
            matched = False
            append_state(char, 0, 178)

            get_symbol(key_delims['paren1_delim'], "+, -, *, /, %, =, !, <, >, &, |, {, ), ;", 178, 179)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ',':
            key = char
            matched = False
            append_state(char, 0, 180)

            get_symbol(key_delims['comma_delim'], "letter, number, +, -, ], (, {, \", '", 180, 181)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ';':
            key = char
            matched = False
            append_state(char, 0, 182)

            get_symbol(key_delims['semicolon_delim'], "letter, number, +, -, (, }", 182, 183)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ':':
            key = char
            matched = False
            append_state(char, 0, 184)

            get_symbol(key_delims['colon_delim'], "letter, number, +, -, (", 184, 185)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '#':
            key = char
            matched = False
            append_state(char, 0, 186)

            get_symbol(key_delims['interpol_delim'], "\"", 186, 187)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i])) 

    print(state)
