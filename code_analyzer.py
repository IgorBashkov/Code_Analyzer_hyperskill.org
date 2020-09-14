import sys
import re
from pathlib import Path


def print_msg(num, content):
    errs = {
        'S001': 'Too long line',
        'S002': 'Indentation is not a multiple of four',
        'S003': 'Unnecessary semicolon',
        'S004': 'At least two spaces before inline comments required',
        'S005': 'TODO found',
        'S006': 'More than two blank lines used before this line',
        'S007': f'Too many spaces after "{content.get("construction_name")}"',
        'S008': f'Class name "{content.get("class_name")}" should use CamelCase',
        'S009': f'Function name "{content.get("function_name")}" should use snake_case',
    }
    print(f'{content["file_name"]}: Line {num + 1}: {content["code"]} {errs[content["code"]]}')


def check_err_1(line):  # string length greater then 79
    return len(line) > 79


def check_err_2(line):  # Indentation is not a multiple of four
    spaces = 0
    for ch in line:
        if ch == ' ':
            spaces += 1
        else:
            break
    return bool(spaces % 4)


def check_err_3(line):  # Unnecessary semicolon
    q, q2 = False, False
    if ';' in line:
        if '#' in line:
            line = line[:line.find('#')]
    while line:
        if line[0] == ';' and not (q or q2):
            return True
        if line[0] == '\\':
            line = line[2:]
        if line[0] == '\'' and not q2:
            q = not q
        if line[0] == '\"' and not q:
            q2 = not q2
        line = line[1:]
    return False


def check_err_4(line):  # At least two spaces before inline comments required
    if '#' in line:
        pos = line.find('#')
        return line[0:pos][-2:] != '  ' and pos > 1
    return False


def check_err_5(line):  # TO_DO found
    if '#' in line:
        return 'todo' in line[line.find('#'):].lower()
    return False


def check_err_6(line, empty_lines=[]):  # More than two blank lines used before this line
    if not len(line.strip()):
        empty_lines.append(1)
    else:
        len_empty_lines = len(empty_lines)
        empty_lines.clear()
        return len_empty_lines > 2
    return False


def check_err_7(line):  # Check spaces after construction name
    temp = r' *(def|class) {2,}'
    res = re.search(temp, line)
    if res:
        return True, {"constuctrion_name": res[1]}
    return False


def check_err_8(line):  # Check class name for camel case
    name_temp = r' *class +(?P<class>[A-Za-z0-9_]+)[\(:]'
    camel_temp = r'^([A-Z][a-z0-9]+)+$'
    name = re.search(name_temp, line)
    if name is not None:
        if re.match(camel_temp, name['class']) is None:
            return True, {"class_name": name['class']}
    return False


def check_err_9(line):
    name_temp = r' *def +(?P<func>[A-Za-z0-9_]+)[\(:]'
    snake_temp = r'^_{,2}([a-z0-9]+_?)+_?$'
    name = re.search(name_temp, line)
    if name is not None:
        if re.match(snake_temp, name['func']) is None:
            return True, {"function_name": name['func']}
    return False


def check_errors(num, line, file_name):
    check_dict = {
        check_err_1: 'S001',
        check_err_2: 'S002',
        check_err_3: 'S003',
        check_err_4: 'S004',
        check_err_5: 'S005',
        check_err_6: 'S006',
        check_err_7: 'S007',
        check_err_8: 'S008',
        check_err_9: 'S009',
    }
    for func, code in check_dict.items():
        res = func(line)
        if res:
            content = {'file_name': file_name,
                       'code': code}
            if isinstance(res, tuple):
                content.update(res[1])
            print_msg(num, content)


def check_file(file_name):
    with open(file_name) as f:
        for n, ln in enumerate(f):
            check_errors(n, ln, file_name)


def main():
    arg = sys.argv[1]
    if arg.endswith('.py'):
        check_file(arg)
    else:
        arg = arg if arg[-1] in '\\/' else arg + '\\'
        for item in Path(arg).iterdir():
            if item.is_file() and item.name.endswith('.py'):
                check_file(arg + item.name)


if __name__ == '__main__':
    main()
