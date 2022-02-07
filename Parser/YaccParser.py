import ply.yacc as yacc
from SyntTree.SyntTree import SyntTree
from Parser.LexParser import LexParser

class Parser:
    tokens = LexParser().tokens

    def __init__(self):
        self.lexer = LexParser()
        self.parser = yacc.yacc(module=self)
        self.proc_names = []
        self.var_names = []
        self.errors = []

    def parse(self, data):
        result = self.parser.parse(data, debug=True)
        #print(self.errors)
        #result.print()
        return result, self.errors

    def p_program(self, p):
        """program : sentence_groups"""
        p[0] = SyntTree('Program Start', child=[p[1], SyntTree('Program End')], lineno=p.lineno(1))

    def p_sentence_groups(self, p):
        """sentence_groups : EOS OPBR EOS sentence_group CLBR EOS
                           | OPBR EOS sentence_group CLBR EOS
                           | OPBR EOS sentence_group CLBR
                           | EOS OPBR EOS sentence_group CLBR
                           | EOS sentence
                           | sentence"""
        if len(p) > 5:
            p[0] = p[4]
        elif len(p) > 2:
            p[0] = p[3]
        else:
            p[0] = p[1]

    def p_sentence_group(self, p):
        """sentence_group : sentence_group sentence
                          | sentence"""
        if len(p) == 3:
            p[0] = SyntTree('sentence_group', child=[p[1], p[2]], lineno=p.lineno(1))
        else:
            p[0] = p[1]

    def p_sentence(self, p):
        """sentence : definition EOS
                    | if
                    | while
                    | if_err
                    | while_err
                    | procedure
                    | call_procedure EOS
                    | robot_command EOS
                    | map_setting EOS
                    | error"""
        p[0] = p[1]

    def p_definition(self, p):
        """definition : INT VARIABLE EQUAL math_expr
                      | CINT VARIABLE EQUAL math_expr
                      | BOOLEAN VARIABLE EQUAL logic_expr
                      | CBOOLEAN VARIABLE EQUAL logic_expr
                      | VARIABLE ASSIGN math_expr
                      | VARIABLE ASSIGN logic_expr
                      | MAP VARIABLE"""
        if len(p) == 5:
            p[0] = SyntTree('definition', value=p[1], child=[SyntTree('variable', value=p[2], lineno=p.lineno(2)), p[4]], lineno=p.lineno(1))
        elif len(p) == 4:
            p[0] = SyntTree('assign', child=[SyntTree('variable', value=p[1], lineno=p.lineno(1)), p[3]], lineno=p.lineno(1))
        else:
            p[0] = SyntTree('definition', value=p[1], child=[SyntTree('variable', value=p[2], lineno=p.lineno(2))], lineno=p.lineno(1))

    def p_math_expr(self, p):
        """math_expr : INC math_first math_second
                     | DEC math_first math_second
                     | math_cmd empty
                     | VARIABLE
                     | number empty"""
        if len(p) == 4:
            p[0] = SyntTree('math_expr', value=p[1], child=[p[2], p[3]], lineno=p.lineno(1))
        elif len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = SyntTree('variable', value=p[1], lineno=p.lineno(1))

    def p_number(self, p):
        """number : NUM"""
        p[0] = SyntTree('number', value=p[1], lineno=p.lineno(1))

    def p_bool(self, p):
        """bool : TRUE
                | FALSE"""
        p[0] = SyntTree('bool', value=p[1], lineno=p.lineno(1))

    def p_math_first(self, p):
        """math_first : math_expr
                     | call_procedure"""
        p[0] = p[1]

    def p_math_second(self, p):
        """math_second : math_first
                      | logic_expr"""
        p[0] = p[1]

    def p_logic_expr(self, p):
        """logic_expr : NOT logic_expr
                      | NOT call_procedure
                      | OR or_elem or_elem
                      | GT math_expr math_expr
                      | LT math_expr math_expr
                      | logic_cmd
                      | bool"""
        if len(p) == 3:
            p[0] = SyntTree('logic_expr', value=p[1], child=[p[2]], lineno=p.lineno(1))
        elif len(p) == 4:
            p[0] = SyntTree('logic_expr', value=p[1], child=[p[2], p[3]], lineno=p.lineno(1))
        else:
            p[0] = p[1]

    def p_or_elem(self, p):
        """or_elem : logic_expr
                   | call_procedure"""
        p[0] = p[1]

    def p_procedure(self, p):
        """procedure : proc_name OPSQBR varlist CLSQBR sentence_groups"""
        p[0] = SyntTree('procedure', value=p[1], child=[p[3], p[5]], lineno=p.lineno(1))

    def p_proc_name(self, p):
        """proc_name : PROC VARIABLE"""
        if (not self.proc_names.__contains__(p[2])):
            self.proc_names.append(p[2])
        else:
            #sys.stderr.write("Error procedure with same name already declared")
            self.errors.append(f"Line: {p.lineno(1)} Error: Procedure '{p[1]}' already declared")
        p[0] = p[2]

    def p_call_procedure(self, p):
        """call_procedure : VARIABLE OPSQBR varlist CLSQBR"""
        if (not self.proc_names.__contains__(p[1])):
            #sys.stderr.write("Error procedure wasn't declared")
            self.errors.append(f"Line: {p.lineno(1)} Error: Procedure '{p[1]}' wasn't declared")
        p[0] = SyntTree('call_procedure', value=p[1], child=[p[3]], lineno=p.lineno(1))

    def p_varlist(self, p):
        """varlist : varlist VARIABLE
                   | VARIABLE"""
        if len(p) == 3:
            p[0] = SyntTree('varlist', child=[p[1], SyntTree('variable', value=p[2], lineno=p.lineno(1))], lineno=p.lineno(1))
        else:
            p[0] = SyntTree('variable', value=p[1], lineno=p.lineno(1))

    def p_if_err(self, p):
        """if_err : IF error sentence_groups ELSE sentence_groups
              | IF error sentence_groups"""
        self.errors.append(f"Line: {p.lineno(2)} Error: Wrong IF condition: {p[2].value}")
        if len(p) == 5:
            p[0] = SyntTree('er_if_else', lineno=p.lineno(1))
        else:
            p[0] = SyntTree('er_if', lineno=p.lineno(1))

    def p_while_err(self, p):
        """while_err : WHILE error DO sentence_groups
                 | WHILE error
                 | WHILE logic_expr error"""
        if len(p) == 5:
            self.errors.append(f"Line: {p.lineno(2)} Error: Wrong WHILE condition: {p[2].value}")
            p[0] = SyntTree('while_err', child=[p[4]], lineno=p.lineno(1))
        else:
            self.errors.append(f"Line: {p.lineno(2)} Error: Wrong WHILE declaration: {p[2].value}")
            p[0] = SyntTree('while_err', lineno=p.lineno(1))

    def p_if(self, p):
        """if : IF logic_expr sentence_groups ELSE sentence_groups
              | IF logic_expr sentence_groups"""
        if len(p) == 6:
            p[0] = SyntTree('if_else', child=[p[2], p[3], p[5]], lineno=p.lineno(1))
        else:
            p[0] = SyntTree('if', child=[p[2], p[3]], lineno=p.lineno(1))

    def p_while(self, p):
        """while : WHILE logic_expr DO sentence_groups"""
        p[0] = SyntTree('while', child=[p[2], p[4]], lineno=p.lineno(1))

    def p_robot_command(self, p):
        """robot_command : logic_cmd
                         | rot_dir
                         | math_cmd"""
        p[0] = p[1]

    def p_rot_dir(self, p):
        """rot_dir : BACK
                   | RIGHT
                   | LEFT"""
        p[0] = SyntTree('cmd_rot', value=p[1], lineno=p.lineno(1))

    def p_logic_cmd(self, p):
        """logic_cmd : STEP"""
        p[0] = SyntTree('cmd_step', value=p[1], lineno=p.lineno(1))

    def p_math_cmd(self, p):
        """math_cmd : LOOK"""
        p[0] = SyntTree('cmd_look', value=p[1], lineno=p.lineno(1))

    def p_map_setting(self, p):
        """map_setting : BAR OPSQBR VARIABLE VARIABLE math_expr math_expr CLSQBR
                        | EMP OPSQBR VARIABLE VARIABLE math_expr math_expr CLSQBR
                        | SET OPSQBR VARIABLE VARIABLE math_expr math_expr CLSQBR
                        | CLR OPSQBR VARIABLE VARIABLE math_expr math_expr CLSQBR"""
        p[0] = SyntTree('map_setting', value=p[1],child=[SyntTree('variable', value=p[3], lineno=p.lineno(3)), SyntTree('variable', value=p[4], lineno=p.lineno(4)), p[5], p[6]], lineno=p.lineno(1))

    def p_empty(self, p):
        'empty :'
        pass

    def p_error(self, p):
        try:
            #sys.stderr.write(f"Unknown Error on {p.lineno} line Token: {p}\n")
            self.errors.append(f"Line: {p.lineno(0)} Error: Wrong syntax expression '{p[0].value}' ")
        except Exception:
            #sys.stderr.write(f"Unknown ERROR {p}")
            self.errors.append(f"Line: {p.lineno} Error: Wrong syntax expression '{p.value}'")


if __name__ == '__main__':
    f = open(r"C:\Users\Amr\PycharmProjects\Interpretator\Parser\check.txt", 'r')
    data = f.read()
    parser = Parser()
    res, errors = parser.parse(data)
    res.print()