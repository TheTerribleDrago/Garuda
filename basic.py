import unicodedata
import sys

################################
# UNICODE HELPERS
################################

def is_identifier_char(ch):
    if ch is None:
        return False
    return ch.isidentifier() or unicodedata.category(ch).startswith("M")

def normalize_name(name):
    return unicodedata.normalize("NFC", name)

################################
# TOKENS
################################

TT_INT="INT"; TT_FLOAT="FLOAT"; TT_STRING="STRING"
TT_IDENTIFIER="IDENTIFIER"; TT_KEYWORD="KEYWORD"
TT_PLUS="PLUS"; TT_MINUS="MINUS"; TT_MUL="MUL"
TT_DIV="DIV"; TT_MOD="MOD"
TT_EQ="EQ"; TT_NE="NE"; TT_LT="LT"; TT_GT="GT"
TT_LTE="LTE"; TT_GTE="GTE"
TT_ASSIGN="ASSIGN"
TT_LPAREN="LPAREN"; TT_RPAREN="RPAREN"
TT_LBRACKET="LBRACKET"; TT_RBRACKET="RBRACKET"
TT_COMMA="COMMA"; TT_SEMI="SEMI"
TT_EOF="EOF"

################################
# KEYWORDS (SANSKRIT)
################################

KEYWORDS = {
    "चर","यदि","तदा","अन्यथा",
    "पर्यंतम्","प्रति",
    "प्रत्याययतु","प्रत्यावर्तयतु",
    "लिखतु","पठतु",
    "प्रारभ्य","समाप्य",
    "विस्मर्यताम्",
    "सत्यम्","असत्यम्","शून्यम्","न"
}

################################
# TOKEN
################################

class Token:
    def __init__(self,t,v=None):
        self.type=t; self.value=v
    def __repr__(self):
        return f"{self.type}:{self.value}" if self.value is not None else self.type

DIGITS="0123456789०१२३४५६७८९"
DEV_MAP={'०':'0','१':'1','२':'2','३':'3','४':'4',
         '५':'5','६':'6','७':'7','८':'8','९':'9'}

################################
# LEXER
################################

class Lexer:
    def __init__(self,text):
        self.text=text; self.pos=-1; self.cur=None
        self.advance()

    def advance(self):
        self.pos+=1
        self.cur=self.text[self.pos] if self.pos<len(self.text) else None

    def make_tokens(self):
        tokens=[]
        while self.cur:
            if self.cur in " \t\n":
                self.advance()
            elif self.cur in DIGITS:
                tokens.append(self.make_number())
            elif self.cur in "\"'":
                tokens.append(self.make_string())
            elif is_identifier_char(self.cur):
                tokens.append(self.make_identifier())
            elif self.cur=="+": tokens.append(Token(TT_PLUS)); self.advance()
            elif self.cur=="-": tokens.append(Token(TT_MINUS)); self.advance()
            elif self.cur=="*": tokens.append(Token(TT_MUL)); self.advance()
            elif self.cur=="/": tokens.append(Token(TT_DIV)); self.advance()
            elif self.cur=="%": tokens.append(Token(TT_MOD)); self.advance()
            elif self.cur=="=":
                self.advance()
                tokens.append(Token(TT_EQ if self.cur=="=" else TT_ASSIGN))
                if tokens[-1].type==TT_EQ: self.advance()
            elif self.cur=="<": tokens.append(Token(TT_LT)); self.advance()
            elif self.cur==">": tokens.append(Token(TT_GT)); self.advance()
            elif self.cur=="(": tokens.append(Token(TT_LPAREN)); self.advance()
            elif self.cur==")": tokens.append(Token(TT_RPAREN)); self.advance()
            elif self.cur=="[": tokens.append(Token(TT_LBRACKET)); self.advance()
            elif self.cur=="]": tokens.append(Token(TT_RBRACKET)); self.advance()
            elif self.cur==",": tokens.append(Token(TT_COMMA)); self.advance()
            elif self.cur==";": tokens.append(Token(TT_SEMI)); self.advance()
            else:
                raise Exception(f"अवैध वर्ण: {self.cur}")
        tokens.append(Token(TT_EOF))
        return tokens

    def make_number(self):
        s=""
        while self.cur and (self.cur in DIGITS or self.cur=="."):
            s+=DEV_MAP.get(self.cur,self.cur)
            self.advance()
        return Token(TT_FLOAT,float(s)) if "." in s else Token(TT_INT,int(s))

    def make_string(self):
        q=self.cur; self.advance(); s=""
        while self.cur and self.cur!=q:
            s+=self.cur; self.advance()
        if not self.cur:
            raise Exception("अपूर्ण स्ट्रिंग")
        self.advance()
        return Token(TT_STRING,s)

    def make_identifier(self):
        s=""
        while self.cur and is_identifier_char(self.cur):
            s+=self.cur; self.advance()
        s=normalize_name(s)
        return Token(TT_KEYWORD,s) if s in KEYWORDS else Token(TT_IDENTIFIER,s)

