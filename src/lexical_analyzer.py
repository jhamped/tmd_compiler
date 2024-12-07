from definitions import *
import tkinter as tk

def lexer(code, console, table):
    pos = 0
    col = 0
    line = 1
    stateNum = 0
    key = ""
    isIden = False
    isChar = False
    isString = False
    isInt = False
    isDec = False
    matched = False
    
    def advance():  
        nonlocal pos, col, line
        if pos < len(code):
            curr = code[pos]
            pos += 1
            if curr == '\n':
                line += 1
                col = 0
            else:
                col += 1

            return curr
        return None 
    
    def peek_next():#
        if pos < len(code):
            return code[pos]
        return None
    
    def skip_whitespace():  
        nonlocal col
        while(char := peek_next()) in whitespace:
            advance()

    def skip_single_comment():#  
        while advance() not in ['\n', None]:
            pass

    def skip_multi_comment():#
        while True:
            char = advance()
            if char == '*' and peek_next() == '/':
                advance() 
                break

    def error_message(error, expected, error_key, expectedError):
        nonlocal line, col
        console.insert(tk.END, "Error: ", "error")
        console.insert(tk.END, f"{error}")
        if expectedError:
            console.insert(tk.END, f"  Expected: {expected}", "expected")
        console.insert(tk.END, f"\n       line {line}, column {col}\n", "ln_col")

    #----------STR_LIT----------
    def get_string():#
        nonlocal key, isString
        isString = True
        key = '"'
        append_state(key, 0, 419)
        ctr = 0

        while True:
            if peek_next() is None:  
                error_message("Expected: \"", "", key, False)
                break
            if peek_next() == '"': 
                add_key(420, 421)
                check_delim(key_delims['lit_delim'], ";, ,, &, ), }, !, |, =", False)
                break
            elif peek_next() == '\\': 
                esc = advance()
                if peek_next() in ['\\', '"', 'n', 't']: 
                    esc += advance()
                    key += esc
                    ctr += 1
                    if ctr == 1:
                        append_state(esc, 419, 420)
                    else:
                        append_state(esc, 420, 420)
                else:
                    error_message(f"Invalid escape sequence: \\{esc}", "", key, False)
            else:
                ctr += 1
                if ctr == 1:
                    add_key(419, 420)
                else:
                    add_key(420, 420)
        
        isString = False
    #----------STR_LIT----------

    #----------CHR_LIT----------
    def get_character():#
        nonlocal key, isChar
        isChar = True
        terminated = False
        key = "'"
        append_state(key, 0, 423)

        if peek_next() is not None:
            if peek_next() == "'":
                add_key(424, 425)
                check_delim(key_delims['lit_delim'], ";, ,, &, )", False)
            else:
                add_key(423, 424)
                if peek_next() == "'":
                    add_key(424, 425)
                    check_delim(key_delims['lit_delim'], ";, ,, &, )", False)
                else:
                    get_key()
                    error_message("Character literals must only contain one character", "", key, False)
        if key.count("'") == 2:
            terminated = True
        if not terminated:
            error_message("Expected: '", "", key, False)
        isChar = False
    #----------CHR_LIT----------

    #----------INT_LIT----------
    def get_num():#
        nonlocal key, isInt, matched, isDec, stateNum
        isInt = True
        curr = char
        key = ''

        if curr == '~':
            append_state('~', 0, 248)
            key += curr
            curr = advance()

        if curr == '0':
            while curr == '0':
                curr = advance()

        if curr.isdigit():
            append_state(curr, 248, 249)
            key += curr
            check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", 249, 250, "num", False)
            if peek_next() == '.':
                check_dec(249, 269)
            elif peek_next().isdigit():
                check_num(249, 251, 252) 
                if peek_next() == '.':
                    check_dec(251, 284)   
                elif peek_next().isdigit():
                    check_num(251, 253, 254)
                    if peek_next() == '.':
                        check_dec(253, 299)
                    elif peek_next().isdigit():
                        check_num(253, 255, 256)
                        if peek_next() == '.':
                            check_dec(255, 314)
                        elif peek_next().isdigit():
                            check_num(255, 257, 258)
                            if peek_next() == '.':
                                check_dec(257, 329)
                            elif peek_next().isdigit():
                                check_num(257, 259, 260)
                                if peek_next() == '.':
                                    check_dec(259, 344)
                                elif peek_next().isdigit():
                                    check_num(259, 261, 262)
                                    if peek_next() == '.':
                                        check_dec(261, 359)
                                    elif peek_next().isdigit():
                                        check_num(261, 263, 264)
                                        if peek_next() == '.':
                                            check_dec(263, 374)
                                        elif peek_next().isdigit():
                                            check_num(263, 265, 266)
                                            if peek_next() == '.':
                                                check_dec(265, 389)
                                            elif peek_next().isdigit():
                                                check_num(265, 267, 268)
                                                if peek_next() == '.':
                                                    check_dec(267, 404)

        isInt = False
        if not matched:
            if peek_next() not in whitespace:
                get_key()
                if key.startswith('~'):
                    max = 11
                else:
                    max = 10
                if '.' in key:
                    literal = key.split('.')
                    if len(literal[0]) > max:
                        error_message(f"{key} exceeds maximum length of 10 digits", "", key, False)
                    if len(literal[1]) > 7:
                        error_message(f"{key} exceeds maximum length of 7 decimal places", "", key, False)
                else:
                    if len(key) > max:
                        error_message(f"{key} exceeds maximum length of 10 digits", "", key, False)
    #----------INT_LIT----------

    #----------DEC_LIT----------
    def get_dec():
        nonlocal key, matched, isInt, isDec, stateNum

        isInt = False
        isDec = True
        trailingZero = ""
        curr = advance()
  
        key += curr
        append_state(curr, stateNum, stateNum+1)
        check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", stateNum+1, stateNum+2, "num", False)
        if peek_next().isdigit():
            check_num(stateNum+1, stateNum+3, stateNum+4)
            if peek_next().isdigit():
                check_num(stateNum+3, stateNum+5, stateNum+6)
                if peek_next().isdigit():
                    check_num(stateNum+5, stateNum+7, stateNum+8)
                    if peek_next().isdigit():
                        check_num(stateNum+7, stateNum+9, stateNum+10)
                        if peek_next().isdigit():
                            check_num(stateNum+9, stateNum+11, stateNum+12)
                            if peek_next().isdigit():
                                key += trailingZero
                                check_num(stateNum+11, stateNum+13, stateNum+14)
        
        if not matched:
            if peek_next() not in whitespace:
                get_key()
                print(f"key decimal: {key}")
                error_message(f"{key} exceeds maximum length of 7 decimal places", "", key, False)
    #----------DEC_LIT----------

    #----------IDEN----------
    def get_id():
        nonlocal pos, key, matched, isIden

        isIden = True
        curr = advance()

        key = curr
        append_state(curr, 0, 188)
        check_if_id(key_delims['iden_delim'], "operator, ;, &, >, (, ), [, ], {, ., ,", 188, 189, "iden", False)
        if peek_next() in identifier: 
            check_id(188, 190, 191)
            if peek_next() in identifier: 
                check_id(190, 192, 193)
                if peek_next() in identifier: 
                    check_id(192, 194, 195)
                    if peek_next() in identifier: 
                        check_id(194, 196, 197)
                        if peek_next() in identifier: 
                            check_id(196, 198, 199)
                            if peek_next() in identifier: 
                                check_id(198, 200, 201)
                                if peek_next() in identifier: 
                                    check_id(200, 202, 203)
                                    if peek_next() in identifier: 
                                        check_id(202, 204, 205)
                                        if peek_next() in identifier: 
                                            check_id(204, 206, 207)
                                            if peek_next() in identifier: 
                                                check_id(206, 208, 209)
                                                if peek_next() in identifier: 
                                                    check_id(208, 210, 211)
                                                    if peek_next() in identifier: 
                                                        check_id(210, 212, 213)
                                                        if peek_next() in identifier: 
                                                            check_id(212, 214, 215)
                                                            if peek_next() in identifier: 
                                                                check_id(214, 216, 217)
                                                                if peek_next() in identifier: 
                                                                    check_id(216, 218, 219)
                                                                    if peek_next() in identifier: 
                                                                        check_id(218, 220, 221)
                                                                        if peek_next() in identifier: 
                                                                            check_id(220, 222, 223)
                                                                            if peek_next() in identifier: 
                                                                                check_id(222, 224, 225)
                                                                                if peek_next() in identifier: 
                                                                                    check_id(224, 226, 227)
                                                                                    if peek_next() in identifier: 
                                                                                        check_id(226, 228, 229)
                                                                                        if peek_next() in identifier: 
                                                                                            check_id(228, 230, 231)
                                                                                            if peek_next() in identifier: 
                                                                                                check_id(230, 232, 233)
                                                                                                if peek_next() in identifier: 
                                                                                                    check_id(232, 234, 233)
                                                                                                    if peek_next() in identifier: 
                                                                                                        check_id(234, 236, 237)
                                                                                                        if peek_next() in identifier: 
                                                                                                            check_id(236, 238, 239)
                                                                                                            if peek_next() in identifier: 
                                                                                                                check_id(238, 240, 241)
                                                                                                                if peek_next() in identifier: 
                                                                                                                    check_id(240, 242, 243)
                                                                                                                    if peek_next() in identifier: 
                                                                                                                        check_id(242, 244, 245)
                                                                                                                        if peek_next() in identifier: 
                                                                                                                            check_id(244, 246, 247)

        isIden = False
        if not matched:
            if peek_next() not in whitespace:
                get_key()
                if len(key) > 30:
                    error_message(f"Identifier {key} exceeds maximum length of 30 characters", "", key, False)
            else:
                error_message(f"Invalid identifier: {key}", "", key, False)

    def get_lexeme():  
        nonlocal key, pos
        index = len(key)
        del state[-index:]
        pos -= index
        get_id()
    #----------IDEN----------

    #----------KEYWORDS----------
    def get_keyword():#
        nonlocal matched, key
        if char == 'b':
            match_found(1)
            if peek_next() == 'l':
                add_key(1, 2)
                if peek_next() == 'n':
                    add_matched_key(key_delims['data_delim'], "letter, [, (", 2, 3, 4, "word", False)
            elif peek_next() == 'r':
                add_key(1, 5)
                if peek_next() == 'k':
                    add_matched_key(key_delims['jmp_delim'], ";", 5, 6, 7, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'c':
            match_found(8)
            if peek_next() == 'h':
                add_key(8, 9)
                if peek_next() == 'r':
                    add_matched_key(key_delims['data_delim'], "letter, [, (", 9, 10, 11, "word", False)
            elif peek_next() == 'o':
                add_key(8, 12)
                if peek_next() == 'n':
                    add_key(12, 13)
                    if peek_next() == 's':
                        add_key(13, 14)
                        if peek_next() == 't':
                            add_matched_key(whitespace, "space", 14, 15, 16, "word", True)
            if not matched:
                get_lexeme()

        elif char == 'd':
            match_found(17)
            if peek_next() == 'e':
                add_key(17, 18)
                if peek_next() == 'c':
                    add_matched_key(key_delims['data_delim'], "letter, [, (", 18, 19, 20, "word", False)
                elif peek_next() == 'f':
                    add_matched_key(key_delims['def_delim'], ":", 18, 21, 22, "word", False)
            elif peek_next() == 'i':
                add_key(17, 23)
                if peek_next() == 's':
                    add_key(23, 24)
                    if peek_next() == 'p':
                        add_matched_key(key_delims['state_delim'], "(", 24, 25, 26, "word", False)
            elif peek_next() == 'o':
                add_matched_key(key_delims['block_delim'], "{", 17, 27, 28, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'e':
            match_found(29)
            if peek_next() == 'l':
                add_key(29, 30)
                if peek_next() == 'i':
                    add_key(30, 31)
                    if peek_next() == 'f':
                        add_matched_key(key_delims['state_delim'], "(", 31, 32, 33, "word", False)
                elif peek_next() == 's':
                    add_key(30, 34)
                    if peek_next() == 'e':
                        add_matched_key(key_delims['block_delim'], "{", 34, 35, 36, "word", False)
            elif peek_next() == 'x':
                add_key(29, 37)
                if peek_next() == 'i':
                    add_key(37, 38)
                    if peek_next() == 't':
                        add_matched_key(key_delims['jmp_delim'], ";", 38, 39, 40, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'f':
            match_found(41)
            if peek_next() == 'a':
                add_key(41, 42)
                if peek_next() == 'l':
                    add_key(42, 43)
                    if peek_next() == 's':
                        add_key(43, 44)
                        if peek_next() == 'e':
                            add_matched_key(key_delims['val_delim'], ";, ,, ), }", 44, 45, 46, "word", False)
            elif peek_next() == 'o':
                add_key(41, 47)
                if peek_next() == 'r':
                    add_key(47, 48)
                    if peek_next() != 'e':
                        matched = True
                        check_if_id(key_delims['state_delim'], "(", 48, 49, "word", False)
                    else:
                        add_key(48, 50)
                        if peek_next() == 'a':
                            add_key(50, 51)
                            if peek_next() == 'c':
                                add_key(51, 52)
                                if peek_next() == 'h':
                                    add_matched_key(key_delims['state_delim'], "(", 52, 53, 54, "word", False)  
            if not matched:
                get_lexeme()

        elif char == 'i':
            match_found(55)
            if peek_next() == 'f':
                add_matched_key(key_delims['state_delim'], "(", 55, 56, 57, "word", False)
            elif peek_next() == 'n':
                add_key(55, 58)
                if peek_next() != 's' and peek_next() != 't':
                    matched = True
                    check_if_id(whitespace, "identifier", 58, 59, "word", True)
                elif peek_next() == 's':
                    add_key(58, 60)
                    if peek_next() == 'p':
                        add_matched_key(key_delims['state_delim'], "(", 60, 61, 62, "word", False)
                elif peek_next() == 't':
                    add_matched_key(key_delims['data_delim'], "identifier, [, (", 58, 63, 64, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'k':
            match_found(65)
            if peek_next() == 'e':
                add_key(65, 66)
                if peek_next() == 'y':
                    add_matched_key(whitespace, "literal", 66, 67, 68, "word", True)
            if not matched:
                get_lexeme()

        elif char == 'm':
            match_found(69)
            if peek_next() == 'a':
                add_key(69, 70)
                if peek_next() == 'i':
                    add_key(70, 71)
                    if peek_next() == 'n':
                        add_matched_key(key_delims['state_delim'], "(", 71, 72, 73, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'n':
            match_found(74)
            if peek_next() == 'o':
                add_key(74, 75)
                if peek_next() == 'n':
                    add_key(75, 76)
                    if peek_next() == 'e':
                        add_matched_key(key_delims['val_delim'], ";, ,, ), }", 76, 77, 78, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'r':
            match_found(79)
            if peek_next() == 'e':
                add_key(79, 80)
                if peek_next() == 't':
                    add_matched_key(whitespace, "literal", 80, 81, 82, "word", True )
            elif peek_next() == 's':
                add_key(79, 83)
                if peek_next() == 'm':
                    add_matched_key(key_delims['jmp_delim'], ";", 83, 84, 85, "word", False)
            if not matched:
                get_lexeme()

        elif char == 's':
            match_found(86)
            if peek_next() == 'e':
                add_key(86, 87)
                if peek_next() == 'g':
                    add_key(87, 88)
                    if peek_next() == 'm':
                        add_matched_key(whitespace, "identifier", 88, 89, 90, "word", True)
            elif peek_next() == 't':
                add_key(86, 91)
                if peek_next() == 'r':
                    add_key(91, 92)
                    if peek_next() != 'c':
                        matched = True
                        check_if_id(key_delims["data_delim"], "letter, [, (", 92, 93, "word", False)
                    else:
                        add_matched_key(whitespace, "identifier", 92, 94, 95, "word", True)
            elif peek_next() == 'w':
                add_key(86, 96)
                if peek_next() == 'i':
                    add_key(96, 97)
                    if peek_next() == 't':
                        add_key(97, 98)
                        if peek_next() == 'c':
                            add_key(98, 99)
                            if peek_next() == 'h':
                                add_matched_key(key_delims['state_delim'], "(", 99, 100, 101, "word", False)
            if not matched:
                get_lexeme()

        elif char == 't':
            match_found(102)
            if peek_next() == 'r':
                add_key(102, 103)
                if peek_next() == 'u':
                    add_key(103, 104)
                    if peek_next() == 'e':
                        add_matched_key(key_delims['val_delim'], ";, ,, ), }", 104, 105, 106, "word", False)
            if not matched:
                get_lexeme()

        elif char == 'v':
            match_found(107)
            if peek_next() == 'a':
                add_key(107, 108)
                if peek_next() == 'r':
                    add_matched_key(whitespace, "identifier", 108, 109, 110, "word", True)
            if not matched:
                get_lexeme()

        elif char == 'w':
            match_found(111)
            if peek_next() == 'h':
                add_key(111, 112)
                if peek_next() == 'i':
                    add_key(112, 113)
                    if peek_next() == 'l':
                        add_key(113, 114)
                        if peek_next() == 'e':
                            add_matched_key(key_delims['state_delim'], "(", 114, 115, 116, "word", False)
            if not matched:
                get_lexeme()

        else:
            key = char
            get_lexeme()
    #----------KEYWORDS----------

    #----------SYMBOLS----------
    def get_symbol():
        nonlocal key, matched
        def symbol_error():
            get_key()
            error_message(f"{key} => invalid operator", "", key, False)

        if char == '=':
            match_found(117)
            if peek_next() == '=':
                add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 117, 119, 120, "symbol", False)
            else:
                check_symbol(key_delims['asn_delim'], "letter, number, (, ~, !, ', \", {, #", 117, 118, False)
            if not matched:
                symbol_error()

        elif char == '+':
            match_found(121)
            if peek_next() == '+':
                add_matched_key(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 121, 123, 124, "symbol", False)
            elif peek_next() == '=':
                add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 121, 125, 126, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 121, 122, False)
            if not matched:
                symbol_error()

        elif char == '-':
            match_found(127)
            if peek_next() == '-':
                add_matched_key(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 127, 129, 130, "symbol", False)
            elif peek_next() == '=':
                add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 127, 131, 132, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 127, 128, False)
            if not matched:
                symbol_error()
                        
        elif char == '*':
            match_found(133)
            if peek_next() == '=':
                add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 133, 135, 136, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 133, 134, False)
            if not matched:
                symbol_error()

        elif char == '/':
            match_found(137)
            if peek_next() == '=':
                add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 137, 139, 140, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 137, 138, False)
            if not matched:
                symbol_error()

        elif char == '%':
            match_found(141)
            if peek_next() == '=':
                add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 141, 143, 144, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 141, 142, False)
            if not matched:
                symbol_error()

        elif char == '&':
            match_found(145)
            if peek_next() == '&':
                add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 145, 147, 148, "symbol", False)
            else:
                check_symbol(key_delims['concat_delim'], "letter, (, \", ', #", 145, 146, False)
            if not matched:
                symbol_error()
                
        elif char == '|':
            match_found(149)
            if peek_next() == '|':
                add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 149, 150, 151, "symbol", False)
            if not matched:
                symbol_error()

        elif char == '!':
            match_found(152)
            if peek_next() == '=':
                add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 152, 154, 155, "symbol", False)
            else:
                check_symbol(key_delims['relate_delim'], "letter, (, \", ', #", 152, 153, False)
            if not matched:
                symbol_error()

        elif char == '<':
            match_found(156)
            if peek_next() == '<':
                add_matched_key(key_delims['var_delim'], "letter, +, -, ], ,", 156, 158, 159, "symbol", False)
            elif peek_next() == '=':
                add_matched_key(key_delims['relate1_delim'], "letter, number, (, ~, !", 156, 160, 161, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 156, 157, False)
            if not matched:
                symbol_error()

        elif char == '>':
            match_found(162)
            if peek_next() == '>':
                add_matched_key(key_delims['var1_delim'], "ASCII Character", 162, 164, 164, "symbol", False)
            elif peek_next() == '=':
                add_matched_key(key_delims['relate1_delim'], "letter, number, (, ~, !", 162, 166, 167, "symbol", False)
            else:
                check_symbol(key_delims['op_delim'], "letter, number, (, ~", 162, 163, False)
            if not matched:
                symbol_error()

        elif char == '[':
            match_found(168)
            check_symbol(key_delims['bracket_delim'], "letter, number, ], ,, +, -", 168, 169, False)
            if not matched:
                symbol_error()

        elif char == ']':
            match_found(170)
            check_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '>'", 170, 171, False)
            if not matched:
                symbol_error()

        elif char == '{':
            match_found(172)
            check_symbol(key_delims['brace_delim'], "letter, number, +, -, ;, (, ', \", {, }", 172, 173, False)
            if not matched:
                symbol_error()

        elif char == '}':
            match_found(174)
            check_symbol(key_delims['brace1_delim'], "letter, number, +, -, ;, (, }, ;, ,", 174, 175, False)
            if not matched:
                symbol_error()

        elif char == '(':
            match_found(176)
            check_symbol(key_delims['paren_delim'], "letter, number, +, -, ;, !, #, ', \", (, )", 176, 177, False)
            if not matched:
                symbol_error()

        elif char == ')':
            match_found(178)
            check_symbol(key_delims['paren1_delim'], "+, -, *, /, %, =, !, <, >, &, |, {, ), ;", 178, 179, False)
            if not matched:
                symbol_error()

        elif char == ',':
            match_found(180)
            check_symbol(key_delims['comma_delim'], "letter, number, +, -, ], (, {, \", '", 180, 181, False)
            if not matched:
                symbol_error()

        elif char == ';':
            match_found(182)
            check_symbol(key_delims['semicolon_delim'], "letter, number, +, -, (, }", 182, 183, False)
            if not matched:
                symbol_error()

        elif char == ':':
            match_found(184)
            check_symbol(key_delims['colon_delim'], "letter, number, +, -, (", 184, 185, False)
            if not matched:
                symbol_error()

        elif char == '#':
            match_found(186)
            check_symbol(key_delims['interpol_delim'], "\"", 186, 187, False)
            if not matched:
                symbol_error()

        elif char == '.' or char == '_':
            key = char
            get_key()
            if key.startswith('.') and key[1:].isdigit():
                error_message(f"Invalid decimal value: {key}", "", key, False)
            else:
                error_message(f"Invalid identifier: {key}", "", key, False)
        
        else:
            key = char
            get_key()
            error_message(f"Invalid: {key}", "", key, False)
    #----------SYMBOLS----------

    #----------CHECKERS----------
    def check_num(s1, s2, s3):
        nonlocal matched
        add_key(s1, s2)
        check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", s2, s3, "num", False)

    def check_dec(s1, s2):
        nonlocal matched, key, isDec, stateNum
        add_key(s1, s2)
        if peek_next() in whitespace:
            error_message(f"Invalid decimal: {key}", "", key, False)
        else:
            stateNum = s2
            get_dec()

    def check_id(s1, s2, s3):
        nonlocal matched
        add_key(s1, s2)
        check_if_id(key_delims['iden_delim'], "operator, ;, &, >, (, ), [, ], {, ., ,", s2, s3, "iden", True)

    def check_symbol(delim, expected, stateNum1, stateNum2, requiredSpace):
        nonlocal matched
        if peek_next() in whitespace or peek_next() in delim or peek_next() in punc_symbols:
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

        if peek_next() not in delim:
            error_message(f"Unexpected {advance()} after {key}", expected, key, True)
            advance()

    def check_if_id(delim, expected, stateNum1, stateNum2, reserved, requiredSpace):
        nonlocal matched, key
        if reserved == "word":
            if peek_next() not in whitespace and (peek_next().isalnum() or peek_next() == '_'):
                matched = False
                return
        elif reserved in ["symbol", "iden", "num"]:
            if peek_next() not in whitespace and peek_next() not in delim:
                matched = False
                return

        matched = True
        state.append(f"end : {stateNum1}-{stateNum2}")

        if reserved == "num":
            key = key.rstrip('0')

        check_delim(delim, expected, requiredSpace)
    #----------CHECKERS----------

    #----------STATE AND KEY MANIPULATION----------
    def append_state(stateChar, stateNum1, stateNum2):
        state.append(f"{stateChar} : {stateNum1}-{stateNum2}")
    
    def append_key(lit):
        lexeme.append(key) 
        token.append(lit)

    def add_key(stateNum1, stateNum2):
        nonlocal key
        state.append(f"{peek_next()} : {stateNum1}-{stateNum2}")
        key += advance()

    def add_matched_key(delim, expected, s1, s2, s3, reserved, requiredSpace):
        nonlocal matched
        add_key(s1, s2)
        matched = True
        check_if_id(delim, expected, s2, s3, reserved, requiredSpace)

    def get_key():
        nonlocal key
        while peek_next() not in whitespace:
            key += advance()

    def match_found(state):
        nonlocal key, matched
        key = char
        matched = False
        append_state(char, 0, state)
    #----------STATE AND KEY MANIPULATION----------

    while (char := advance()) is not None:
        if char == '/' and peek_next() == '/': advance(), skip_single_comment()
        elif char == '/' and peek_next() == '*': advance(), skip_multi_comment()
        elif char == '"': get_string()
        elif char == "'": get_character()       
        elif char.isdigit() or char == '~': get_num()
        elif char in alpha: get_keyword()
        elif char in punc_symbols: get_symbol()

    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i])) 
    #print(state)

    lexeme.clear()
    token.clear()
    state.clear()
