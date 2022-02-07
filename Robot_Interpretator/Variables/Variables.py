import sys


class Variable:
    def __init__(self, type, value, name=''):
        self.type = type
        self.value = None
        self.set_value(value)
        self.name = name

    def set_value(self, value):
        if (value == True or value == False):
            if self.type == 'int' or self.type == 'cint':
                self.convert_type(value)
            else:
                self.value = value
        elif self.type != 'boolean' or self.type != 'cboolean':
            self.value = value
        else:
            sys.stderr.write("Error: INT couldn't be converted to BOOLEAN")
            raise Exception

    def __repr__(self):
        return f"Type: {self.type}; Name: {self.name};  Value: {self.value};"

    def convert_type(self, value):
        if value == True:
            self.value = 1
        else:
            self.value = 0


if __name__ == '__main__':
    v = Variable('boolean', True, 'v')
    v.set_value(12)
    print(v)