################################
# AST NODES
################################

class NumberNode: 
    def __init__(self,t): self.t=t
class StringNode:
    def __init__(self,t): self.t=t
class VarAccessNode:
    def __init__(self,n): self.n=n
class VarAssignNode:
    def __init__(self,n,v): self.n=n; self.v=v
class BinOpNode:
    def __init__(self,l,o,r): self.l=l; self.o=o; self.r=r
class UnaryOpNode:
    def __init__(self,o,n): self.o=o; self.n=n
class IfNode:
    def __init__(self,c,b,e=None): self.c=c; self.b=b; self.e=e
class WhileNode:
    def __init__(self,c,b): self.c=c; self.b=b
class ForNode:
    def __init__(self,i,c,s,b): self.i=i; self.c=c; self.s=s; self.b=b
class BlockNode:
    def __init__(self,s): self.s=s
class FuncDefNode:
    def __init__(self,n,a,b): self.n=n; self.a=a; self.b=b
class CallNode:
    def __init__(self,n,a): self.n=n; self.a=a
class ReturnNode:
    def __init__(self,e): self.e=e
class BuiltInNode:
    def __init__(self,n,a): self.n=n; self.a=a

################################
# RETURN SIGNAL
################################

class ReturnSignal:
    def __init__(self,value):
        self.value=value

################################
# PARSER
################################

class Parser:
    def __init__(self,tokens):
        self.tokens=tokens; self.i=-1
        self.advance()

    def advance(self):
        self.i+=1
        self.cur=self.tokens[self.i]

    def parse(self):
        stmts=[]
        while self.cur.type!=TT_EOF:
            stmts.append(self.statement())
            if self.cur.type==TT_SEMI:
                self.advance()
        return BlockNode(stmts)

    def statement(self):
        if self.cur.type==TT_KEYWORD and self.cur.value=="प्रारभ्य":
            return self.block()

        if self.cur.type==TT_KEYWORD and self.cur.value=="चर":
            self.advance()
            name=self.cur; self.advance()
            self.advance()
            return VarAssignNode(name,self.expr())

        if self.cur.type==TT_KEYWORD and self.cur.value=="यदि":
            self.advance()
            cond=self.expr()
            self.advance()
            body=self.statement()
            else_body=None
            if self.cur.type==TT_KEYWORD and self.cur.value=="अन्यथा":
                self.advance()
                else_body=self.statement()
            return IfNode(cond,body,else_body)

        if self.cur.type==TT_KEYWORD and self.cur.value=="पर्यंतम्":
            self.advance()
            cond=self.expr()
            self.advance()
            body=self.statement()
            return WhileNode(cond,body)

        if self.cur.type==TT_KEYWORD and self.cur.value=="प्रत्याययतु":
            self.advance()
            name=self.cur; self.advance()
            self.advance()
            args=[]
            if self.cur.type!=TT_RPAREN:
                args.append(self.cur); self.advance()
                while self.cur.type==TT_COMMA:
                    self.advance()
                    args.append(self.cur); self.advance()
            self.advance()
            self.advance()
            body=self.statement()
            return FuncDefNode(name,args,body)

        if self.cur.type==TT_KEYWORD and self.cur.value=="प्रत्यावर्तयतु":
            self.advance()
            return ReturnNode(self.expr())

        if self.cur.type==TT_KEYWORD and self.cur.value=="लिखतु":
            return self.builtin_call()

        return self.expr()

    def block(self):
        self.advance()
        stmts=[]
        while not (self.cur.type==TT_KEYWORD and self.cur.value=="समाप्य"):
            stmts.append(self.statement())
            if self.cur.type==TT_SEMI:
                self.advance()
        self.advance()
        return BlockNode(stmts)

    def builtin_call(self):
        self.advance()
        self.advance()
        args=[]
        if self.cur.type!=TT_RPAREN:
            args.append(self.expr())
            while self.cur.type==TT_COMMA:
                self.advance()
                args.append(self.expr())
        self.advance()
        return BuiltInNode("लिखतु",args)

    def expr(self):
        left=self.term()
        while self.cur.type in (TT_PLUS,TT_MINUS):
            op=self.cur; self.advance()
            left=BinOpNode(left,op,self.term())
        return left

    def term(self):
        left=self.factor()
        while self.cur.type in (TT_MUL,TT_DIV,TT_MOD):
            op=self.cur; self.advance()
            left=BinOpNode(left,op,self.factor())
        return left

    def factor(self):
        tok=self.cur
        if tok.type==TT_INT:
            self.advance(); return NumberNode(tok)
        if tok.type==TT_STRING:
            self.advance(); return StringNode(tok)
        if tok.type==TT_IDENTIFIER:
            self.advance()
            if self.cur.type==TT_LPAREN:
                return self.call(tok)
            return VarAccessNode(tok)
        if tok.type==TT_LPAREN:
            self.advance()
            expr=self.expr()
            self.advance()
            return expr
        raise Exception("अमान्य अभिव्यक्ति")

    def call(self,name):
        self.advance()
        args=[]
        if self.cur.type!=TT_RPAREN:
            args.append(self.expr())
            while self.cur.type==TT_COMMA:
                self.advance()
                args.append(self.expr())
        self.advance()
        return CallNode(VarAccessNode(name),args)

