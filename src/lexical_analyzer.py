from definitions import *
import tkinter as tk

state = []
lexeme = []
token = []

def lexer(code, console, table):
    pos = 0
    col = 0
    line = 1
    isIden = False
    isChar = False
    isString = False
    isInt = False
    isDec = False
    stateNum = 0

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
        nonlocal key
        key = '"'
        append_state(key, 0, 419)
        ctr = 0
        while True:
            if next_char() is None:  
                error_message("Expected: \"", key)
                break
            if next_char() == '"': 
                add_key(420, 421)
                check_delim(key_delims['lit_delim'], ";, ,, &, ), }", False)
                break
            elif next_char() == '\\': 
                esc = get_char()
                if next_char() in ['\\', '"', 'n', 't']: 
                    esc += get_char()
                    key += esc
                    ctr += 1
                    if ctr == 1:
                        append_state(esc, 419, 420)
                    else:
                        append_state(esc, 420, 420)
                else:
                    error_message(f"Invalid escape sequence: \\{esc}", key)
            else:
                ctr += 1
                if ctr == 1:
                    add_key(419, 420)
                else:
                    add_key(420, 420)

    def get_character():
        nonlocal key
        terminated = False
        key = "'"
        append_state(key, 0, 423)

        if next_char() is not None:
            if next_char() == "'":
                add_key(424, 425)
                check_delim(key_delims['lit_delim'], ";, ,, &, )", False)
            else:
                add_key(423, 424)
                if next_char() == "'":
                    add_key(424, 425)
                    check_delim(key_delims['lit_delim'], ";, ,, &, )", False)
                else:
                    get_key()
                    error_message("Character literals must only contain one character", key)
        if key.count("'") == 2:
            terminated = True
        if not terminated:
            error_message("Expected: '", key)

    def get_dec():
        nonlocal key, matched, isInt, isDec, stateNum

        isInt = False
        isDec = True
        trailingZero = ""
        curr = get_char()
  
        key += curr
        append_state(curr, stateNum, stateNum+1)
        check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", stateNum+1, stateNum+2, "num", False)
        if next_char().isdigit():
            check_num(stateNum+1, stateNum+3, stateNum+4)
            if next_char().isdigit():
                check_num(stateNum+3, stateNum+5, stateNum+6)
                if next_char().isdigit():
                    check_num(stateNum+5, stateNum+7, stateNum+8)
                    if next_char().isdigit():
                        check_num(stateNum+7, stateNum+9, stateNum+10)
                        if next_char().isdigit():
                            check_num(stateNum+9, stateNum+11, stateNum+12)
                            if next_char().isdigit():
                                key += trailingZero
                                check_num(stateNum+11, stateNum+13, stateNum+14)
        
        if not matched:
            if next_char() not in whitespace:
                get_key()
                print(f"key decimal: {key}")
                error_message(f"{key} exceeds maximum length of 7 decimal places", key)

    def get_num():
        nonlocal key, isInt, matched, isDec, stateNum
        isInt = True
        curr = char
        key = ''

        if curr == '~':
            append_state('~', 0, 248)
            key += curr
            curr = get_char()

        if curr == '0':
            while curr == '0':
                curr = get_char()

        if curr.isdigit():
            append_state(curr, 248, 249)
            key += curr
            check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", 249, 250, "num", False)
            if next_char() == '.':
                check_dec(249, 269)
            elif next_char().isdigit():
                check_num(249, 251, 252) 
                if next_char() == '.':
                    check_dec(251, 284)   
                elif next_char().isdigit():
                    check_num(251, 253, 254)
                    if next_char() == '.':
                        check_dec(253, 299)
                    elif next_char().isdigit():
                        check_num(253, 255, 256)
                        if next_char() == '.':
                            check_dec(255, 314)
                        elif next_char().isdigit():
                            check_num(255, 257, 258)
                            if next_char() == '.':
                                check_dec(257, 329)
                            elif next_char().isdigit():
                                check_num(257, 259, 260)
                                if next_char() == '.':
                                    check_dec(259, 344)
                                elif next_char().isdigit():
                                    check_num(259, 261, 262)
                                    if next_char() == '.':
                                        check_dec(261, 359)
                                    elif next_char().isdigit():
                                        check_num(261, 263, 264)
                                        if next_char() == '.':
                                            check_dec(263, 374)
                                        elif next_char().isdigit():
                                            check_num(263, 265, 266)
                                            if next_char() == '.':
                                                check_dec(265, 389)
                                            elif next_char().isdigit():
                                                check_num(265, 267, 268)
                                                if next_char() == '.':
                                                    check_dec(267, 404)

        isInt = False
        if not matched:
            if next_char() not in whitespace:
                get_key()
                if key.startswith('~'):
                    max = 11
                else:
                    max = 10
                if '.' in key:
                    literal = key.split('.')
                    if len(literal[0]) > max:
                        error_message(f"{key} exceeds maximum length of 10 digits", key)
                    if len(literal[1]) > 7:
                        error_message(f"{key} exceeds maximum length of 7 decimal places", key)
                else:
                    if len(key) > max:
                        error_message(f"{key} exceeds maximum length of 10 digits", key)

    def check_num(s1, s2, s3):
        nonlocal matched
        add_key(s1, s2)
        check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", s2, s3, "num", False)

    def check_dec(s1, s2):
        nonlocal matched, key, isDec, stateNum
        add_key(s1, s2)
        if next_char() in whitespace:
            error_message(f"Invalid decimal: {key}", key)
        else:
            stateNum = s2
            get_dec()

    def check_id(s1, s2, s3):
        nonlocal matched
        add_key(s1, s2)
        check_if_id(key_delims['iden_delim'], "operator, ;, &, >, (, ), [, ], {, ., ,", s2, s3, "iden", True)

    def get_id():
        nonlocal pos, key, matched, isIden

        isIden = True
        curr = get_char()

        key = curr
        append_state(curr, 0, 188)
        check_if_id(key_delims['iden_delim'], "operator, ;, &, >, (, ), [, ], {, ., ,", 188, 189, "iden", False)
        if next_char() in identifier: 
            check_id(188, 190, 191)
            if next_char() in identifier: 
                check_id(190, 192, 193)
                if next_char() in identifier: 
                    check_id(192, 194, 195)
                    if next_char() in identifier: 
                        check_id(194, 196, 197)
                        if next_char() in identifier: 
                            check_id(196, 198, 199)
                            if next_char() in identifier: 
                                check_id(198, 200, 201)
                                if next_char() in identifier: 
                                    check_id(200, 202, 203)
                                    if next_char() in identifier: 
                                        check_id(202, 204, 205)
                                        if next_char() in identifier: 
                                            check_id(204, 206, 207)
                                            if next_char() in identifier: 
                                                check_id(206, 208, 209)
                                                if next_char() in identifier: 
                                                    check_id(208, 210, 211)
                                                    if next_char() in identifier: 
                                                        check_id(210, 212, 213)
                                                        if next_char() in identifier: 
                                                            check_id(212, 214, 215)
                                                            if next_char() in identifier: 
                                                                check_id(214, 216, 217)
                                                                if next_char() in identifier: 
                                                                    check_id(216, 218, 219)
                                                                    if next_char() in identifier: 
                                                                        check_id(218, 220, 221)
                                                                        if next_char() in identifier: 
                                                                            check_id(220, 222, 223)
                                                                            if next_char() in identifier: 
                                                                                check_id(222, 224, 225)
                                                                                if next_char() in identifier: 
                                                                                    check_id(224, 226, 227)
                                                                                    if next_char() in identifier: 
                                                                                        check_id(226, 228, 229)
                                                                                        if next_char() in identifier: 
                                                                                            check_id(228, 230, 231)
                                                                                            if next_char() in identifier: 
                                                                                                check_id(230, 232, 233)
                                                                                                if next_char() in identifier: 
                                                                                                    check_id(232, 234, 233)
                                                                                                    if next_char() in identifier: 
                                                                                                        check_id(234, 236, 237)
                                                                                                        if next_char() in identifier: 
                                                                                                            check_id(236, 238, 239)
                                                                                                            if next_char() in identifier: 
                                                                                                                check_id(238, 240, 241)
                                                                                                                if next_char() in identifier: 
                                                                                                                    check_id(240, 242, 243)
                                                                                                                    if next_char() in identifier: 
                                                                                                                        check_id(242, 244, 245)
                                                                                                                        if next_char() in identifier: 
                                                                                                                            check_id(244, 246, 247)

        isIden = False
        if not matched:
            if next_char() not in whitespace:
                get_key()
                if len(key) > 30:
                    error_message(f"Identifier {key} exceeds maximum length of 30 characters", key)
            else:
                error_message(f"Invalid identifier: {key}", key)

    def append_key(lit):
        lexeme.append(key) 
        token.append(lit)

    def add_key(stateNum1, stateNum2):
        nonlocal key
        state.append(f"{next_char()} : {stateNum1}-{stateNum2}")
        key += get_char()

    def get_key():
        nonlocal key
        while next_char() not in whitespace:
            key += get_char()

    def get_lexeme():  
        nonlocal key, pos
        indexNum = len(key)
        del state[-indexNum:]
        pos -= indexNum
        get_id()

    def get_symbol(delim, expected, stateNum1, stateNum2, requiredSpace):
        nonlocal matched
        if next_char() in whitespace or next_char() in delim:
            matched = True
            check_delim(delim, expected, requiredSpace)
            append_state("end", stateNum1, stateNum2)

    def check_delim(delim, expected, requiredSpace):
        nonlocal key
        if isIden: append_key('id')
        elif isChar: append_key('chr_lit')
        elif isString: append_key('str_lit')
        elif isInt: append_key('int_lit')
        elif isDec: append_key('dec_lit')
        else: append_key(key)

        if not requiredSpace:
            skip_whitespace()

        if next_char() not in delim:
            error_message(f"Expected: {expected} after {key}", key)
            get_char()

    def check_if_id(delim, expected, stateNum1, stateNum2, reserved, requiredSpace):
        nonlocal matched, key
        if reserved == "word":
            if next_char() not in whitespace and (next_char().isalnum() or next_char() == '_'):
                matched = False
                return
        elif reserved in ["symbol", "iden", "num"]:
            if next_char() not in whitespace and next_char() not in delim:
                matched = False
                return

        matched = True
        state.append(f"end : {stateNum1}-{stateNum2}")

        if reserved == "num":
            key = key.rstrip('0')

        check_delim(delim, expected, requiredSpace)

    def append_state(stateChar, stateNum1, stateNum2):
        state.append(f"{stateChar} : {stateNum1}-{stateNum2}")

    def check_keyword():
        nonlocal matched, key
        if char == 'b':
            key = char
            matched = False
            append_state(char, 0, 1)

            if next_char() == 'l':
                add_key(1, 2)
                if next_char() == 'n':
                    add_key(2, 3)
                    matched = True
                    check_if_id(key_delims['data_delim'], "letter, [, (", 3, 4, "word", False)
            elif next_char() == 'r':
                add_key(1, 5)
                if next_char() == 'k':
                    add_key(5, 6)
                    matched = True
                    check_if_id(key_delims['jmp_delim'], ";", 6, 7, "word", False)
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
                    check_if_id(key_delims['data_delim'], "letter, [, (", 10, 11, "word", False)
            elif next_char() == 'o':
                add_key(8, 12)
                if next_char() == 'n':
                    add_key(12, 13)
                    if next_char() == 's':
                        add_key(13, 14)
                        if next_char() == 't':
                            add_key(14, 15)
                            matched = True
                            check_if_id(whitespace, "space", 15, 16, "word", True)
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
                    check_if_id(key_delims['data_delim'], "letter, [, (", 19, 20, "word", False)
                elif next_char() == 'f':
                    add_key(18, 21)
                    matched = True
                    check_if_id(key_delims['def_delim'], ":", 21, 22, "word", False)
            elif next_char() == 'i':
                add_key(17, 23)
                if next_char() == 's':
                    add_key(23, 24)
                    if next_char() == 'p':
                        add_key(24, 25)
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 25, 26, "word", False)
            elif next_char() == 'o':
                add_key(17, 27)
                matched = True
                check_if_id(key_delims['block_delim'], "{", 27, 28, "word", False)
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
                        check_if_id(key_delims['state_delim'], "(", 32, 33, "word", False)
                elif next_char() == 's':
                    add_key(30, 34)
                    if next_char() == 'e':
                        add_key(34, 35)
                        matched = True
                        check_if_id(key_delims['block_delim'], "{", 35, 36, "word", False)
            elif next_char() == 'x':
                add_key(29, 37)
                if next_char() == 'i':
                    add_key(37, 38)
                    if next_char() == 't':
                        add_key(38, 39)
                        matched = True
                        check_if_id(key_delims['jmp_delim'], ";", 39, 40, "word", False)
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
                            check_if_id(key_delims['val_delim'], ";, ,, ), }", 45, 46, "word", False)
            elif next_char() == 'o':
                add_key(41, 47)
                if next_char() == 'r':
                    add_key(47, 48)
                    if next_char() != 'e':
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 48, 49, "word", False)
                    else:
                        add_key(48, 50)
                        if next_char() == 'a':
                            add_key(50, 51)
                            if next_char() == 'c':
                                add_key(51, 52)
                                if next_char() == 'h':
                                    add_key(52, 53)
                                    matched = True
                                    check_if_id(key_delims['state_delim'], "(", 53, 54, "word", False)  
            if not matched:
                get_lexeme()

        elif char == 'i':
            key = char
            matched = False
            append_state(char, 0, 55)

            if next_char() == 'f':
                add_key(55, 56)
                matched = True
                check_if_id(key_delims['state_delim'], "(", 56, 57, "word", False)
            elif next_char() == 'n':
                add_key(55, 58)
                if next_char() != 's' and next_char() != 't':
                    matched = True
                    check_if_id(whitespace, "identifier", 58, 59, "word", True)
                elif next_char() == 's':
                    add_key(58, 60)
                    if next_char() == 'p':
                        add_key(60, 61)
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 61, 62, "word", False)
                elif next_char() == 't':
                    add_key(58, 63)
                    matched = True
                    check_if_id(key_delims['data_delim'], "letter, [, (", 63, 64, "word", False)
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
                    check_if_id(whitespace, "literal", 67, 68, "word", True)
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
                        check_if_id(key_delims['state_delim'], "(", 72, 73, "word", False)
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
                        check_if_id(key_delims['val_delim'], ";, ,, ), }", 77, 78, "word", False)
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
                    check_if_id(whitespace, "literal", 81, 82, "word", True )
            elif next_char() == 's':
                add_key(79, 83)
                if next_char() == 'm':
                    add_key(83, 84)
                    matched = True
                    check_if_id(key_delims['jmp_delim'], ";", 84, 85, "word", False)
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
                        check_if_id(whitespace, "identifier", 89, 90, "word", True)
            elif next_char() == 't':
                add_key(86, 91)
                if next_char() == 'r':
                    add_key(91, 92)
                    if next_char() != 'c':
                        matched = True
                        check_if_id(key_delims["data_delim"], "letter, [, (", 92, 93, "word", False)
                    else:
                        add_key(92, 94)
                        matched = True
                        check_if_id(whitespace, "identifier", 94, 95, "word", True)
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
                                check_if_id(key_delims['state_delim'], "(", 100, 101, "word", False)
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
                        check_if_id(key_delims['val_delim'], ";, ,, ), }", 105, 106, "word", False)
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
                    check_if_id(whitespace, "identifier", 109, 110, "word", True)
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
                            check_if_id(key_delims['state_delim'], "(", 115, 116, "word", False)
            if not matched:
                get_lexeme()

        else:
            key = char
            get_lexeme()
    
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
            isString = True
            get_string()
            isString = False

        elif char == "'":
            isChar = True
            get_character()
            isChar = False

        elif char == '_':
            key = char
            while next_char() not in whitespace:
                key += get_char()
            error_message(f"Invalid identifier: {key}", key)
        
        elif char.isdigit() or char == '~':
            isInt = True
            get_num()

        elif char in alpha:
            check_keyword()

        elif char == '=':
            key = char 
            matched = False
            append_state(char, 0, 117)

            if next_char() == '=':
                add_key(117, 119)
                matched = True
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 119, 120, "symbol", False)
            else:
                get_symbol(key_delims['asn_delim'], "letter, number, (, ~, !, ', \", {, #", 117, 118, False)
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
                check_if_id(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 123, 124, "symbol", False)
            elif next_char() == '=':
                add_key(121, 125)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 125, 126, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 121, 122, False)
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
                check_if_id(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 129, 130, "symbol", False)
            elif next_char() == '=':
                add_key(127, 131)
                matched = True
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 131, 132, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 127, 128, False)
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
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 135, 136, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 133, 134, False)
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
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 139, 140, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 137, 138, False)
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
                check_if_id(key_delims['op_delim'], "letter, number, (, ~", 143, 144, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 141, 142, False)
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
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 147, 148, "symbol", False)
            else:
                get_symbol(key_delims['concat_delim'], "letter, (, \", ', #", 145, 146, False)
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
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 150, 151, "symbol", False)
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
                check_if_id(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 154, 155, "symbol", False)
            else:
                get_symbol(key_delims['relate_delim'], "letter, (, \", ', #", 152, 153, False)
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
                check_if_id(key_delims['var_delim'], "letter, +, -, ], ,", 158, 159, "symbol", False)
            elif next_char() == '=':
                add_key(156, 160)
                matched = True
                check_if_id(key_delims['relate1_delim'], "letter, number, (, ~, !", 160, 161, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 156, 157, False)
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
                check_if_id(key_delims['var1_delim'], "ASCII Character", 164, 164, "symbol", False)
            elif next_char() == '=':
                add_key(162, 166)
                matched = True
                check_if_id(key_delims['relate1_delim'], "letter, number, (, ~, !", 166, 167, "symbol", False)
            else:
                get_symbol(key_delims['op_delim'], "letter, number, (, ~", 162, 163, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '[':
            key = char
            matched = False
            append_state(char, 0, 168)

            get_symbol(key_delims['bracket_delim'], "letter, number, ], ,, +, -", 168, 169, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ']':
            key = char
            matched = False
            append_state(char, 0, 170)

            get_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '>'", 170, 171, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '{':
            key = char
            matched = False
            append_state(char, 0, 172)

            get_symbol(key_delims['brace_delim'], "letter, number, +, -, ;, (, ', \", {, }", 172, 173, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '}':
            key = char
            matched = False
            append_state(char, 0, 174)

            get_symbol(key_delims['brace1_delim'], "letter, number, +, -, ;, (, }, ;, ,", 174, 175, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '(':
            key = char
            matched = False
            append_state(char, 0, 176)

            get_symbol(key_delims['paren_delim'], "letter, number, +, -, ;, !, #, ', \", (, )", 176, 177, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ')':
            key = char
            matched = False
            append_state(char, 0, 178)

            get_symbol(key_delims['paren1_delim'], "+, -, *, /, %, =, !, <, >, &, |, {, ), ;", 178, 179, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ',':
            key = char
            matched = False
            append_state(char, 0, 180)

            get_symbol(key_delims['comma_delim'], "letter, number, +, -, ], (, {, \", '", 180, 181, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ';':
            key = char
            matched = False
            append_state(char, 0, 182)

            get_symbol(key_delims['semicolon_delim'], "letter, number, +, -, (, }", 182, 183, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == ':':
            key = char
            matched = False
            append_state(char, 0, 184)

            get_symbol(key_delims['colon_delim'], "letter, number, +, -, (", 184, 185, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

        elif char == '#':
            key = char
            matched = False
            append_state(char, 0, 186)

            get_symbol(key_delims['interpol_delim'], "\"", 186, 187, False)
            if not matched:
                get_key()
                error_message(f"{key} => invalid operator", key)

    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i])) 

    #print(state)

    lexeme.clear()
    token.clear()
    state.clear()
