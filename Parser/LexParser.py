import ply.lex as lexer

class LexParser:
    def __init__(self):
        self.lexer = lexer.lex(module=self)

    reserved = {
        r'true': 'TRUE',
        r'false': 'FALSE',
        r'boolean': 'BOOLEAN',
        r'int': 'INT',
        r'cboolean': 'CBOOLEAN',
        r'cint': 'CINT',
        r'map': 'MAP',
        r'inc': 'INC',
        r'dec': 'DEC',
        r'or': 'OR',
        r'not': 'NOT',
        r'gt': 'GT',
        r'lt': 'LT',
        r'while': 'WHILE',
        r'do': 'DO',
        r'if': 'IF',
        r'else': 'ELSE',
        r'step': 'STEP',
        r'right': 'RIGHT',
        r'left': 'LEFT',
        r'back': 'BACK',
        r'look': 'LOOK',
        r'proc': 'PROC',
        r'bar': 'BAR',
        r'emp': 'EMP',
        r'set': 'SET',
        r'clr': 'CLR',
    }

    special = [
        'NUM', 'VARIABLE',
        'OPBR', 'CLBR', 'OPSQBR', 'CLSQBR',
        'ASSIGN', 'EQUAL',
        'EOS'
    ]
    tokens = special + list(reserved.values())
    t_ignore = ' \t'

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    def t_NUM(self, t):
        r'\-?\d+'
        t.value = int(t.value)
        return t

    def t_VARIABLE(self, t):
        r'[a-zA-Z][a-zA-Z\d\_]*'
        str = t.value.lower()
        t.value = str
        t.type = self.reserved.get(str, 'VARIABLE')
        return t

    def t_OPBR(self, t):
        r'\('
        return t

    def t_CLBR(self, t):
        r'\)'
        return t

    def t_OPSQBR(self, t):
        r'\['
        return t

    def t_CLSQBR(self, t):
        r'\]'
        return t

    def t_ASSIGN(self, t):
        r'\:\='
        return t

    def t_EQUAL(self, t):
        r'\='
        return t

    def t_EOS(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_error(self, t):
        print(f"Invalid character {t.value[0]}")
        t.lexer.skip(1)
        t.value = t.value[0]
        return t


if __name__ == '__main__':
    f = open(r"C:\Users\Amr\PycharmProjects\Interpretator\Parser\check2.txt", 'r')
    lex = LexParser()
    data = f.read()
    lex.input(data)
    while True:
        tok = lex.token()
        if not tok:
            break
        print(tok)