################################
# RUNTIME VALUES
################################

class Number:
    def __init__(self,v): self.v=v
    def __repr__(self): return str(self.v)

class String:
    def __init__(self,v): self.v=v
    def __repr__(self): return self.v

class Function:
    def __init__(self,args,body,interpreter):
        self.args=args; self.body=body; self.interpreter=interpreter

    def execute(self,values):
        old=self.interpreter.sym.copy()
        for i,a in enumerate(self.args):
            self.interpreter.sym[normalize_name(a.value)] = values[i]
        result=self.interpreter.visit(self.body)
        self.interpreter.sym=old
        if isinstance(result,ReturnSignal):
            return result.value
        return None

################################
# BUILT-IN FUNCTIONS
################################

class BuiltInFunction:
    def execute(self,args):
        print(" ".join(str(a) for a in args))
        return None

################################
# INTERPRETER
################################

class Interpreter:
    def __init__(self):
        self.sym={"लिखतु":BuiltInFunction()}

    def visit(self,node):
        if node is None: return None
        method=getattr(self,f"v_{type(node).__name__}")
        return method(node)

    def v_NumberNode(self,n): return Number(n.t.value)
    def v_StringNode(self,n): return String(n.t.value)
    def v_VarAccessNode(self,n): return self.sym[n.n.value]
    def v_VarAssignNode(self,n):
        v=self.visit(n.v)
        self.sym[n.n.value]=v
        return v
    def v_BinOpNode(self,n):
        l=self.visit(n.l).v; r=self.visit(n.r).v
        if n.o.type==TT_PLUS: return Number(l+r)
        if n.o.type==TT_MINUS: return Number(l-r)
        if n.o.type==TT_MUL: return Number(l*r)
        if n.o.type==TT_DIV: return Number(l//r)
    def v_BlockNode(self,n):
        for s in n.s:
            r=self.visit(s)
            if isinstance(r,ReturnSignal):
                return r
        return None
    def v_ReturnNode(self,n):
        return ReturnSignal(self.visit(n.e))
    def v_IfNode(self,n):
        if self.visit(n.c).v!=0:
            return self.visit(n.b)
        if n.e: return self.visit(n.e)
        return None
    def v_WhileNode(self,n):
        while self.visit(n.c).v!=0:
            r=self.visit(n.b)
            if isinstance(r,ReturnSignal):
                return r
        return None
    def v_FuncDefNode(self,n):
        self.sym[n.n.value]=Function(n.a,n.b,self)
        return None
    def v_CallNode(self,n):
        fn=self.visit(n.n)
        args=[self.visit(a) for a in n.a]
        if isinstance(fn,BuiltInFunction):
            return fn.execute(args)
        return fn.execute(args)
    def v_BuiltInNode(self,n):
        args=[self.visit(a) for a in n.a]
        return self.sym[n.n].execute(args)

################################
# RUN
################################

def run(code):
    lexer=Lexer(code)
    tokens=lexer.make_tokens()
    tree=Parser(tokens).parse()
    Interpreter().visit(tree)

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: python3 basic.py file.garuda")
    else:
        with open(sys.argv[1],encoding="utf-8") as f:
            run(f.read())
