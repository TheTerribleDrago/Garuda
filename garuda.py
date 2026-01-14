#TOKENS
TT_INT        = "INT"
TT_FLOAT      = "FLOAT"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD    = "KEYWORD"

TT_PLUS   = "PLUS"
TT_MINUS  = "MINUS"
TT_MUL    = "MUL"
TT_DIV    = "DIV"

TT_ASSIGN = "ASSIGN"
TT_EQ     = "EQ"
TT_NE     = "NE"
TT_LT     = "LT"
TT_GT     = "GT"
TT_LTE    = "LTE"
TT_GTE    = "GTE"

TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LBRACE = "LBRACE"
TT_RBRACE = "RBRACE"
TT_COMMA  = "COMMA"

TT_NEWLINE = "NEWLINE"
TT_EOF     = "EOF"

#KEYWORDS
KEYWORDS = {
    "var", #variable
    "yadi", #if
    "ut", #else
    "yavad" ,#while
    "mudranam", #print
    "satya", #true
    "asatya", #false
    "nahi", #not
    "va", #or
    "tatha" #and
}
class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result

class IllegalCharacterError(Error):
    def __init__(self, details):
        super().__init__('Illegal character error', details)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_;
        self.value = value
    
    def __repr__(self):
        if self.value:return f'{self.type}:{self.value}'
        return f'{self.type}'

DIGITS = '1234567890'  
#LEXER
class Lexer:
    def __init__(self,text):
        self.text = text
        self.pos=-1
        self.current_char = None
        self.advance()
    def advance(self):
        self.pos+=1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char is not None:
             if self.current_char in " \t":
                self.advance()

             elif self.current_char == "\n":
                tokens.append(Token(TT_NEWLINE))
                self.advance()

             elif self.current_char in DIGITS:
                tokens.append(self.make_number())

             elif self.current_char.isalpha() or self.current_char == "_":
                tokens.append(self.make_identifier())

             elif self.current_char == "+":
                tokens.append(Token(TT_PLUS))
                self.advance()

             elif self.current_char == "-":
                tokens.append(Token(TT_MINUS))
                self.advance()

             elif self.current_char == "*":
                tokens.append(Token(TT_MUL))
                self.advance()

             elif self.current_char == "/":
                tokens.append(Token(TT_DIV))
                self.advance()

             elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN))
                self.advance()

             elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN))
                self.advance()

             elif self.current_char == "{":
                tokens.append(Token(TT_LBRACE))
                self.advance()

             elif self.current_char == "}":
                tokens.append(Token(TT_RBRACE))
                self.advance()

             elif self.current_char == ",":
                tokens.append(Token(TT_COMMA))
                self.advance()

             elif self.current_char == "=":
                tokens.append(self.make_equals())

             elif self.current_char == "!":
                tokens.append(self.make_not_equals())

             elif self.current_char == "<":
                tokens.append(self.make_less_than())

             elif self.current_char == ">":
                tokens.append(self.make_greater_than())

             else:
                char = self.current_char
                self.advance()
                return [], IllegalCharacterError(" ' " + char + " ' ")
        tokens.append(Token(TT_EOF))
        return tokens, None

    def make_number(self):
                num_str = ''
                dot_count = 0
                
                while self.current_char is not None and self.current_char in DIGITS + '.':
                    if self.current_char == '.':
                        if dot_count==1:
                            break
                        dot_count+=1
                        num_str+='.'
                    else:
                        num_str +=self.current_char
                    self.advance()
                if dot_count==0:
                    return Token(TT_INT, int(num_str))
                else:
                    return Token(TT_FLOAT, float(num_str))
                
        #RUN

def run(text):
    lexer  = Lexer(text)
    tokens, error = lexer.make_tokens()

    return tokens, error