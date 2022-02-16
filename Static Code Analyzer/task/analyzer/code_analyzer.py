import sys
import os
import re
import ast
# write your code here

class Static_code_analiz:

    code = {'S001': 'Too long',
            'S002': 'Indentation is not a multiple of four',
            'S003': 'Unnecessary semicolon',
            'S004': 'At least two spaces required before inline comments',
            'S005': 'TODO found',
            'S006': 'More than two blank lines used before this line',
            'S007': 'Too many spaces after construction_name (def or class);',
            'S008': 'Class name class_name should be written in CamelCase;',
            'S009': 'Function name function_name should be written in snake_case.',
            'S010': 'Argument name arg_name should be written in snake_case;',
            'S011': 'Variable var_name should be written in snake_case;',
            'S012': 'The default argument value is mutable.'
    }

    def __init__(self, file):
        self.error = []
        self.lines = []
        self.path = file
        with open(file, 'r') as f:
            #self.tree = ast.parse(f.read())
            #print(ast.dump(self.tree))
            for line in f.readlines():
                #print(line)
                self.lines.append(line)
        with open(file, 'r') as f:
            self.tree = ast.parse(f.read())
        #print(len(self.lines))
        for n_line, line in enumerate(self.lines):
            self.lines_should_not_exceed(n_line, line)
            self.indentation_is_not_a_multiple_of_four(n_line, line)
            self.unnecessary_semicolon(n_line, line)
            self.least_two_spaces_comments(n_line, line)
            self.TODO_found(n_line, line)
            self.more_two_blank_lines(n_line, line)
            self.class_name_should_be_written_in_camel_case(n_line, line)
            self.function_name_should_be_written_in_snake_case(n_line, line)

        self.argument_name_should_be_written_in_snake_case()
        self.var_name_should_be_written_in_snake_case()
        self.default_argument_value_is_mutable()
        self.print_error_end()

    def lines_should_not_exceed(self, n_line, line, max_size=79):
        if len(line) > 79:
            self.print_error(n_line+1, 'S001')

    def indentation_is_not_a_multiple_of_four(self, n_line, line,):
        tab = 0
        while line[tab] == ' ':
            tab += 1
        if tab % 4 != 0:
            self.print_error(n_line+1, 'S002')

    def unnecessary_semicolon(self, n_line, line):
        index = len(line)-1
        if '#' in line:
            index = line.index('#')

        if '\'' in line or '\"' in line:
            if '\'' in line:
                l = line.split('\'')
            elif '\"' in line:
                l = line.split('\"')
            if ';' in l[0]:
                self.print_error(n_line + 1, "S003")
            if ';' in l[2]:
                if line.find('#') == -1:
                    self.print_error(n_line + 1, "S003")
                elif line.find(';') < line.find('#'):
                    self.print_error(n_line + 1, "S003")
            return
        if ';' in line[:index]:
            self.print_error(n_line+1, "S003")

    def least_two_spaces_comments(self, n_line, line):
        if "#" in line:
            index = line.index('#')
            #print(index)
            #print(line[index-1])
            #print(line[index - 2])
            if index > 2 and (line[index-1] != ' ' or line[index-2] != ' '):
                self.print_error(n_line + 1, "S004")

    def TODO_found(self, n_line, line):
        if '#' in line:
            index = line.index('#')
            index = line[index:].upper().find('TODO')
            if index != -1:
                self.print_error(n_line + 1, "S005")

    def more_two_blank_lines(self, n_line, line):
        #print(len(line.strip()), '1:',len(self.lines[n_line-1].strip()), ",2:", len(self.lines[n_line-2].strip()), ",3:", len(self.lines[n_line-3].strip()) )
        if len(line.strip()) != 0 and n_line > 2:
            if len(self.lines[n_line-1].strip()) == 0 and len(self.lines[n_line-2].strip()) == 0 and len(self.lines[n_line-3].strip()) == 0:
                self.print_error(n_line + 1, "S006")

    def class_name_should_be_written_in_camel_case(self, n_line, line):
        template = r"class .+:$"
        temp2 = r"class [A-Z][^_]*:$"
        temp3 = r"class +[A-Z][^_]*:$"
        class_name = re.findall(template, line)
        for item in class_name:
            if not re.match(temp2, item):
                if re.match(temp3, item):
                    self.print_error(n_line + 1, "S007")
                else:
                    self.print_error(n_line + 1, "S008")

    def function_name_should_be_written_in_snake_case(self, n_line, line):
        template = r"def .+:$"
        temp2 = r"def [a-z_][^A-Z]*\(.*\):$"
        temp3 = r"def +[a-z_][^A-Z]*\(.*\):$"
        class_name = re.findall(template, line)
        for item in class_name:
            if not re.match(temp2, item):
                if re.match(temp3, item):
                    self.print_error(n_line + 1, "S007")
                else:
                    self.print_error(n_line + 1, "S009")

    def argument_name_should_be_written_in_snake_case(self):
        temp_var = r"^[a-z_]+$"
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                #function_name = node.name
                #args_def = [item.value for item in node.args.defaults]
                n_line = node.lineno
                args = [item.arg for item in node.args.args]
                for arg in args:
                    if not re.match(temp_var, arg):
                        self.print_error(n_line, "S010")
                # print(node.value.value)
                # print(node.targets[0].id)
                #print(f'name:{function_name}, args:{args},default={args_def}')

    def var_name_should_be_written_in_snake_case(self):
        vars = set()
        temp_var = r"^[a-z_]+$"
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                try:

                    #print(node.targets[0].id)
                    name = node.targets[0].id
                    #print(name, re.match(temp_var, name))
                    #value = node.value.value
                    n_line = node.lineno

                    if re.match(temp_var, name) is None and name not in vars:
                        #print('error')
                        #print(f"Line {n_line}: {name}={value}")
                        self.print_error(n_line, "S011")
                        vars.add(name)
                except AttributeError:
                    continue

    def default_argument_value_is_mutable(self):
        temp_arg = r"[a-z_0-9-]+"
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                for item in node.args.defaults:
                    try:
                        if not (re.match(temp_arg, str(item.value)) or str(item.value) == 'None'):
                            n_line = node.lineno
                            print(item.value)
                            self.print_error(n_line, "S012")
                    except AttributeError:
                        n_line = node.lineno
                        self.print_error(n_line, "S012")

    def print_error(self, line, code, message=None):

        if message is None:
            message = self.code[code]
        self.error.append({'line': line, 'code': code, 'message': message})
        #print(f"{self.path}: Line {line}: {code} {message}")

    def print_error_end(self):
        self.error.sort(key=lambda x: x['line'])
        for error in self.error:
            print(f"{self.path}: Line {error['line']}: {error['code']} {error['message']}")


def parsing_args(args):
    paths=[]
    if len(args)<2:
        return None
    if args[1][-1] == 'y' and args[1][-2] == 'p':
        paths.append(args[1])
    else:
        files = os.listdir(args[1])
        for file in files:
            if file[-1] == 'y' and file[-2] == 'p':
                paths.append(f'{args[1]}{os.sep}{file}')
    paths.sort(key=lambda x: int(x[-4]))
    return paths

args = sys.argv  # we get the list of arguments
list = parsing_args(args)


for dir in list:
    code_chek = Static_code_analiz(dir)
