from definitions import *
from lexical_func import *

def lexer(code, console, table):
    
    lex = Lexical(code, console)
    get = GetLitAndIden(lex)

    while (char := lex.advance()) is not None:
        if char == '/' and lex.peek_next() == '/': 
            lex.advance() 
            lex.skip_single_comment()
        elif char == '/' and lex.peek_next() == '*': 
            lex.advance(), 
            lex.skip_multi_comment()
        elif char == '"': 
            get.get_string()
        elif char == "'": 
            get.get_character()       
        elif char.isdigit() or char == '~': 
            get.get_num(char)
        elif char in alpha: 
            get.get_keyword(char)
        elif char in punc_symbols: 
            get.get_symbol(char)
        elif char in whitespace:
            pass
        else:
            lex.error_message(f"Invalid character: {char}", "", False)
    if errorflag[0] == False:
        console.tag_config("accepted", foreground="#00FFFF", font=("Arial", 12, "bold"))
        console.insert(tk.END,"Input accepted: ", "accepted")
        console.insert(tk.END,"Token recognized.\n")
    for i in range(len(lexeme)):
        table.insert("", "end", values=(lexeme[i], token[i])) 
    #print(state)
