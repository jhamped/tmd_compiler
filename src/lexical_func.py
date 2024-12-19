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
        self.invalid = False
        self.struct = False

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
            if char == '*' and self.peek_next() == '/' and char != None:
                self.advance() 
                break
            elif char == None:
                break

    def error_message(self, error, expected, expectedError):
        self.console.insert(tk.END, "Error: ", "error")
        self.console.insert(tk.END, f"{error}")
        if expectedError:
            self.console.insert(tk.END, f"  Expected: {expected}", "expected")
        self.console.insert(tk.END, f"\n       line {self.line}, column {self.col}\n", "ln_col")

class GetLitAndIden: 
    def __init__(self, lex):
        self.lex = lex
        self.modify = StateAndKeyManipulation(lex)
        self.check = Checkers(lex)

    def get_string(self):
        self.lex.isString = True
        self.lex.key = '"'
        self.modify.append_state(self.lex.key, 0, 421)
        ctr = 0

        while True:
            if self.lex.peek_next() is None:  
                self.lex.error_message("Expected: \"", "", False)
                break
            if self.lex.peek_next() == '"': 
                self.modify.add_key(422, 423)
                self.check.check_delim(key_delims['lit_delim'], "';', ',', '&', ')', '}', '!', '=', '|', ':'", False)
                break
            elif self.lex.peek_next() == '\\': 
                esc = self.lex.advance()
                if self.lex.peek_next() in ['\\', '"', 'n', 't']: 
                    esc += self.lex.advance()
                    self.lex.key += esc
                    ctr += 1
                    if ctr == 1:
                        self.modify.append_state(esc, 421, 422)
                    else:
                        self.modify.append_state(esc, 422, 422)
                else:
                    self.lex.error_message(f"Invalid escape sequence: \\{esc}", "", False)
            elif self.lex.peek_next() == "\n":
                curr = self.lex.advance()
                while self.lex.peek_next() != '"' and self.lex.peek_next() != None:
                    self.lex.key += curr
                    curr = self.lex.advance()
                if self.lex.peek_next() == '"':
                    self.lex.key += curr
                    self.lex.key += self.lex.advance()
                else:
                    continue
                self.lex.error_message(f"Invalid string: {self.lex.key}", "", False)
                break
            else:
                ctr += 1
                if ctr == 1:
                    self.modify.add_key(421, 422)
                else:
                    self.modify.add_key(422, 422)
        
        self.lex.isString = False

    def get_character(self):
        self.lex.isChar = True
        terminated = False
        self.lex.key = "'"

        self.modify.append_state(self.lex.key, 0, 425)
        if self.lex.peek_next() is not None:
            if self.lex.peek_next() == "'":
                self.modify.add_key(426, 427)
                self.check.check_delim(key_delims['lit_delim'], "';', ',', '&', ')', '}', '!', '=', '|', ':'", False)
            else:
                self.modify.add_key(425, 426)
                if self.lex.peek_next() == "'":
                    self.modify.add_key(426, 427)
                    self.check.check_delim(key_delims['lit_delim'], "';', ',', '&', ')', '}', '!', '=', '|', ':'", False)
                else:
                    self.modify.get_key(key_delims['lit_delim'])
                    self.lex.error_message("Character literals must only contain one character", "", False)
        if self.lex.key.count("'") == 2:
            terminated = True
        if not terminated:
            self.lex.error_message("Expected: '", "", False)

        self.lex.isChar = False

    def get_num(self, char):
        self.lex.matched = False
        self.lex.isInt = True
        curr = char
        self.lex.key = ''

        if curr == '~':
            self.modify.append_state('~', 0, 250)
            self.lex.key += curr
            curr = self.lex.advance()

        if curr == '0' and not (self.lex.peek_next() in whitespace or self.lex.peek_next() in key_delims['num_delim']) and self.lex.peek_next() != '.':
            while curr == '0' and not (self.lex.peek_next() in whitespace or self.lex.peek_next() in key_delims['num_delim']) and self.lex.peek_next() != '.':
                curr = self.lex.advance()

        if curr in digit:
            self.modify.append_state(curr, 250, 251)
            self.lex.key += curr
            self.check.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", 251, 252, "num", False)
            if self.lex.peek_next() == '.':
                self.check.check_dec(251, 271)
            elif self.lex.peek_next() in digit:
                self.check.check_num(251, 253, 254) 
                if self.lex.peek_next() == '.':
                    self.check.check_dec(253, 286)   
                elif self.lex.peek_next() in digit:
                    self.check.check_num(253, 255, 256)
                    if self.lex.peek_next() == '.':
                        self.check.check_dec(255, 301)
                    elif self.lex.peek_next() in digit:
                        self.check.check_num(255, 257, 258)
                        if self.lex.peek_next() == '.':
                            self.check.check_dec(257, 316)
                        elif self.lex.peek_next() in digit:
                            self.check.check_num(257, 259, 260)
                            if self.lex.peek_next() == '.':
                                self.check.check_dec(259, 331)
                            elif self.lex.peek_next() in digit:
                                self.check.check_num(259, 261, 262)
                                if self.lex.peek_next() == '.':
                                    self.check.check_dec(261, 346)
                                elif self.lex.peek_next() in digit:
                                    self.check.check_num(261, 263, 264)
                                    if self.lex.peek_next() == '.':
                                        self.check.check_dec(263, 361)
                                    elif self.lex.peek_next() in digit:
                                        self.check.check_num(263, 265, 266)
                                        if self.lex.peek_next() == '.':
                                            self.check.check_dec(265, 376)
                                        elif self.lex.peek_next() in digit:
                                            self.check.check_num(265, 267, 268)
                                            if self.lex.peek_next() == '.':
                                                self.check.check_dec(267, 391)
                                            elif self.lex.peek_next() in digit:
                                                self.check.check_num(267, 269, 270)
                                                if self.lex.peek_next() == '.':
                                                    self.check.check_dec(269, 406)

        self.lex.isInt = False
        if not self.lex.matched:
            if self.lex.peek_next() not in whitespace:
                self.lex.key += curr
                self.modify.get_key(key_delims['num_delim'])
                if self.lex.key.startswith('~'):
                    max = 11
                    if not self.lex.key[1].isdigit():
                        if '.' in self.lex.key:
                            self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)
                        else:
                            if self.lex.peek_next() in [')', '}', ']']:
                                self.lex.key += self.lex.advance()
                            self.lex.error_message(f"Invalid: {self.lex.key}", "", False)
                else:
                    max = 10
                if '.' in self.lex.key:
                    literal = self.lex.key.split('.')
                    if len(literal[0]) > max:
                        self.lex.error_message(f"{self.lex.key} exceeds maximum length of 10 digits", "", False)
                        if len(literal[1]) > 7:
                            self.lex.error_message(f"{self.lex.key} exceeds maximum length of 7 decimal places", "", False)
                else:   
                    if len(self.lex.key) > max:
                        self.lex.error_message(f"{self.lex.key} exceeds maximum length of 10 digits", "", False)

    def get_dec(self):
        self.lex.isInt = False
        self.lex.isDec = True
        decimal = ''
        curr = self.lex.advance()
        self.lex.key += curr

        if curr in digit:
            decimal += curr
            self.modify.append_state(curr, self.lex.stateNum, self.lex.stateNum+1)
            self.check.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", self.lex.stateNum+1, self.lex.stateNum+2, "num", False)
            if self.lex.peek_next() in digit:
                decimal += self.lex.peek_next()
                self.check.check_num(self.lex.stateNum+1, self.lex.stateNum+3, self.lex.stateNum+4)
                if self.lex.peek_next() in digit:
                    decimal += self.lex.peek_next()
                    self.check.check_num(self.lex.stateNum+3, self.lex.stateNum+5, self.lex.stateNum+6)
                    if self.lex.peek_next() in digit:
                        decimal += self.lex.peek_next()
                        self.check.check_num(self.lex.stateNum+5, self.lex.stateNum+7, self.lex.stateNum+8)
                        if self.lex.peek_next() in digit:
                            decimal += self.lex.peek_next()
                            self.check.check_num(self.lex.stateNum+7, self.lex.stateNum+9, self.lex.stateNum+10)
                            if self.lex.peek_next() in digit:
                                decimal += self.lex.peek_next()
                                self.check.check_num(self.lex.stateNum+9, self.lex.stateNum+11, self.lex.stateNum+12)
                                if self.lex.peek_next() in digit:
                                    decimal += self.lex.peek_next()
                                    self.check.check_num(self.lex.stateNum+11, self.lex.stateNum+13, self.lex.stateNum+14)
        
        if not self.lex.matched:
            lex = ''
            invalid = False
            if self.lex.peek_next() not in whitespace:
                if curr not in digit:
                    lex += curr
                    invalid = True
                while self.lex.peek_next() not in whitespace and self.lex.peek_next() not in key_delims['num_delim']:
                    lex += self.lex.advance()
                if all(char == '0' for char in lex) and lex != '':
                    self.check.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", 0, 0, "num", False)
                    return
                if invalid:
                    lex = lex[1:]
                self.lex.key += lex
                decimal += lex
                if len(decimal) >= 7:
                    self.lex.error_message(f"{self.lex.key} exceeds maximum length of 7 decimal places", "", False)
                    return
                if self.lex.key.count('.') > 1:
                    self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)
                    return
            self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)

    def get_id(self):
        self.lex.isIden = True
        curr = self.lex.advance()

        self.lex.key = curr
        self.modify.append_state(curr, 0, 190)
        self.check.check_if_match(key_delims['iden_delim'], "operator, ';', '&', '>', '(', ')', '[', ']', '{', '}', '.', ','", 190, 191, "iden", False)
        if self.lex.peek_next() in identifier: 
            self.check.check_id(190, 192, 193)
            if self.lex.peek_next() in identifier: 
                self.check.check_id(192, 194, 195)
                if self.lex.peek_next() in identifier: 
                    self.check.check_id(194, 196, 197)
                    if self.lex.peek_next() in identifier: 
                        self.check.check_id(196, 198, 199)
                        if self.lex.peek_next() in identifier: 
                            self.check.check_id(198, 200, 201)
                            if self.lex.peek_next() in identifier: 
                                self.check.check_id(200, 202, 203)
                                if self.lex.peek_next() in identifier: 
                                    self.check.check_id(202, 204, 205)
                                    if self.lex.peek_next() in identifier: 
                                        self.check.check_id(204, 206, 207)
                                        if self.lex.peek_next() in identifier: 
                                            self.check.check_id(206, 208, 209)
                                            if self.lex.peek_next() in identifier: 
                                                self.check.check_id(208, 210, 211)
                                                if self.lex.peek_next() in identifier: 
                                                    self.check.check_id(210, 212, 213)
                                                    if self.lex.peek_next() in identifier: 
                                                        self.check.check_id(212, 214, 215)
                                                        if self.lex.peek_next() in identifier: 
                                                            self.check.check_id(214, 216, 217)
                                                            if self.lex.peek_next() in identifier: 
                                                                self.check.check_id(216, 218, 219)
                                                                if self.lex.peek_next() in identifier: 
                                                                    self.check.check_id(218, 220, 221)
                                                                    if self.lex.peek_next() in identifier: 
                                                                        self.check.check_id(220, 222, 223)
                                                                        if self.lex.peek_next() in identifier: 
                                                                            self.check.check_id(222, 224, 225)
                                                                            if self.lex.peek_next() in identifier: 
                                                                                self.check.check_id(224, 226, 227)
                                                                                if self.lex.peek_next() in identifier: 
                                                                                    self.check.check_id(226, 228, 229)
                                                                                    if self.lex.peek_next() in identifier: 
                                                                                        self.check.check_id(228, 230, 231)
                                                                                        if self.lex.peek_next() in identifier: 
                                                                                            self.check.check_id(230, 232, 233)
                                                                                            if self.lex.peek_next() in identifier: 
                                                                                                self.check.check_id(232, 234, 235)
                                                                                                if self.lex.peek_next() in identifier: 
                                                                                                    self.check.check_id(234, 236, 237)
                                                                                                    if self.lex.peek_next() in identifier: 
                                                                                                        self.check.check_id(236, 238, 239)
                                                                                                        if self.lex.peek_next() in identifier: 
                                                                                                            self.check.check_id(238, 240, 241)
                                                                                                            if self.lex.peek_next() in identifier: 
                                                                                                                self.check.check_id(240, 242, 243)
                                                                                                                if self.lex.peek_next() in identifier: 
                                                                                                                    self.check.check_id(242, 244, 245)
                                                                                                                    if self.lex.peek_next() in identifier: 
                                                                                                                        self.check.check_id(244, 246, 247)
                                                                                                                        if self.lex.peek_next() in identifier: 
                                                                                                                            self.check.check_id(246, 248, 249)

        self.lex.isIden = False
        if self.lex.invalid:
            self.modify.get_key("")
            self.lex.invalid = False
            self.lex.error_message(f"Invalid identifier: {self.lex.key}", "", False)

        if not self.lex.matched:
            if self.lex.peek_next() not in whitespace:
                self.modify.get_key(key_delims['iden_delim'])
                if len(self.lex.key) > 30:
                    self.lex.error_message(f"Identifier {self.lex.key} exceeds maximum length of 30 characters", "", False)
                else:
                    self.lex.error_message(f"Invalid identifier: {self.lex.key}", "", False)

    def get_lexeme(self):  
        index = len(self.lex.key)
        del state[-index:]
        self.lex.pos -= index
        self.get_id()

    def get_keyword(self, char):
        self.lex.isIden = False

        if char == 'b':
            self.modify.match_found(1, char)
            if self.lex.peek_next() == 'l':
                self.modify.add_key(1, 2)
                if self.lex.peek_next() == 'n':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 2, 3, 4, "word", False)
            elif self.lex.peek_next() == 'r':
                self.modify.add_key(1, 5)
                if self.lex.peek_next() == 'k':
                    self.modify.add_matched_key(key_delims['jmp_delim'], "';'", 5, 6, 7, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'c':
            self.modify.match_found(8, char)
            if self.lex.peek_next() == 'h':
                self.modify.add_key(8, 9)
                if self.lex.peek_next() == 'r':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 9, 10, 11, "word", False)
            elif self.lex.peek_next() == 'o':
                self.modify.add_key(8, 12)
                if self.lex.peek_next() == 'n':
                    self.modify.add_key(12, 13)
                    if self.lex.peek_next() == 's':
                        self.modify.add_key(13, 14)
                        if self.lex.peek_next() == 't':
                            self.modify.add_matched_key(whitespace, "whitespace", 14, 15, 16, "word", True)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'd':
            self.modify.match_found(17, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(17, 18)
                if self.lex.peek_next() == 'c':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 18, 19, 20, "word", False)
                elif self.lex.peek_next() == 'f':
                    self.modify.add_matched_key(key_delims['def_delim'], "':'", 18, 21, 22, "word", False)
            elif self.lex.peek_next() == 'i':
                self.modify.add_key(17, 23)
                if self.lex.peek_next() == 's':
                    self.modify.add_key(23, 24)
                    if self.lex.peek_next() == 'p':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 24, 25, 26, "word", False)
            elif self.lex.peek_next() == 'o':
                self.modify.add_matched_key(key_delims['block_delim'], "'{'", 17, 27, 28, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'e':
            self.modify.match_found(29, char)
            if self.lex.peek_next() == 'l':
                self.modify.add_key(29, 30)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(30, 31)
                    if self.lex.peek_next() == 'f':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 31, 32, 33, "word", False)
                elif self.lex.peek_next() == 's':
                    self.modify.add_key(30, 34)
                    if self.lex.peek_next() == 'e':
                        self.modify.add_matched_key(key_delims['block_delim'], "'{'", 34, 35, 36, "word", False)
            elif self.lex.peek_next() == 'x':
                self.modify.add_key(29, 37)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(37, 38)
                    if self.lex.peek_next() == 't':
                        self.modify.add_matched_key(key_delims['jmp_delim'], "';'", 38, 39, 40, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'f':
            self.modify.match_found(41, char)
            if self.lex.peek_next() == 'a':
                self.modify.add_key(41, 42)
                if self.lex.peek_next() == 'l':
                    self.modify.add_key(42, 43)
                    if self.lex.peek_next() == 's':
                        self.modify.add_key(43, 44)
                        if self.lex.peek_next() == 'e':
                            self.modify.add_matched_key(key_delims['val_delim'], "';', ',', ')', '}', '!', '&', '='", 44, 45, 46, "word", False)
            elif self.lex.peek_next() == 'o':
                self.modify.add_key(41, 47)
                if self.lex.peek_next() == 'r':
                    self.modify.add_key(47, 48)
                    if self.lex.peek_next() != 'e':
                        self.lexmatched = True
                        self.check.check_if_match(key_delims['state_delim'], "'('", 48, 49, "word", False)
                    else:
                        self.modify.add_key(48, 50)
                        if self.lex.peek_next() == 'a':
                            self.modify.add_key(50, 51)
                            if self.lex.peek_next() == 'c':
                                self.modify.add_key(51, 52)
                                if self.lex.peek_next() == 'h':
                                    self.modify.add_matched_key(key_delims['state_delim'], "'('", 52, 53, 54, "word", False)  
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'i':
            self.modify.match_found(55, char)
            if self.lex.peek_next() == 'f':
                self.modify.add_matched_key(key_delims['state_delim'], "'('", 55, 56, 57, "word", False)
            elif self.lex.peek_next() == 'n':
                self.modify.add_key(55, 58)
                if self.lex.peek_next() != 's' and self.lex.peek_next() != 't':
                    self.lex.matched = True
                    self.check.check_if_match(whitespace, "alpha", 58, 59, "word", True)
                elif self.lex.peek_next() == 's':
                    self.modify.add_key(58, 60)
                    if self.lex.peek_next() == 'p':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 60, 61, 62, "word", False)
                elif self.lex.peek_next() == 't':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 58, 63, 64, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'k':
            self.modify.match_found(65, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(65, 66)
                if self.lex.peek_next() == 'y':
                    self.modify.add_matched_key(whitespace, "whitespace", 66, 67, 68, "word", True)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'm':
            self.modify.match_found(69, char)
            if self.lex.peek_next() == 'a':
                self.modify.add_key(69, 70)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(70, 71)
                    if self.lex.peek_next() == 'n':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 71, 72, 73, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'n':
            self.modify.match_found(74, char)
            if self.lex.peek_next() == 'o':
                self.modify.add_key(74, 75)
                if self.lex.peek_next() == 'n':
                    self.modify.add_key(75, 76)
                    if self.lex.peek_next() == 'e':
                        self.modify.add_matched_key(key_delims['val_delim'], "';', ',', ')', '}', '!', '&', '='", 76, 77, 78, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'r':
            self.modify.match_found(79, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(79, 80)
                if self.lex.peek_next() == 't':
                    self.modify.add_matched_key(whitespace, "whitespace", 80, 81, 82, "word", True )
            elif self.lex.peek_next() == 's':
                self.modify.add_key(79, 83)
                if self.lex.peek_next() == 'm':
                    self.modify.add_matched_key(key_delims['jmp_delim'], "';'", 83, 84, 85, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 's':
            self.modify.match_found(86, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(86, 87)
                if self.lex.peek_next() == 'g':
                    self.modify.add_key(87, 88)
                    if self.lex.peek_next() == 'm':
                        self.modify.add_matched_key(whitespace, "whitespace", 88, 89, 90, "word", True)
            elif self.lex.peek_next() == 't':
                self.modify.add_key(86, 91)
                if self.lex.peek_next() == 'r':
                    self.modify.add_key(91, 92)
                    if self.lex.peek_next() != 'c':
                        self.lex.matched = True
                        self.check.check_if_match(key_delims["data_delim"], "whitespace, '[', '('", 92, 93, "word", False)
                    else:
                        self.modify.add_matched_key(whitespace, "whitespace", 92, 94, 95, "word", True)
            elif self.lex.peek_next() == 'w':
                self.modify.add_key(86, 96)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(96, 97)
                    if self.lex.peek_next() == 't':
                        self.modify.add_key(97, 98)
                        if self.lex.peek_next() == 'c':
                            self.modify.add_key(98, 99)
                            if self.lex.peek_next() == 'h':
                                self.modify.add_matched_key(key_delims['state_delim'], "'('", 99, 100, 101, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 't':
            self.modify.match_found(102, char)
            if self.lex.peek_next() == 'r':
                self.modify.add_key(102, 103)
                if self.lex.peek_next() == 'u':
                    self.modify.add_key(103, 104)
                    if self.lex.peek_next() == 'e':
                        self.modify.add_matched_key(key_delims['val_delim'], "';', ',', ')', '}', '!', '&', '='", 104, 105, 106, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'v':
            self.modify.match_found(107, char)
            if self.lex.peek_next() == 'a':
                self.modify.add_key(107, 108)
                if self.lex.peek_next() == 'r':
                    self.modify.add_matched_key(whitespace, "whitespace", 108, 109, 110, "word", True)
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'w':
            self.modify.match_found(111, char)
            if self.lex.peek_next() == 'h':
                self.modify.add_key(111, 112)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(112, 113)
                    if self.lex.peek_next() == 'l':
                        self.modify.add_key(113, 114)
                        if self.lex.peek_next() == 'e':
                            self.modify.add_matched_key(key_delims['state_delim'], "'('", 114, 115, 116, "word", False)
            if not self.lex.matched:
                self.get_lexeme()

        else:
            self.lex.key = char
            self.get_lexeme()

    def get_symbol(self, char):
        if char == '=':
            self.modify.match_found(117, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 117, 119, 120, "symbol", False)
            else:
                self.check.check_symbol(key_delims['asn_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"', '{', '#'", 117, 118, False)

        elif char == '+':
            self.modify.match_found(121, char)
            if self.lex.peek_next() == '+':
                self.modify.add_matched_key(key_delims['unary_delim'], "alpha, number, '(', ')', ';', ',', '~'", 121, 123, 124, "symbol", False)
            elif self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 121, 125, 126, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 121, 122, False)

        elif char == '-':
            self.modify.match_found(127, char)
            if self.lex.peek_next() == '-':
                self.modify.add_matched_key(key_delims['unary_delim'], "alpha, number, '(', ')', ';', ',', '~'", 127, 129, 130, "symbol", False)
            elif self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 127, 131, 132, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 127, 128, False)
                        
        elif char == '*':
            self.modify.match_found(133, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 133, 135, 136, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 133, 134, False)

        elif char == '/':
            self.modify.match_found(137, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 137, 139, 140, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 137, 138, False)

        elif char == '%':
            self.modify.match_found(141, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 141, 143, 144, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 141, 142, False)

        elif char == '&':
            self.modify.match_found(145, char)
            if self.lex.peek_next() == '&':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 145, 147, 148, "symbol", False)
            else:
                self.check.check_symbol(key_delims['concat_delim'], "alpha,'(', '\"', '\'', '#'", 145, 146, False)
                
        elif char == '|':
            self.modify.match_found(149, char)
            if self.lex.peek_next() == '|':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 149, 150, 151, "symbol", False)

        elif char == '!':
            self.modify.match_found(152, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 152, 154, 155, "symbol", False)
            else:
                self.check.check_symbol(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 152, 153, False)

        elif char == '<':
            self.modify.match_found(156, char)
            if self.lex.peek_next() == '<':
                self.modify.add_matched_key(key_delims['var_delim'], "alpha,'(', '+', '-'", 156, 158, 159, "symbol", False)
            elif self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate1_delim'], "alpha, number, '(', '~', '+', '-', '!'", 156, 160, 161, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 156, 157, False)

        elif char == '>':
            self.modify.match_found(162, char)
            if self.lex.peek_next() == '>':
                self.modify.add_matched_key(key_delims['var1_delim'], "ASCII Character", 162, 164, 164, "symbol", False)
            elif self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate1_delim'], "alpha, number, '(', '~', '+', '-', '!'", 162, 166, 167, "symbol", False)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 162, 163, False)

        elif char == '[':
            self.modify.match_found(168, char)
            self.check.check_symbol(key_delims['bracket_delim'], "alpha, number, ']', ',', '+', '-'", 168, 169, False)

        elif char == ']':
            self.modify.match_found(170, char)
            if self.lex.peek_next() == '.':
                self.check.check_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '.'", 170, 171, False)
            else:
                self.check.check_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '.'", 170, 171, True)

        elif char == '{':
            self.modify.match_found(172, char)
            self.check.check_symbol(key_delims['brace_delim'], "alpha, number, ';', '(', "'", '"', '{', '}', '+', '-'", 172, 173, False)

        elif char == '}':
            self.modify.match_found(174, char)
            self.check.check_symbol(key_delims['brace1_delim'], "alpha, number, '(', '}', '+', '-', None, ';', ','", 174, 175, False)

        elif char == '(':
            self.modify.match_found(176, char)
            self.check.check_symbol(key_delims['paren_delim'], "alpha, number, ';', '!', '#', '\'', '\"', '(', ')', '+', '-', '.'", 176, 177, False)

        elif char == ')':
            self.modify.match_found(178, char)
            self.check.check_symbol(key_delims['paren1_delim'], "'+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', '{', ')', ';'", 178, 179, False)

        elif char == ',':
            self.modify.match_found(180, char)
            self.check.check_symbol(key_delims['comma_delim'], "alpha, number,']', '(', '{', '\"', '\'', '+', '-'", 180, 181, False)

        elif char == ';':
            self.modify.match_found(182, char)
            self.check.check_symbol(key_delims['semicolon_delim'], "alpha, number, '(', '}', '+', '-', None", 182, 183, False)

        elif char == ':':
            self.modify.match_found(184, char)
            self.check.check_symbol(key_delims['colon_delim'], "alpha, number, '(', '+', '-'", 184, 185, False)

        elif char == '#':
            self.modify.match_found(186, char)
            self.check.check_symbol(key_delims['interpol_delim'], "\"", 186, 187, False)

        elif char == '.':
            self.lex.key = char
            fraction = ''

            self.lex.skip_whitespace()

            if self.lex.struct and self.lex.peek_next() in alpha:
                self.modify.append_key(self.lex.key)
                self.get_id()
            else:
                while self.lex.peek_next() not in whitespace and (self.lex.peek_next() not in key_delims['num_delim'] or self.lex.peek_next() not in key_delims['iden_delim']):
                    fraction += self.lex.peek_next()
                    self.lex.advance()
                if fraction.isdigit() and not self.lex.struct:
                    self.lex.key += fraction
                    self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)
                else:
                    if fraction == '':
                        self.lex.error_message(f"Unexpected None after .", "identifier", True)
                    elif self.lex.struct:
                        self.lex.error_message(f"Invalid identifier: {fraction}", "", False)
                    else:
                        self.lex.key += fraction
                        self.lex.error_message(f"Invalid: {self.lex.key}", "", False)
                    
        elif char == '_':
            self.lex.key = char
            self.modify.get_key('')
            self.lex.error_message(f"Invalid identifier: {self.lex.key}", "", False)
        
        else:
            self.lex.key = char
            self.modify.get_key('')
            self.lex.error_message(f"Invalid: {self.lex.key}", "", False)


class Checkers:
    def __init__(self, lex):
        self.lex = lex
        self.modify = StateAndKeyManipulation(lex)

    def check_num(self, s1, s2, s3):
        self.modify.add_key(s1, s2)
        self.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", s2, s3, "num", False)

    def check_dec(self, s1, s2):
        self.modify.add_key(s1, s2)
        if self.lex.peek_next() in whitespace:
            self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)
        else:
            self.lex.stateNum = s2
            if self.lex.peek_next() in alphanumeric:
                GetLitAndIden(self.lex).get_dec()
                self.lex.isDec = False
            else:
                self.modify.get_key(key_delims['num_delim'])
                self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)

    def check_id(self, s1, s2, s3):
        self.modify.add_key(s1, s2)
        if not self.lex.invalid:
            self.check_if_match(key_delims['iden_delim'], "operator, ';', '&', '>', '(', ')', '[', ']', '{', '}', '.', ','", s2, s3, "iden", False)            

    def check_symbol(self, delim, expected, stateNum1, stateNum2, requiredSpace):
        if self.lex.peek_next() in whitespace or self.lex.peek_next() in delim:
            self.lex.matched = True
            self.modify.append_state("end", stateNum1, stateNum2)
        self.check_delim(delim, expected, requiredSpace)

    def check_delim(self, delim, expected, requiredSpace):
        word = ''
        esc = ''
        invalid = ''

        if not requiredSpace:
            self.lex.skip_whitespace()

        if self.lex.peek_next() == '/':
            while True:
                self.lex.advance()
                if self.lex.peek_next() == '/': 
                    self.lex.advance() 
                    self.lex.skip_single_comment()
                    self.lex.skip_whitespace()
                    if self.lex.peek_next() == '/':
                        continue
                    else:
                        break
                else:
                    self.lex.pos -= 1
                    break

        if self.lex.peek_next() == '/':
            self.lex.advance()
            if self.lex.peek_next() == '*': 
                self.lex.advance() 
                self.lex.skip_multi_comment()
            else:
                self.lex.pos -= 1

        if not requiredSpace:
            self.lex.skip_whitespace()

        if self.lex.peek_next() not in delim:
            if self.lex.isIden and self.lex.peek_next() in alpha:
                self.modify.append_key('id')
                self.lex.key = ''
                GetLitAndIden(self.lex).get_keyword(self.lex.advance())
                return

            if self.lex.peek_next() in alpha and self.lex.key not in ['bln', 'chr', 'dec', 'int', 'str', 'var']:
                while self.lex.peek_next() in identifier:
                    word += self.lex.advance()
                if word not in keywords:
                    self.lex.error_message(f"Unexpected id after {self.lex.key}", expected, True)
                else:
                    self.lex.error_message(f"Unexpected {word} after {self.lex.key}", expected, True)
            elif self.lex.peek_next() in alpha and self.lex.key in ['bln', 'chr', 'dec', 'int', 'str', 'var']:
                self.modify.append_key(self.lex.key)
            else:
                self.lex.error_message(f"Unexpected {self.lex.peek_next()} after {self.lex.key}", expected, True)
                if self.lex.peek_next() == '\\':
                    ctr = 1
                    while ctr <=2:
                        esc += self.lex.advance()
                        ctr += 1
                    self.lex.error_message(f"Invalid escape sequence: {esc}", "", False)
                    return
                if self.lex.peek_next() == '~':
                    while self.lex.peek_next() not in whitespace and self.lex.peek_next() not in key_delims['num_delim']:
                        invalid += self.lex.advance()
                    self.lex.error_message(f"Invalid: {invalid}", "", False)
                    return
                self.lex.advance()
                
        else:
            if self.lex.isIden or self.lex.key == ']':
                if self.lex.peek_next() == '.': self.lex.struct = True

            if self.lex.isIden: self.modify.append_key('id')
            elif self.lex.isChar: self.modify.append_key('chr_lit')
            elif self.lex.isString: self.modify.append_key('str_lit')
            elif self.lex.isInt: self.modify.append_key('int_lit')
            elif self.lex.isDec: self.modify.append_key('dec_lit')
            else: self.modify.append_key(self.lex.key)

    def check_if_match(self, delim, expected, stateNum1, stateNum2, reserved, requiredSpace):
        addZero = False
        if reserved in ["iden", "word"]:
            if self.lex.peek_next() not in whitespace and self.lex.peek_next() not in delim:
                self.lex.matched = False
                return
        elif reserved == "num":
            if self.lex.peek_next() not in whitespace:
                if self.lex.peek_next() in alpha:
                    self.modify.get_key(key_delims["num_delim"])
                    self.lex.error_message(f"Invalid identifier: {self.lex.key}", "", False)
                    self.lex.matched = True
                    return
                elif self.lex.peek_next() in digit or self.lex.peek_next() == '.':
                    self.lex.matched = False
                    return

        self.lex.matched = True
        state.append(f"end : {stateNum1}-{stateNum2}")

        if reserved == "num" and not self.lex.key == '0' and '.' in self.lex.key:
            literal = self.lex.key.split('.')
            if all(char == '0' for char in literal[1]):        
                addZero = True
            self.lex.key = self.lex.key.rstrip('0')

        if addZero:
            self.lex.key += '0'

        self.check_delim(delim, expected, requiredSpace)


class StateAndKeyManipulation:
    def __init__(self, lex):
        self.lex = lex

    def append_state(self, stateChar, stateNum1, stateNum2):
        state.append(f"{stateChar} : {stateNum1}-{stateNum2}")
    
    def append_key(self, lit):
        lexeme.append(self.lex.key) 
        token.append(lit)

    def add_key(self, stateNum1, stateNum2):
        state.append(f"{self.lex.peek_next()} : {stateNum1}-{stateNum2}")
        self.lex.key += self.lex.advance()

    def add_matched_key(self, delim, expected, s1, s2, s3, reserved, requiredSpace):
        self.add_key(s1, s2)
        if reserved == "word" and self.lex.peek_next() not in delim and self.lex.peek_next() not in identifier:
            self.lex.matched = False
            self.lex.invalid = True
            return
        
        self.lex.matched = True
        Checkers(self.lex).check_if_match(delim, expected, s2, s3, reserved, requiredSpace)

    def get_key(self, delim):
        while self.lex.peek_next() not in whitespace and self.lex.peek_next() not in delim:
            self.lex.key += self.lex.advance()

    def match_found(self, state, char):
        self.lex.key = char
        self.lex.matched = False
        self.append_state(char, 0, state)
