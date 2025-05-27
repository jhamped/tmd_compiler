from definitions import *
import tkinter as tk

class Lexical:
    def __init__(self, code, console):
        self.pos = 0
        self.col = 0
        self.line = 1
        self.code = code
        self.console = console

        self.idNum = 0
        self.stateNum = 0
        self.key = ""
        self.isIden = False
        self.isChar = False
        self.isString = False
        self.isInt = False
        self.isDec = False
        self.matched = False
        self.invalid = False
        self.isStringDone = False
        #self.struct = False

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
    def peek_next2(self):
        if self.pos+1 < len(self.code):
            return self.code[self.pos+1]
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
        self.console.insert(tk.END, "Lexical Error: ", "error")
        self.console.insert(tk.END, f"{error}")
        #if expectedError:
        #    self.console.insert(tk.END, f"  Delimiter: {expected}", "expected")
        self.console.insert(tk.END, f"\n       line {self.line}, column {self.col}\n", "ln_col")
        errorflag[0] = True
class GetLitAndIden: 
    def __init__(self, lex):
        self.lex = lex
        self.modify = StateAndKeyManipulation(lex)
        self.check = Checkers(lex)

    def get_string(self):
        self.lex.isDec = False
        self.lex.isString = True
        self.lex.key = '"'
        self.modify.append_state(self.lex.key, 0, 411)
        ctr = 0

        while True:
            if self.lex.peek_next() is None:  
                self.lex.error_message("Invalid: \"", "", False)
                break
            if self.lex.peek_next() == '"': 
                self.modify.add_key(412, 413)
                self.check.check_delim(key_delims['lit_delim'], "';', ',', '&', ')', '}', '!', '=', '|', ':'", True)
                break
            elif self.lex.peek_next() == '\\': 
                esc = self.lex.advance()
                if self.lex.peek_next() in ['\\', '"', 'n', 't']: 
                    esc += self.lex.advance()
                    self.lex.key += esc
                    ctr += 1
                    if ctr == 1:
                        self.modify.append_state(esc, 411, 412)
                    else:
                        self.modify.append_state(esc, 412, 412)
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
                    self.modify.add_key(411, 412)
                else:
                    self.modify.add_key(412, 412)
        self.lex.isString = False

    def get_character(self):
        self.lex.isDec = False
        self.lex.isChar = True
        terminated = False
        self.lex.key = "'"

        self.modify.append_state(self.lex.key, 0, 415)
        if self.lex.peek_next() is not None:
            if self.lex.peek_next() == "'":
                self.modify.add_key(416, 417)
                self.check.check_delim(key_delims['lit_delim'], "';', ',', '&', ')', '}', '!', '=', '|', ':'", False)
            else:
                self.modify.add_key(415, 416)
                if self.lex.peek_next() == "'":
                    self.modify.add_key(416, 417)
                    self.check.check_delim(key_delims['lit_delim'], "';', ',', '&', ')', '}', '!', '=', '|', ':'", False)
                else:
                    self.modify.get_key(key_delims['lit_delim'])
                    self.lex.error_message("Character literals must only contain one character", "", False)
        if self.lex.key.count("'") == 2:
            terminated = True
        if not terminated:
            self.lex.error_message("Delimiter: '", "", False)

        self.lex.isChar = False

    def get_num(self, char):
        print("Get Num")
        self.lex.isDec = False
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
            self.modify.append_state(curr, 240, 241)
            self.lex.key += curr
            self.check.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", 241, 242, "num", True)
            if self.lex.peek_next() == '.' and self.lex.isDec == False:
                self.check.check_dec(241, 261)
            elif self.lex.peek_next() in digit:
                self.check.check_num(241, 243, 244) 
                if self.lex.peek_next() == '.' and self.lex.isDec == False:
                    self.check.check_dec(243, 276)   
                elif self.lex.peek_next() in digit:
                    self.check.check_num(243, 245, 246)
                    if self.lex.peek_next() == '.' and self.lex.isDec == False:
                        self.check.check_dec(245, 291)
                    elif self.lex.peek_next() in digit:
                        self.check.check_num(245, 247, 248)
                        if self.lex.peek_next() == '.' and self.lex.isDec == False:
                            self.check.check_dec(247, 306)
                        elif self.lex.peek_next() in digit:
                            self.check.check_num(247, 249, 250)
                            if self.lex.peek_next() == '.' and self.lex.isDec == False:
                                self.check.check_dec(249, 321)
                            elif self.lex.peek_next() in digit:
                                self.check.check_num(249, 251, 252)
                                if self.lex.peek_next() == '.' and self.lex.isDec == False:
                                    self.check.check_dec(251, 336)
                                elif self.lex.peek_next() in digit:
                                    self.check.check_num(251, 253, 254)
                                    if self.lex.peek_next() == '.' and self.lex.isDec == False:
                                        self.check.check_dec(253, 351)
                                    elif self.lex.peek_next() in digit:
                                        self.check.check_num(253, 255, 256)
                                        if self.lex.peek_next() == '.' and self.lex.isDec == False:
                                            self.check.check_dec(255, 366)
                                        elif self.lex.peek_next() in digit:
                                            self.check.check_num(255, 257, 258)
                                            if self.lex.peek_next() == '.' and self.lex.isDec == False:
                                                self.check.check_dec(257, 381)
                                            elif self.lex.peek_next() in digit:
                                                self.check.check_num(257, 259, 260)
                                                if self.lex.peek_next() == '.' and self.lex.isDec == False:
                                                    self.check.check_dec(259, 396)

        self.lex.isInt = False
        if not self.lex.matched:
            if self.lex.peek_next() not in whitespace:
                if len(self.lex.key) < 10:
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
            self.check.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", self.lex.stateNum+1, self.lex.stateNum+2, "num", True)
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
                    if self.lex.peek_next() == None:
                        break
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
        print("GET ID")
        self.lex.isDec = False
        self.lex.isIden = True
        curr = self.lex.advance()
        self.lex.key = curr
        self.modify.append_state(curr, 0, 180)
        self.check.check_if_match(key_delims['iden_delim'], "operator, ';', '&', '>', '(', ')', '[', ']', '{', '}', '.', ','", 180, 181, "iden", True)
        if self.lex.peek_next() in identifier: 
            self.check.check_id(180, 182, 183)
            if self.lex.peek_next() in identifier: 
                self.check.check_id(182, 184, 185)
                if self.lex.peek_next() in identifier: 
                    self.check.check_id(184, 186, 187)
                    if self.lex.peek_next() in identifier: 
                        self.check.check_id(186, 188, 189)
                        if self.lex.peek_next() in identifier: 
                            self.check.check_id(188, 190, 191)
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

        #self.lex.isIden = False
        if self.lex.invalid:
            self.modify.get_key("")
            self.lex.isIden = False
            self.lex.invalid = False
            #self.lex.matched = True #remove this if nagerror
            self.lex.error_message(f"Invalid identifier: {self.lex.key}", "", False)
        else:
            self.lex.isIden = False
        if not self.lex.matched:
            if self.lex.peek_next() not in whitespace:
                self.modify.get_key(key_delims['iden_delim'])
                self.lex.isIden = False
                if len(self.lex.key) > 30:
                    self.lex.error_message(f"Identifier {self.lex.key} exceeds maximum length of 30 characters", "", False)
                else:
                    last_lexem = self.lex.key[-1]
                    current_id = self.lex.key[:-1]
                    self.lex.error_message(f"Invalid Delimiter: {self.lex.key}", "", False)
        else:
            self.lex.isIden = False
    def get_lexeme(self):  
        if self.lex.peek_next() is None:
            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next() }", "", False)
            return
        index = len(self.lex.key)
        del state[-index:]
        self.lex.pos -= index
        self.get_id()

    def get_keyword(self, char):
        self.lex.isDec = False
        self.lex.isIden = False

        if char == 'b':
            self.modify.match_found(1, char)
            if self.lex.peek_next() == 'l':
                self.modify.add_key(1, 2)
                if self.lex.peek_next() == 'n':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 2, 3, 4, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            elif self.lex.peek_next() == 'r':
                self.modify.add_key(1, 5)
                if self.lex.peek_next() == 'k':
                    self.modify.add_matched_key(key_delims['jmp_delim'], "';'", 5, 6, 7, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'c':
            self.modify.match_found(8, char)
            if self.lex.peek_next() == 'h':
                self.modify.add_key(8, 9)
                if self.lex.peek_next() == 'r':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 9, 10, 11, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            elif self.lex.peek_next() == 'o':
                self.modify.add_key(8, 12)
                if self.lex.peek_next() == 'n':
                    self.modify.add_key(12, 13)
                    if self.lex.peek_next() == 's':
                        self.modify.add_key(13, 14)
                        if self.lex.peek_next() == 't':
                            self.modify.add_matched_key(whitespace, "whitespace", 14, 15, 16, "word", True)
                            if not self.lex.matched and self.lex.peek_next() not in identifier:
                                 
                                self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                                return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'd':
            self.modify.match_found(17, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(17, 18)
                if self.lex.peek_next() == 'c':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 18, 19, 20, "word", True)
                elif self.lex.peek_next() == 'f':
                    self.modify.add_matched_key(key_delims['def_delim'], "':'", 18, 21, 22, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            elif self.lex.peek_next() == 'i':
                self.modify.add_key(17, 23)
                if self.lex.peek_next() == 's':
                    self.modify.add_key(23, 24)
                    if self.lex.peek_next() == 'p':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 24, 25, 26, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
            elif self.lex.peek_next() == 'o':
                self.modify.add_matched_key(key_delims['block_delim'], "'{'", 17, 27, 28, "word", True)
                if not self.lex.matched and self.lex.peek_next() not in identifier:
                     
                    self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                    return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'e':
            self.modify.match_found(29, char)
            if self.lex.peek_next() == 'l':
                self.modify.add_key(29, 30)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(30, 31)
                    if self.lex.peek_next() == 'f':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 31, 32, 33, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
                elif self.lex.peek_next() == 's':
                    self.modify.add_key(30, 34)
                    if self.lex.peek_next() == 'e':
                        self.modify.add_matched_key(key_delims['block_delim'], "'{'", 34, 35, 36, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
            elif self.lex.peek_next() == 'x':
                self.modify.add_key(29, 37)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(37, 38)
                    if self.lex.peek_next() == 't':
                        self.modify.add_matched_key(key_delims['jmp_delim'], "';'", 38, 39, 40, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
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
                            self.modify.add_matched_key(key_delims['val_delim'], "';', ',', ')', '}', '!', '&', '='", 44, 45, 46, "word", True)
                            if not self.lex.matched and self.lex.peek_next() not in identifier:
                                 
                                self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                                return
            
            elif self.lex.peek_next() == 'o':
                self.modify.add_key(41, 47)
                if self.lex.peek_next() == 'r':
                    self.modify.add_key(47, 48)
                    if self.lex.peek_next() != 'e':
                        self.lexmatched = True
                        self.check.check_if_match(key_delims['state_delim'], "'('", 48, 49, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
                    elif self.lex.peek_next() == 'e':
                        self.modify.add_key(48, 50)
                        if self.lex.peek_next() == 'a':
                            self.modify.add_key(50, 51)
                            if self.lex.peek_next() == 'c':
                                self.modify.add_key(51, 52)
                                if self.lex.peek_next() == 'h':
                                    self.modify.add_matched_key(key_delims['state_delim'], "'('", 52, 53, 54, "word", True)  
                                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                                         
                                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                                        return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'i':
            self.modify.match_found(55, char)
            if self.lex.peek_next() == 'f':
                self.modify.add_matched_key(key_delims['state_delim'], "'('", 55, 56, 57, "word", True)
                if not self.lex.matched and self.lex.peek_next() not in identifier:
                     
                    self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                    return
            elif self.lex.peek_next() == 'n':
                self.modify.add_key(55, 58)
                if self.lex.peek_next() != 's' and self.lex.peek_next() != 't':
                    self.lex.matched = True
                    self.check.check_if_match(whitespace, "alpha", 58, 59, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
                elif self.lex.peek_next() == 's':
                    self.modify.add_key(58, 60)
                    if self.lex.peek_next() == 'p':
                        self.modify.add_matched_key(key_delims['state_delim'], "'('", 60, 61, 62, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
                elif self.lex.peek_next() == 't':
                    self.modify.add_matched_key(key_delims['data_delim'], "whitespace, '[', '('", 58, 63, 64, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'k':
            self.modify.match_found(65, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(65, 66)
                if self.lex.peek_next() == 'y':
                    self.modify.add_matched_key(whitespace, "whitespace", 66, 67, 68, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'm':
            self.modify.match_found(69, char)
            if self.lex.peek_next() == 'a':
                self.modify.add_key(69, 70)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(70, 71)
                    if self.lex.peek_next() == 'n':
                        self.modify.add_matched_key(key_delims['block_delim'], "'{'", 71, 72, 73, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'n':
            self.modify.match_found(74, char)
            if self.lex.peek_next() == 'o':
                self.modify.add_key(74, 75)
                if self.lex.peek_next() == 'n':
                    self.modify.add_key(75, 76)
                    if self.lex.peek_next() == 'e':
                        self.modify.add_matched_key(key_delims['val_delim'], "';', ',', ')', '}', '!', '&', '='", 76, 77, 78, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'r':
            self.modify.match_found(79, char)
            if self.lex.peek_next() == 'e':
                self.modify.add_key(79, 80)
                if self.lex.peek_next() == 't':
                    self.modify.add_matched_key(whitespace, "whitespace", 80, 81, 82, "word", True )
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            elif self.lex.peek_next() == 's':
                self.modify.add_key(79, 83)
                if self.lex.peek_next() == 'm':
                    self.modify.add_matched_key(key_delims['jmp_delim'], "';'", 83, 84, 85, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
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
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
            elif self.lex.peek_next() == 't':
                self.modify.add_key(86, 91)
                if self.lex.peek_next() == 'r':
                    self.modify.add_key(91, 92)
                    self.check.check_if_match(key_delims['data_delim'], "whitespace, '[', '('", 92, 93, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
                    #else:
                    #    self.modify.add_matched_key(whitespace, "whitespace", 92, 94, 95, "word", True)
            elif self.lex.peek_next() == 'w':
                self.modify.add_key(86, 94)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(95, 96)
                    if self.lex.peek_next() == 't':
                        self.modify.add_key(96, 97)
                        if self.lex.peek_next() == 'c':
                            self.modify.add_key(97, 98)
                            if self.lex.peek_next() == 'h':
                                self.modify.add_matched_key(key_delims['state_delim'], "'('", 97, 98, 99, "word", True)
                                if not self.lex.matched and self.lex.peek_next() not in identifier:
                                     
                                    self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                                    return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 't':
            self.modify.match_found(100, char)
            if self.lex.peek_next() == 'r':
                self.modify.add_key(100, 101)
                if self.lex.peek_next() == 'u':
                    self.modify.add_key(101, 102)
                    if self.lex.peek_next() == 'e':
                        self.modify.add_matched_key(key_delims['val_delim'], "';', ',', ')', '}', '!', '&', '='", 102, 103, 104, "word", True)
                        if not self.lex.matched and self.lex.peek_next() not in identifier:
                             
                            self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                            return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'v':
            self.modify.match_found(105, char)
            if self.lex.peek_next() == 'a':
                self.modify.add_key(105, 106)
                if self.lex.peek_next() == 'r':
                    self.modify.add_matched_key(whitespace, "whitespace", 106, 107, 108, "word", True)
                    if not self.lex.matched and self.lex.peek_next() not in identifier:
                         
                        self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                        return
            if not self.lex.matched:
                self.get_lexeme()

        elif char == 'w':
            self.modify.match_found(109, char)
            if self.lex.peek_next() == 'h':
                self.modify.add_key(110, 111)
                if self.lex.peek_next() == 'i':
                    self.modify.add_key(111, 112)
                    if self.lex.peek_next() == 'l':
                        self.modify.add_key(112, 113)
                        if self.lex.peek_next() == 'e':
                            self.modify.add_matched_key(key_delims['state_delim'], "'('", 112, 113, 114, "word", True)
                            if not self.lex.matched and self.lex.peek_next() not in identifier:
                                 
                                self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next()} after {self.lex.key}", "", False)
                                return
            if not self.lex.matched:
                self.get_lexeme()

        else:
            self.lex.key = char
            self.get_lexeme()

    def get_symbol(self, char):
        print("sybolo")
        self.lex.isDec = False
        if char == '=':
            self.modify.match_found(115, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 115, 117, 118, "symbol", True)
            else:
                self.check.check_symbol(key_delims['asn_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"', '{', '#'", 115, 116, True)

        elif char == '+':
            self.modify.match_found(119, char)
            if self.lex.peek_next() == '+':
                self.modify.add_matched_key(key_delims['unary_delim'], "alpha, number, '(', ')', ';', ',', '~'", 119, 121, 122, "symbol", True)
            elif self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 119, 123, 124, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 119, 120, True)

        elif char == '-':
            self.modify.match_found(125, char)
            if self.lex.peek_next() == '-':
                self.modify.add_matched_key(key_delims['unary_delim'], "alpha, number, '(', ')', ';', ',', '~'", 125, 127, 128, "symbol", True)
            elif self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 125, 129, 130, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 125, 126, True)
                        
        elif char == '*':
            self.modify.match_found(131, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 131, 133, 134, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 131, 132, True)

        elif char == '/':
            self.modify.match_found(135, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 135, 137, 138, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 135, 136, True)

        elif char == '%':
            self.modify.match_found(139, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 139, 141, 142, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 139, 140, True)

        elif char == '&':
            self.modify.match_found(143, char)
            if self.lex.peek_next() == '&':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 143, 145, 146, "symbol", True)
            else:
                self.check.check_symbol(key_delims['concat_delim'], "alpha,'(', '\"', '\'', '#'", 143, 144, True)
                
        elif char == '|':
            self.modify.match_found(147, char)
            if self.lex.peek_next() == '|':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 147, 148, 149, "symbol", True)
            else:
                self.lex.advance()
                self.lex.error_message(f"Invalid Delimiter: {self.lex.peek_next() }", "", False)

        elif char == '!':
            self.modify.match_found(150, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate_delim'], "alpha, number, '(', '~', '/', '.', '+', '-', '!', '\'', '\"'", 150, 152, 153, "symbol", True)
            else:
                self.check.check_symbol(key_delims['not_delim'], "alpha, '(',", 150, 151, True)

        elif char == '<':
            self.modify.match_found(154, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate1_delim'], "alpha, number, '(', '~', '+', '-', '!'", 154, 156, 157, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 154, 155, True)

        elif char == '>':
            self.modify.match_found(158, char)
            if self.lex.peek_next() == '=':
                self.modify.add_matched_key(key_delims['relate1_delim'], "alpha, number, '(', '~', '+', '-', '!'", 158, 160, 161, "symbol", True)
            else:
                self.check.check_symbol(key_delims['op_delim'], "alpha, number, '(', '~', '+', '-'", 158, 159, True)

        elif char == '[':
            self.modify.match_found(162, char)
            self.check.check_symbol(key_delims['bracket_delim'], "alpha, number, ']', ',', '+', '-'", 162, 163, True)

        elif char == ']':
            self.modify.match_found(164, char)
            #if self.lex.peek_next() == '.':
            #    self.lex.struct = True
            self.check.check_symbol(key_delims['bracket1_delim'], "operator, ')', '=', ';', '&', '.'", 164, 165, True)

        elif char == '{':
            self.modify.match_found(166, char)
            self.check.check_symbol(key_delims['brace_delim'], "alpha, number, ';', '(', "'", '"', '{', '}', '+', '-'", 166, 167, True)

        elif char == '}':
            self.modify.match_found(168, char)
            self.check.check_symbol(key_delims['brace1_delim'], "alpha, number, '(', '}', '+', '-', None, ';', ','", 168, 169, True)

        elif char == '(':
            self.modify.match_found(170, char)
            self.check.check_symbol(key_delims['paren_delim'], "alpha, number, ';', '!', '#', '\'', '\"', '(', ')', '+', '-', '.'", 170, 171, True)

        elif char == ')':
            self.modify.match_found(172, char)
            self.check.check_symbol(key_delims['paren1_delim'], "'+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', '{', ')', ';'", 172, 173, True)

        elif char == ',':
            self.modify.match_found(174, char)
            self.check.check_symbol(key_delims['comma_delim'], "alpha, number,']', '(', '{', '\"', '\'', '+', '-'", 174, 175, True)

        elif char == ';':
            self.modify.match_found(176, char)
            self.check.check_symbol(key_delims['semicolon_delim'], "alpha, number, '(', '}', '+', '-', None", 176, 177, True)

        elif char == ':':
            self.modify.match_found(178, char)
            self.check.check_symbol(key_delims['colon_delim'], "alpha, number, '(', '+', '-'", 178, 179, True)
        
        elif char == '.':
            self.lex.key = char
            fraction = ''

            self.lex.skip_whitespace()

            while self.lex.peek_next() not in whitespace and (self.lex.peek_next() not in key_delims['num_delim'] or self.lex.peek_next()) and self.lex.peek_next() != None:
                fraction += self.lex.peek_next()
                self.lex.advance()
            if fraction.isdigit():
                self.lex.key += fraction
                self.lex.error_message(f"Invalid decimal value: {self.lex.key}", "", False)
            else:
                if fraction == '':
                    self.lex.error_message(f"Invalid Delimiter: None after .", "identifier", True)
                #elif self.lex.struct:
                #    self.lex.error_message(f"Invalid identifier: {fraction}", "", False)
                else:
                    self.lex.key += fraction
                    self.lex.error_message(f"Invalid: {self.lex.key}", "", False)
            #self.lex.struct = False
                    
        elif char == '_':
            self.lex.key = char
            self.modify.get_key('')
            self.lex.error_message(f"Invalid identifier: {self.lex.key}", "", False)
        
        else:
            self.lex.key = char
            #self.modify.get_key('')
            self.lex.error_message(f"Invalid: {self.lex.key}", "", False)


class Checkers:
    def __init__(self, lex):
        self.lex = lex
        self.modify = StateAndKeyManipulation(lex)

    def check_num(self, s1, s2, s3):
        self.modify.add_key(s1, s2)
        self.check_if_match(key_delims['num_delim'], "operator, ':', ';', ')', '}', ']', ','", s2, s3, "num", True)

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
        print(f"1 {self.lex.key}")
        self.modify.add_key(s1, s2)
        print(f"2 {self.lex.key}")
        if not self.lex.invalid:
            self.check_if_match(key_delims['iden_delim'], "operator, ';', '&', '>', '(', ')', '[', ']', '{', '}', '.', ','", s2, s3, "iden", True)            

    def check_symbol(self, delim, expected, stateNum1, stateNum2, requiredSpace):
        if self.lex.peek_next() in whitespace or self.lex.peek_next() in delim:
            self.lex.matched = True
            self.modify.append_state("end", stateNum1, stateNum2)
        self.check_delim(delim, expected, requiredSpace)

    def check_delim(self, delim, expected, requiredSpace):
        print("Check_delim")
        esc = ''
        invalid = ''
        word = ''
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
                if self.lex.key in idens:
                    id = idens.index(self.lex.key)
                else:
                    id = self.lex.idNum
                    self.lex.idNum += 1
                    idens.append(self.lex.key)
                self.modify.append_key(f'id{id+1}')
                self.lex.key = ''
                GetLitAndIden(self.lex).get_keyword(self.lex.advance())
                return

            if self.lex.peek_next() in alpha and self.lex.key not in ['bln', 'chr', 'dec', 'int', 'str', 'var']:
                while self.lex.peek_next() in identifier and not self.lex.isString:
                    word += self.lex.advance()
                if word not in keywords:
                    self.lex.error_message(f"Invalid Delimiter: id after {self.lex.key}", expected, True)
                else:
                    self.lex.error_message(f"Invalid Delimiter: {word} after {self.lex.key}", expected, True)
            elif self.lex.peek_next() in alpha and self.lex.key in ['bln', 'chr', 'dec', 'int', 'str', 'var']:
                self.modify.append_key(self.lex.key)
            else:
                self.lex.error_message(f"Invalid Delimiter {self.lex.peek_next()} after {self.lex.key}", expected, True)
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
                #self.lex.advance()
                self.lex.isDec = True
                
        else:
            #if self.lex.isIden or self.lex.key == ']':
            #    if self.lex.peek_next() == '.': self.lex.struct = True

            if self.lex.isIden and self.lex.peek_next() in ['!', '&', '|']:
                curr = self.lex.peek_next()
                if curr == '!' and self.lex.peek_next2() != '=':
                    self.lex.error_message(f"Invalid identifier: {self.lex.key + curr}", "", False)
                    return
                elif curr == '|' and self.lex.peek_next2() != '|':
                    self.lex.error_message(f"Invalid identifier: {self.lex.key + curr}", "", False)
                    return
                self.lex.pos -= 1

            if self.lex.isIden: 
                if self.lex.key in idens:
                    id = idens.index(self.lex.key)
                else:
                    id = self.lex.idNum
                    self.lex.idNum += 1
                    idens.append(self.lex.key)
                self.modify.append_key(f'id{id+1}')
            elif self.lex.isChar: self.modify.append_key('chr_lit')
            elif self.lex.isString: self.modify.append_key('str_lit')
            elif self.lex.isInt: self.modify.append_key('int_lit')
            elif self.lex.isDec: self.modify.append_key('dec_lit')
            else: self.modify.append_key(self.lex.key)

    def check_if_match(self, delim, expected, stateNum1, stateNum2, reserved, requiredSpace):
        addZero = False
        print(f"3 {self.lex.key}")

        if reserved in ["iden", "word"]:
            if self.lex.peek_next() not in whitespace and self.lex.peek_next() not in delim:
                self.lex.matched = False
                return
        elif reserved == "num":
            if self.lex.peek_next() not in whitespace:
                if self.lex.peek_next() in alpha:
                    self.modify.get_key(key_delims["num_delim"])
                    self.lex.error_message(f"Invalid number: {self.lex.key}", "", False)
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
        rows.append(self.lex.line)
        col.append(self.lex.col)

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
        if self.lex.peek_next() is not None:
            while self.lex.peek_next() not in whitespace and self.lex.peek_next() not in delim:
                print(f"4 {self.lex.key}/{self.lex.isIden}/{self.lex.peek_next()}")
                if self.lex.isIden and self.lex.peek_next() not in identifier:
                    self.lex.advance()
                    return
                self.lex.key += self.lex.advance()
                
                if self.lex.peek_next() is None:
                    break
        #if self.lex.isIden and self.lex.peek_next() not in identifier:
        #    self.lex.key += self.lex.advance()
    def match_found(self, state, char):
        self.lex.key = char
        self.lex.matched = False
        self.append_state(char, 0, state)
