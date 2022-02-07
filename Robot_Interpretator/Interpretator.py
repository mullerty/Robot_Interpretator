from Parser.YaccParser import Parser
from Robot_Interpretator.Robot.Robot import Robot
from Robot_Interpretator.Variables.Variables import Variable
import sys


class Var_proc:
    def __init__(self):
        self.pre = None
        self.vars = {}
        self.rob_maps = {}
        self.next = None


class Interpreter:
    def __init__(self, program, robot, x, y):
        self.parser = Parser()
        self.program_file = program
        self.robot = robot
        self.x_ex = x
        self.y_ex = y
        self.procs = {}
        self.curProc = None
        self.variables = Var_proc()

    def start(self):
        tree, errors = self.parser.parse(self.program_file)
        if len(errors) == 0:
            self.tree_analyser(tree)
            return self.robot.escaped(self.x_ex, self.y_ex)
        else:
            sys.stderr.write('\nERRORS FOUND:\n')
            for i in errors:
                sys.stderr.write(i+'\n')
        return False

    def tree_analyser(self, node):
        node_type = node.type
        if node_type is None:
            return
        elif node_type == 'Program Start':
            self.tree_analyser(node.child[0])
        elif node_type == 'sentence_group':
            self.tree_analyser(node.child[0])
            self.tree_analyser(node.child[1])
        elif node_type == 'Program End':
            return
        elif node_type == 'definition':
            var_name = node.child[0].value
            var_type = node.value
            try:
                if var_type != 'map':
                    var_value = self.var_setter(node.child[1])
                    self.definition(var_type, var_name, var_value.value)
                else:
                    self.map_definition(var_name)
            except Exception as err:
                sys.stderr.write(f"Line: {node.lineno} Error: Something wrong in definition")
                raise err
        elif node_type == 'assign':

            var1 = node.child[0]
            if self.variables.vars.__contains__(var1.value):
                var1 = self.variables.vars[var1.value]
            else:
                sys.stderr.write(f"Variable '{var1.value}' wasn't defined!")
                raise Exception

            var2 = self.var_setter(node.child[1])

            try:
                if not (var2 is None):
                    self.assign(var1, var2)
            except Exception as err:
                sys.stderr.write(f"Line: {node.lineno} Error: Something wrong in Assign")
                raise err
        elif node_type == 'if' or node_type == 'if_else':
            try:
                if node_type == 'if_else':
                    self.if_else(node.child[0], node.child[1], node.child[2])
                else:
                    self.if_else(node.child[0], node.child[1])
            except Exception as err:
                print(f"Line: {node.lineno} Error: Something wrong in IF statement")
                raise err
        elif node_type == 'while':
            try:
                self.while_do(node)
            except Exception as err:
                print(f"Line: {node.lineno} Error: Something wrong in DO WHILE statement")
                raise err
        elif node_type == 'procedure':
            try:
                self.dec_proc(node)
            except Exception as err:
                print(f"Line: {node.lineno} Error: Something wrong in procedure declaration")
                raise err
        elif node_type == 'call_procedure':
            try:
                self.callproc(node)
            except Exception as err:
                print(f"Line: {node.lineno} Error: Something wrong in Call function")
                raise err
        elif node.type == 'cmd_rot':
            if node.value == 'back':
                self.robot.back()
            elif node.value == 'right':
                self.robot.right()
            elif node.value == 'left':
                self.robot.left()
        elif node.type == 'cmd_step':
            self.robot.step()
        elif node.type == 'cmd_look':
            self.robot.look()
        elif node.type == 'map_setting':
            try:
                var0 = self.var_setter(node.child[0])
                if var0.type == 'cint' or var0.type == 'cboolean':
                    sys.stderr.write(f"Line: {node.lineno} Error: CBOOLEAN or CINT can't be changed")
                    raise Exception
                var1 = node.child[1].value
                if not self.variables.rob_maps.__contains__(var1):
                    sys.stderr.write(f"Line: {node.lineno} Error: Map variable '{var1}' wasn't defined")
                    raise Exception
                var2 = self.var_setter(node.child[2])
                if var2.type == 'boolean' or var2.type == 'cboolean':
                    var2.type = 'int'
                    if var2.value:
                        var2.value = 1
                    else:
                        var2.value = 0
                var3 = self.var_setter(node.child[3])
                if var3.type == 'boolean' or var3.type == 'cboolean':
                    var3.type = 'int'
                    if var3.value:
                        var3.value = 1
                    else:
                        var3.value = 0

                if node.value == 'bar':
                    self.bar(var0, var1, var2.value, var3.value)
                elif node.value == 'emp':
                    self.emp(var0, var1, var2.value, var3.value)
                elif node.value == 'set':
                    self.set(var0, var1, var2.value, var3.value)
                elif node.value == 'clr':
                    self.clr(var0, var1, var2.value, var3.value)
            except Exception as err:
                print(f"Line: {node.lineno} Error: Something wrong in map settings")
                raise err

    # Методы для работы с переменными

    def var_setter(self, node):
        if node.type == 'math_expr':
            return self.math_expr(node)
        elif node.type == 'variable':
            if self.variables.vars.__contains__(node.value):
                return self.variables.vars[node.value]
            else:
                sys.stderr.write(f"Variable '{node.value}' wasn't defined!")
                raise Exception
        elif node.type == 'cmd_look':
            return self.robot.look()
        elif node.type == 'number':
            return Variable('int', int(node.value))
        elif node.type == 'logic_expr':
            return self.logic_expr(node)
        elif node.type == 'cmd_step':
            return self.robot.step()
        elif node.type == 'bool':
            if node.value == 'true':
                return Variable('boolean', True)
            else:
                return Variable('boolean', False)
        elif node.type == 'call_procedure':
            return self.callproc(node)

    def definition(self, type, name, value):
        if not self.variables.vars.__contains__(name):
            variable = Variable(type, value, name)  # (type, value, name)
        else:
            sys.stderr.write(f"Variable '{name}' already defined!")
            raise Exception
        try:
            self.variables.vars[name] = variable
            print(f"Defined: {variable}")
        except variable.value is None:
            sys.stderr.write(f"Wrong value for variable '{name}'!")
            raise Exception

    def map_definition(self, name):
        if not self.variables.rob_maps.__contains__(name):
            self.variables.rob_maps[name] = {}
        else:
            sys.stderr.write(f"Map '{name}' already defined!")
            raise Exception

    def assign(self, var1, var2):
        if var1.type != 'cboolean' or var1.type != 'cint':
            var1.set_value(var2.value)
            self.variables.vars[var1.name] = var1
            print(f"Assigned: {var1}")
        else:
            sys.stderr.write("Error: CBOOLEAN and CINT couldn't be changed")
            raise Exception

    def math_expr(self, node):

        result = None
        first = self.var_setter(node.child[0])
        second = self.var_setter(node.child[1])

        if first.type == 'boolean':
            first.type = 'int'
            if first.value:
                first.value = 1
            else:
                first.value = 0

        if second.type == 'boolean':
            second.type = 'int'
            if second.value:
                second.value = 1
            else:
                second.value = 0

        if node.value == 'inc':
            result = first.value + second.value
        elif node.value == 'dec':
            result = first.value - second.value

        return Variable('int', result)

    def logic_expr(self, node):

        result = None

        if node.value == 'not':
            first = self.var_setter(node.child[0])
            if first.type != 'boolean':
                sys.stderr.write(f"Line: {node.lineno} Error: Wrong NOT expression")
                raise Exception
            result = not first.value
        elif node.value == 'or':
            first = self.var_setter(node.child[0])
            second = self.var_setter(node.child[1])
            if first.type != 'boolean' and second.type != 'boolean':
                sys.stderr.write(f"Line: {node.lineno} Error: Wrong OR expression")
                raise Exception
            result = first.value or second.value
        elif node.value == 'gt' or node.value == 'lt':
            first = self.var_setter(node.child[0])
            second = self.var_setter(node.child[1])
            if first.type == 'boolean':
                if first.value:
                    first.value = 1
                else:
                    first.value = 0
            if second.type == 'boolean':
                if second.value:
                    second.value = 1
                else:
                    second.value = 0

            if node.value == 'gt':
                result = first.value > second.value
            elif node.value == 'lt':
                result = first.value < second.value

        return Variable('boolean', result)

    # Методы для if и while
    def createNewIf_While_Env(self):
        current = Var_proc()
        current.vars = self.variables.vars
        current.rob_maps = self.variables.rob_maps
        current.pre = self.variables
        self.variables.next = current
        self.variables = self.variables.next

    def returnIf_While_Env(self):
        intersection = self.variables.pre.vars.keys() & self.variables.vars.keys()
        for i in intersection:
            self.variables.pre.vars[i] = self.variables.vars[i]
        intersection = self.variables.pre.rob_maps.keys() & self.variables.rob_maps.keys()
        for i in intersection:
            self.variables.pre.rob_maps[i] = self.variables.rob_maps[i]
        self.variables = self.variables.pre

    def if_else(self, expression, then_statement, else_statement=None):
        self.createNewIf_While_Env()
        condition = self.logic_expr(expression).value
        if condition:
            self.tree_analyser(then_statement)
        elif not (else_statement is None):
            self.tree_analyser(else_statement)
        self.returnIf_While_Env()

    def while_do(self, node):
        body = node.child[1]
        expression = node.child[0]
        self.createNewIf_While_Env()
        counter = 0
        condition = self.logic_expr(expression).value
        while condition:
            counter += 1
            self.tree_analyser(body)
            condition = self.var_setter(expression).value
            if counter > 1000:
                sys.stderr.write(f"Line: {node.lineno} Error: WHILE runtime error")
                raise Exception
        self.returnIf_While_Env()

    # Методы для процедур
    def createNewProcEnv(self, varlist, varlist_call):
        current = Var_proc()
        current.pre = self.variables
        for i in range(len(varlist)):
            current.vars[varlist[i]] = self.variables.vars[varlist_call[i]]
        self.variables.next = current
        self.variables = self.variables.next

    def returnProcEnv(self, vars, vars_pre):
        for i in range(len(vars)):
            if self.variables.pre.vars[vars_pre[i]].type == self.variables.vars[vars[i]].type:
                self.variables.pre.vars[vars_pre[i]] = self.variables.vars[vars[i]]
            else:
                sys.stderr.write(f"Error: Wrong types of variables!")
                raise Exception
        self.variables = self.variables.pre

    def varlist(self, node, varlist):
        if node.type == 'varlist':
            if not varlist.__contains__(node.child[1].value):
                self.varlist(node.child[0], varlist)
                varlist.append(node.child[1].value)
            else:
                sys.stderr.write(f"Line: {node.lineno} Error: Duplication of variables in procedure declaration")
                raise Exception
        elif node.type == 'variable':
            if not varlist.__contains__(node.value):
                varlist.append(node.value)
            else:
                sys.stderr.write(f"Line: {node.lineno} Error: Duplication of variables in procedure declaration")
                raise Exception

    def dec_proc(self, node):
        varlist = []
        self.varlist(node.child[0], varlist)
        self.procs[node.value] = [varlist, node.child[1]]

    def callproc(self, node):
        proc = self.procs[node.value]
        varlist = []
        self.varlist(node.child[0], varlist)
        for i in varlist:
            if not self.variables.vars.__contains__(i):
                sys.stderr.write(f"Line: {node.lineno} Error: Variable {i} wasn't defined")
                raise Exception
        if len(varlist) != len(proc[0]):
            sys.stderr.write(f"Line: {node.lineno} Error: Wrong number of variables in procedure call")
            raise Exception

        self.createNewProcEnv(proc[0], varlist)
        self.tree_analyser(proc[1])
        self.returnProcEnv(proc[0], varlist)
        result = self.variables.vars[varlist[0]]
        print(f"Procedure '{node.value}' returned: {result}")
        return result

    # Методы для настройки карты робота (ПОДПРАВИТЬ!)
    def bar(self, res, map, x, y):
        if self.variables.rob_maps[map].get((x, y)) == '#':
            self.variables.vars[res.name] = Variable('boolean', True, res.name)
        else:
            self.variables.vars[res.name] = Variable('boolean', False, res.name)

    def emp(self, res, map, x, y):
        if self.variables.rob_maps[map].get((x, y)) != '#':
            self.variables.vars[res.name] = Variable('boolean', True, res.name)
        else:
            self.variables.vars[res.name] = Variable('boolean', False, res.name)

    def set(self, res, map, x, y):

        if res.value:
            self.variables.rob_maps[map].update({(x, y): '#'})
        else:
            self.variables.rob_maps[map].update({(x, y): ''})

    def clr(self, res, map, x, y):
        self.variables.rob_maps[map].update({(x, y): '?'})
        self.variables.vars[res.name] = Variable('boolean', True, res.name)


if __name__ == '__main__':
    f = open(r"C:\Users\Amr\PycharmProjects\Interpretator\Parser\check2.txt", 'r')
    data = f.read()
    robot = Robot()
    x, y = robot.create_map(r'C:\Users\Amr\PycharmProjects\Interpretator\Robot_Interpretator\Robot\Maps\Map3.txt')
    inter = Interpreter(data, robot, x, y)
    if inter.start():
        print(f"Robot found exit")
        inter.robot.print_map()
    else:
        print(f"Robot can't find exit")