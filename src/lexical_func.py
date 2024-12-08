from definitions import *
import tkinter as tk

class Lexical:
    def __init__(self, code, console):
        self.pos = 0
        self.col = 0
        self.line = 1
        self.code = code
        self.console = console

        self.stateNum = 0
        self.key = ""
        self.isIden = False
        self.isChar = False
        self.isString = False
        self.isInt = False
        self.isDec = False
        self.matched = False

    def advance(self):
        if self.pos < len(self.code):
            curr = self.code[self.pos]
            self.pos += 1
            if curr == '\n':
                self.line += 1
                self.col = 0
            else:
                self.col += 1

            return curr
        return None 
    
    def peek_next(self):
        if self.pos < len(self.code):
            return self.code[self.pos]
        return None
    
    def skip_whitespace(self):
        while(self.peek_next()) in whitespace:
            self.advance()

    def skip_single_comment(self):
        while self.advance() not in ['\n', None]:
            pass

    def skip_multi_comment(self):
        while True:
            char = self.advance()
            if char == '*' and self.peek_next() == '/':
                self.advance() 
                break

    def error_message(self, error, expected, expectedError):
        self.console.insert(tk.END, "Error: ", "error")
        self.console.insert(tk.END, f"{error}")
        if expectedError:
            self.console.insert(tk.END, f"  Expected: {expected}", "expected")
        self.console.insert(tk.END, f"\n       line {self.line}, column {self.col}\n", "ln_col")

    def get_string(self):
        self.isString = True
        self.key = '"'
        self.append_state(self.key, 0, 419)
        ctr = 0

        while True:
            if self.peek_next() is None:  
                self.error_message("Expected: \"", "", False)
                break
            if self.peek_next() == '"': 
                self.add_key(420, 421)
                self.check_delim(key_delims['lit_delim'], ";, ,, &, ), }, !, |, =", False)
                break
            elif self.peek_next() == '\\': 
                esc = self.advance()
                if self.peek_next() in ['\\', '"', 'n', 't']: 
                    esc += self.advance()
                    self.key += esc
                    ctr += 1
                    if ctr == 1:
                        self.append_state(esc, 419, 420)
                    else:
                        self.append_state(esc, 420, 420)
                else:
                    self.error_message(f"Invalid escape sequence: \\{esc}", "", False)
            else:
                ctr += 1
                if ctr == 1:
                    self.add_key(419, 420)
                else:
                    self.add_key(420, 420)
        
        self.isString = False

    def get_character(self):
        self.isChar = True
        terminated = False
        self.key = "'"

        self.append_state(self.key, 0, 423)
        if self.peek_next() is not None:
            if self.peek_next() == "'":
                self.add_key(424, 425)
                self.check_delim(key_delims['lit_delim'], ";, ,, &, )", False)
            else:
                self.add_key(423, 424)
                if self.peek_next() == "'":
                    self.add_key(424, 425)
                    self.check_delim(key_delims['lit_delim'], ";, ,, &, )", False)
                else:
                    self.get_key()
                    self.error_message("Character literals must only contain one character", "", False)
        if self.key.count("'") == 2:
            terminated = True
        if not terminated:
            self.error_message("Expected: '", "", False)

        self.isChar = False

    def get_num(self, char):
        self.isInt = True
        curr = char
        self.key = ''

        if curr == '~':
            self.append_state('~', 0, 248)
            self.key += curr
            curr = self.advance()

        if curr == '0':
            while curr == '0':
                curr = self.advance()

        if curr.isdigit():
            self.append_state(curr, 248, 249)
            self.key += curr
            self.check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", 249, 250, "num", False)
            if self.peek_next() == '.':
                self.check_dec(249, 269)
            elif self.peek_next().isdigit():
                self.check_num(249, 251, 252) 
                if self.peek_next() == '.':
                    self.check_dec(251, 284)   
                elif self.peek_next().isdigit():
                    self.check_num(251, 253, 254)
                    if self.peek_next() == '.':
                        self.check_dec(253, 299)
                    elif self.peek_next().isdigit():
                        self.check_num(253, 255, 256)
                        if self.peek_next() == '.':
                            self.check_dec(255, 314)
                        elif self.peek_next().isdigit():
                            self.check_num(255, 257, 258)
                            if self.peek_next() == '.':
                                self.check_dec(257, 329)
                            elif self.peek_next().isdigit():
                                self.check_num(257, 259, 260)
                                if self.peek_next() == '.':
                                    self.check_dec(259, 344)
                                elif self.peek_next().isdigit():
                                    self.check_num(259, 261, 262)
                                    if self.peek_next() == '.':
                                        self.check_dec(261, 359)
                                    elif self.peek_next().isdigit():
                                        self.check_num(261, 263, 264)
                                        if self.peek_next() == '.':
                                            self.check_dec(263, 374)
                                        elif self.peek_next().isdigit():
                                            self.check_num(263, 265, 266)
                                            if self.peek_next() == '.':
                                                self.check_dec(265, 389)
                                            elif self.peek_next().isdigit():
                                                self.check_num(265, 267, 268)
                                                if self.peek_next() == '.':
                                                    self.check_dec(267, 404)

        self.isInt = False
        if not self.matched:
            if self.peek_next() not in whitespace:
                self.get_key()
                if self.key.startswith('~'):
                    max = 11
                else:
                    max = 10
                if '.' in self.key:
                    literal = self.key.split('.')
                    if len(literal[0]) > max:
                        self.error_message(f"{self.key} exceeds maximum length of 10 digits", "", False)
                    if len(literal[1]) > 7:
                        self.error_message(f"{self.key} exceeds maximum length of 7 decimal places", "", False)
                else:
                    if len(self.key) > max:
                        self.error_message(f"{self.key} exceeds maximum length of 10 digits", "", False)

    def get_dec(self):
        self.isInt = False
        self.isDec = True
        trailingZero = ""
        curr = self.advance()
  
        self.key += curr
        self.append_state(curr, self.stateNum, self.stateNum+1)
        self.check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", self.stateNum+1, self.stateNum+2, "num", False)
        if self.peek_next().isdigit():
            self.check_num(self.stateNum+1, self.stateNum+3, self.stateNum+4)
            if self.peek_next().isdigit():
                self.check_num(self.stateNum+3, self.stateNum+5, self.stateNum+6)
                if self.peek_next().isdigit():
                    self.check_num(self.stateNum+5, self.stateNum+7, self.stateNum+8)
                    if self.peek_next().isdigit():
                        self.check_num(self.stateNum+7, self.stateNum+9, self.stateNum+10)
                        if self.peek_next().isdigit():
                            self.check_num(self.stateNum+9, self.stateNum+11, self.stateNum+12)
                            if self.peek_next().isdigit():
                                self.key += trailingZero
                                self.check_num(self.stateNum+11, self.stateNum+13, self.stateNum+14)
        
        if not self.matched:
            if self.peek_next() not in whitespace:
                self.get_key()
                print(f"key decimal: {self.key}")
                self.error_message(f"{self.key} exceeds maximum length of 7 decimal places", "", False)

    def get_id(self):
        self.isIden = True
        curr = self.advance()

        self.key = curr
        self.append_state(curr, 0, 188)
        self.check_if_id(key_delims['iden_delim'], "operator, ;, &, >, (, ), [, ], {, ., ,", 188, 189, "iden", False)
        if self.peek_next() in identifier: 
            self.check_id(188, 190, 191)
            if self.peek_next() in identifier: 
                self.check_id(190, 192, 193)
                if self.peek_next() in identifier: 
                    self.check_id(192, 194, 195)
                    if self.peek_next() in identifier: 
                        self.check_id(194, 196, 197)
                        if self.peek_next() in identifier: 
                            self.check_id(196, 198, 199)
                            if self.peek_next() in identifier: 
                                self.check_id(198, 200, 201)
                                if self.peek_next() in identifier: 
                                    self.check_id(200, 202, 203)
                                    if self.peek_next() in identifier: 
                                        self.check_id(202, 204, 205)
                                        if self.peek_next() in identifier: 
                                            self.check_id(204, 206, 207)
                                            if self.peek_next() in identifier: 
                                                self.check_id(206, 208, 209)
                                                if self.peek_next() in identifier: 
                                                    self.check_id(208, 210, 211)
                                                    if self.peek_next() in identifier: 
                                                        self.check_id(210, 212, 213)
                                                        if self.peek_next() in identifier: 
                                                            self.check_id(212, 214, 215)
                                                            if self.peek_next() in identifier: 
                                                                self.check_id(214, 216, 217)
                                                                if self.peek_next() in identifier: 
                                                                    self.check_id(216, 218, 219)
                                                                    if self.peek_next() in identifier: 
                                                                        self.check_id(218, 220, 221)
                                                                        if self.peek_next() in identifier: 
                                                                            self.check_id(220, 222, 223)
                                                                            if self.peek_next() in identifier: 
                                                                                self.check_id(222, 224, 225)
                                                                                if self.peek_next() in identifier: 
                                                                                    self.check_id(224, 226, 227)
                                                                                    if self.peek_next() in identifier: 
                                                                                        self.check_id(226, 228, 229)
                                                                                        if self.peek_next() in identifier: 
                                                                                            self.check_id(228, 230, 231)
                                                                                            if self.peek_next() in identifier: 
                                                                                                self.check_id(230, 232, 233)
                                                                                                if self.peek_next() in identifier: 
                                                                                                    self.check_id(232, 234, 233)
                                                                                                    if self.peek_next() in identifier: 
                                                                                                        self.check_id(234, 236, 237)
                                                                                                        if self.peek_next() in identifier: 
                                                                                                            self.check_id(236, 238, 239)
                                                                                                            if self.peek_next() in identifier: 
                                                                                                                self.check_id(238, 240, 241)
                                                                                                                if self.peek_next() in identifier: 
                                                                                                                    self.check_id(240, 242, 243)
                                                                                                                    if self.peek_next() in identifier: 
                                                                                                                        self.check_id(242, 244, 245)
                                                                                                                        if self.peek_next() in identifier: 
                                                                                                                            self.check_id(244, 246, 247)

        self.isIden = False
        if not self.matched:
            if self.peek_next() not in whitespace:
                self.get_key()
                if len(self.key) > 30:
                    self.error_message(f"Identifier {self.key} exceeds maximum length of 30 characters", "", False)
            else:
                self.error_message(f"Invalid identifier: {self.key}", "", False)

    def get_lexeme(self):  
        index = len(self.key)
        del state[-index:]
        self.pos -= index
        self.get_id()

    def get_keyword(self, char):
        if char == 'b':
            self.match_found(1, char)
            if self.peek_next() == 'l':
                self.add_key(1, 2)
                if self.peek_next() == 'n':
                    self.add_matched_key(key_delims['data_delim'], "letter, [, (", 2, 3, 4, "word", False)
            elif self.peek_next() == 'r':
                self.add_key(1, 5)
                if self.peek_next() == 'k':
                    self.add_matched_key(key_delims['jmp_delim'], ";", 5, 6, 7, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'c':
            self.match_found(8, char)
            if self.peek_next() == 'h':
                self.add_key(8, 9)
                if self.peek_next() == 'r':
                    self.add_matched_key(key_delims['data_delim'], "letter, [, (", 9, 10, 11, "word", False)
            elif self.peek_next() == 'o':
                self.add_key(8, 12)
                if self.peek_next() == 'n':
                    self.add_key(12, 13)
                    if self.peek_next() == 's':
                        self.add_key(13, 14)
                        if self.peek_next() == 't':
                            self.add_matched_key(whitespace, "space", 14, 15, 16, "word", True)
            if not self.matched:
                self.get_lexeme()

        elif char == 'd':
            self.match_found(17, char)
            if self.peek_next() == 'e':
                self.add_key(17, 18)
                if self.peek_next() == 'c':
                    self.add_matched_key(key_delims['data_delim'], "letter, [, (", 18, 19, 20, "word", False)
                elif self.peek_next() == 'f':
                    self.add_matched_key(key_delims['def_delim'], ":", 18, 21, 22, "word", False)
            elif self.peek_next() == 'i':
                self.add_key(17, 23)
                if self.peek_next() == 's':
                    self.add_key(23, 24)
                    if self.peek_next() == 'p':
                        self.add_matched_key(key_delims['state_delim'], "(", 24, 25, 26, "word", False)
            elif self.peek_next() == 'o':
                self.add_matched_key(key_delims['block_delim'], "{", 17, 27, 28, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'e':
            self.match_found(29, char)
            if self.peek_next() == 'l':
                self.add_key(29, 30)
                if self.peek_next() == 'i':
                    self.add_key(30, 31)
                    if self.peek_next() == 'f':
                        self.add_matched_key(key_delims['state_delim'], "(", 31, 32, 33, "word", False)
                elif self.peek_next() == 's':
                    self.add_key(30, 34)
                    if self.peek_next() == 'e':
                        self.add_matched_key(key_delims['block_delim'], "{", 34, 35, 36, "word", False)
            elif self.peek_next() == 'x':
                self.add_key(29, 37)
                if self.peek_next() == 'i':
                    self.add_key(37, 38)
                    if self.peek_next() == 't':
                        self.add_matched_key(key_delims['jmp_delim'], ";", 38, 39, 40, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'f':
            self.match_found(41, char)
            if self.peek_next() == 'a':
                self.add_key(41, 42)
                if self.peek_next() == 'l':
                    self.add_key(42, 43)
                    if self.peek_next() == 's':
                        self.add_key(43, 44)
                        if self.peek_next() == 'e':
                            self.add_matched_key(key_delims['val_delim'], ";, ,, ), }", 44, 45, 46, "word", False)
            elif self.peek_next() == 'o':
                self.add_key(41, 47)
                if self.peek_next() == 'r':
                    self.add_key(47, 48)
                    if self.peek_next() != 'e':
                        matched = True
                        self.check_if_id(key_delims['state_delim'], "(", 48, 49, "word", False)
                    else:
                        self.add_key(48, 50)
                        if self.peek_next() == 'a':
                            self.add_key(50, 51)
                            if self.peek_next() == 'c':
                                self.add_key(51, 52)
                                if self.peek_next() == 'h':
                                    self.add_matched_key(key_delims['state_delim'], "(", 52, 53, 54, "word", False)  
            if not self.matched:
                self.get_lexeme()

        elif char == 'i':
            self.match_found(55, char)
            if self.peek_next() == 'f':
                self.add_matched_key(key_delims['state_delim'], "(", 55, 56, 57, "word", False)
            elif self.peek_next() == 'n':
                self.add_key(55, 58)
                if self.peek_next() != 's' and self.peek_next() != 't':
                    matched = True
                    self.check_if_id(whitespace, "identifier", 58, 59, "word", True)
                elif self.peek_next() == 's':
                    self.add_key(58, 60)
                    if self.peek_next() == 'p':
                        self.add_matched_key(key_delims['state_delim'], "(", 60, 61, 62, "word", False)
                elif self.peek_next() == 't':
                    self.add_matched_key(key_delims['data_delim'], "identifier, [, (", 58, 63, 64, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'k':
            self.match_found(65, char)
            if self.peek_next() == 'e':
                self.add_key(65, 66)
                if self.peek_next() == 'y':
                    self.add_matched_key(whitespace, "literal", 66, 67, 68, "word", True)
            if not self.matched:
                self.get_lexeme()

        elif char == 'm':
            self.match_found(69, char)
            if self.peek_next() == 'a':
                self.add_key(69, 70)
                if self.peek_next() == 'i':
                    self.add_key(70, 71)
                    if self.peek_next() == 'n':
                        self.add_matched_key(key_delims['state_delim'], "(", 71, 72, 73, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'n':
            self.match_found(74, char)
            if self.peek_next() == 'o':
                self.add_key(74, 75)
                if self.peek_next() == 'n':
                    self.add_key(75, 76)
                    if self.peek_next() == 'e':
                        self.add_matched_key(key_delims['val_delim'], ";, ,, ), }", 76, 77, 78, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'r':
            self.match_found(79, char)
            if self.peek_next() == 'e':
                self.add_key(79, 80)
                if self.peek_next() == 't':
                    self.add_matched_key(whitespace, "literal", 80, 81, 82, "word", True )
            elif self.peek_next() == 's':
                self.add_key(79, 83)
                if self.peek_next() == 'm':
                    self.add_matched_key(key_delims['jmp_delim'], ";", 83, 84, 85, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 's':
            self.match_found(86, char)
            if self.peek_next() == 'e':
                self.add_key(86, 87)
                if self.peek_next() == 'g':
                    self.add_key(87, 88)
                    if self.peek_next() == 'm':
                        self.add_matched_key(whitespace, "identifier", 88, 89, 90, "word", True)
            elif self.peek_next() == 't':
                self.add_key(86, 91)
                if self.peek_next() == 'r':
                    self.add_key(91, 92)
                    if self.peek_next() != 'c':
                        matched = True
                        self.check_if_id(key_delims["data_delim"], "letter, [, (", 92, 93, "word", False)
                    else:
                        self.add_matched_key(whitespace, "identifier", 92, 94, 95, "word", True)
            elif self.peek_next() == 'w':
                self.add_key(86, 96)
                if self.peek_next() == 'i':
                    self.add_key(96, 97)
                    if self.peek_next() == 't':
                        self.add_key(97, 98)
                        if self.peek_next() == 'c':
                            self.add_key(98, 99)
                            if self.peek_next() == 'h':
                                self.add_matched_key(key_delims['state_delim'], "(", 99, 100, 101, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 't':
            self.match_found(102, char)
            if self.peek_next() == 'r':
                self.add_key(102, 103)
                if self.peek_next() == 'u':
                    self.add_key(103, 104)
                    if self.peek_next() == 'e':
                        self.add_matched_key(key_delims['val_delim'], ";, ,, ), }", 104, 105, 106, "word", False)
            if not self.matched:
                self.get_lexeme()

        elif char == 'v':
            self.match_found(107, char)
            if self.peek_next() == 'a':
                self.add_key(107, 108)
                if self.peek_next() == 'r':
                    self.add_matched_key(whitespace, "identifier", 108, 109, 110, "word", True)
            if not self.matched:
                self.get_lexeme()

        elif char == 'w':
            self.match_found(111, char)
            if self.peek_next() == 'h':
                self.add_key(111, 112)
                if self.peek_next() == 'i':
                    self.add_key(112, 113)
                    if self.peek_next() == 'l':
                        self.add_key(113, 114)
                        if self.peek_next() == 'e':
                            self.add_matched_key(key_delims['state_delim'], "(", 114, 115, 116, "word", False)
            if not self.matched:
                self.get_lexeme()

        else:
            self.key = char
            self.get_lexeme()

    def get_symbol(self, char):
        def symbol_error():
            self.get_key()
            self.error_message(f"{self.key} => invalid operator", "", False)

        if char == '=':
            self.match_found(117, char)
            if self.peek_next() == '=':
                self.add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 117, 119, 120, "symbol", False)
            else:
                self.check_symbol(key_delims['asn_delim'], "letter, number, (, ~, !, ', \", {, #", 117, 118, False)
            if not self.matched:
                symbol_error()

        elif char == '+':
            self.match_found(121, char)
            if self.peek_next() == '+':
                self.add_matched_key(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 121, 123, 124, "symbol", False)
            elif self.peek_next() == '=':
                self.add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 121, 125, 126, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 121, 122, False)
            if not self.matched:
                symbol_error()

        elif char == '-':
            self.match_found(127, char)
            if self.peek_next() == '-':
                self.add_matched_key(key_delims['unary_delim'], "letter, number, (, ), ;, ,, ~", 127, 129, 130, "symbol", False)
            elif self.peek_next() == '=':
                self.add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 127, 131, 132, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 127, 128, False)
            if not self.matched:
                symbol_error()
                        
        elif char == '*':
            self.match_found(133, char)
            if self.peek_next() == '=':
                self.add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 133, 135, 136, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 133, 134, False)
            if not self.matched:
                symbol_error()

        elif char == '/':
            self.match_found(137, char)
            if self.peek_next() == '=':
                self.add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 137, 139, 140, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 137, 138, False)
            if not self.matched:
                symbol_error()

        elif char == '%':
            self.match_found(141, char)
            if self.peek_next() == '=':
                self.add_matched_key(key_delims['op_delim'], "letter, number, (, ~", 141, 143, 144, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 141, 142, False)
            if not self.matched:
                symbol_error()

        elif char == '&':
            self.match_found(145, char)
            if self.peek_next() == '&':
                self.add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 145, 147, 148, "symbol", False)
            else:
                self.check_symbol(key_delims['concat_delim'], "letter, (, \", ', #", 145, 146, False)
            if not self.matched:
                symbol_error()
                
        elif char == '|':
            self.match_found(149, char)
            if self.peek_next() == '|':
                self.add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 149, 150, 151, "symbol", False)
            if not self.matched:
                symbol_error()

        elif char == '!':
            self.match_found(152, char)
            if self.peek_next() == '=':
                self.add_matched_key(key_delims['relate_delim'], "letter, number, (, ~, !, ', \"", 152, 154, 155, "symbol", False)
            else:
                self.check_symbol(key_delims['relate_delim'], "letter, (, \", ', #", 152, 153, False)
            if not self.matched:
                symbol_error()

        elif char == '<':
            self.match_found(156, char)
            if self.peek_next() == '<':
                self.add_matched_key(key_delims['var_delim'], "letter, +, -, ], ,", 156, 158, 159, "symbol", False)
            elif self.peek_next() == '=':
                self.add_matched_key(key_delims['relate1_delim'], "letter, number, (, ~, !", 156, 160, 161, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 156, 157, False)
            if not self.matched:
                symbol_error()

        elif char == '>':
            self.match_found(162, char)
            if self.peek_next() == '>':
                self.add_matched_key(key_delims['var1_delim'], "ASCII Character", 162, 164, 164, "symbol", False)
            elif self.peek_next() == '=':
                self.add_matched_key(key_delims['relate1_delim'], "letter, number, (, ~, !", 162, 166, 167, "symbol", False)
            else:
                self.check_symbol(key_delims['op_delim'], "letter, number, (, ~", 162, 163, False)
            if not self.matched:
                symbol_error()

        elif char == '[':
            self.match_found(168, char)
            self.check_symbol(key_delims['bracket_delim'], "letter, number, ], ,, +, -", 168, 169, False)
            if not self.matched:
                symbol_error()

        elif char == ']':
            self.match_found(170, char)
            self.check_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '>'", 170, 171, False)
            if not self.matched:
                symbol_error()

        elif char == '{':
            self.match_found(172, char)
            self.check_symbol(key_delims['brace_delim'], "letter, number, +, -, ;, (, ', \", {, }", 172, 173, False)
            if not self.matched:
                symbol_error()

        elif char == '}':
            self.match_found(174, char)
            self.check_symbol(key_delims['brace1_delim'], "letter, number, +, -, ;, (, }, ;, ,", 174, 175, False)
            if not self.matched:
                symbol_error()

        elif char == '(':
            self.match_found(176, char)
            self.check_symbol(key_delims['paren_delim'], "letter, number, +, -, ;, !, #, ', \", (, )", 176, 177, False)
            if not self.matched:
                symbol_error()

        elif char == ')':
            self.match_found(178, char)
            self.check_symbol(key_delims['paren1_delim'], "+, -, *, /, %, =, !, <, >, &, |, {, ), ;", 178, 179, False)
            if not self.matched:
                symbol_error()

        elif char == ',':
            self.match_found(180, char)
            self.check_symbol(key_delims['comma_delim'], "letter, number, +, -, ], (, {, \", '", 180, 181, False)
            if not self.matched:
                symbol_error()

        elif char == ';':
            self.match_found(182, char)
            self.check_symbol(key_delims['semicolon_delim'], "letter, number, +, -, (, }", 182, 183, False)
            if not self.matched:
                symbol_error()

        elif char == ':':
            self.match_found(184, char)
            self.check_symbol(key_delims['colon_delim'], "letter, number, +, -, (", 184, 185, False)
            if not self.matched:
                symbol_error()

        elif char == '#':
            self.match_found(186, char)
            self.check_symbol(key_delims['interpol_delim'], "\"", 186, 187, False)
            if not self.matched:
                symbol_error()

        elif char == '.' or char == '_':
            self.key = char
            self.get_key()
            if self.key.startswith('.') and self.key[1:].isdigit():
                self.error_message(f"Invalid decimal value: {self.key}", "", False)
            else:
                self.error_message(f"Invalid identifier: {self.key}", "", False)
        
        else:
            self.key = char
            self.get_key()
            self.error_message(f"Invalid: {self.key}", "", False)

    def check_num(self, s1, s2, s3):
        self.add_key(s1, s2)
        self.check_if_id(key_delims['num_delim'], "operator, ;, ), }, ], ,", s2, s3, "num", False)

    def check_dec(self, s1, s2):
        self.add_key(s1, s2)
        if self.peek_next() in whitespace:
            self.error_message(f"Invalid decimal: {self.key}", "", False)
        else:
            self.stateNum = s2
            self.get_dec()

    def check_id(self, s1, s2, s3):
        self.add_key(s1, s2)
        self.check_if_id(key_delims['iden_delim'], "operator, ;, &, >, (, ), [, ], {, ., ,", s2, s3, "iden", True)

    def check_symbol(self, delim, expected, stateNum1, stateNum2, requiredSpace):
        if self.peek_next() in whitespace or self.peek_next() in delim or self.peek_next() in punc_symbols:
            self.matched = True
            self.check_delim(delim, expected, requiredSpace)
            self.append_state("end", stateNum1, stateNum2)

    def check_delim(self, delim, expected, requiredSpace):
        if self.isIden: self.append_key('id')
        elif self.isChar: self.append_key('chr_lit')
        elif self.isString: self.append_key('str_lit')
        elif self.isInt: self.append_key('int_lit')
        elif self.isDec: self.append_key('dec_lit')
        else: self.append_key(self.key)

        if not requiredSpace:
            self.skip_whitespace()

        if self.peek_next() not in delim:
            self.error_message(f"Unexpected {self.advance()} after {self.key}", expected, True)
            self.advance()

    def check_if_id(self, delim, expected, stateNum1, stateNum2, reserved, requiredSpace):
        if reserved == "word":
            if self.peek_next() not in whitespace and (self.peek_next().isalnum() or self.peek_next() == '_'):
                matched = False
                return
        elif reserved in ["symbol", "iden", "num"]:
            if self.peek_next() not in whitespace and self.peek_next() not in delim:
                self.matched = False
                return

        self.matched = True
        state.append(f"end : {stateNum1}-{stateNum2}")

        if reserved == "num":
            self.key = self.key.rstrip('0')

        self.check_delim(delim, expected, requiredSpace)

    def append_state(self, stateChar, stateNum1, stateNum2):
        state.append(f"{stateChar} : {stateNum1}-{stateNum2}")
    
    def append_key(self, lit):
        lexeme.append(self.key) 
        token.append(lit)

    def add_key(self, stateNum1, stateNum2):
        state.append(f"{self.peek_next()} : {stateNum1}-{stateNum2}")
        self.key += self.advance()

    def add_matched_key(self, delim, expected, s1, s2, s3, reserved, requiredSpace):
        self.add_key(s1, s2)
        self.matched = True
        self.check_if_id(delim, expected, s2, s3, reserved, requiredSpace)

    def get_key(self):
        while self.peek_next() not in whitespace:
            self.key += self.advance()

    def match_found(self, state, char):
        self.key = char
        self.matched = False
        self.append_state(char, 0, state)