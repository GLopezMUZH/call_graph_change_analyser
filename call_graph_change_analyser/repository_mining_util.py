# %%
import os
import subprocess
from subprocess import *
from typing import List
import logging

from importlib import reload
from pydriller import *

from models import *
from gumtree_difffile_parser import get_method_call_change_info_cpp
from utils_sql import *
import utils_py

# %%
import utils_sql
reload(utils_sql)
reload(models)


# %%
# os.environ['COMSPEC']

# %%
# con.close()

# %%
# Functions


def save_source_code(file_path, source_text):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    if isinstance(source_text, bytes):
        logging.debug("save_source_code was bytes")
        source_text = source_text.decode('utf-8')

    try:
        f = open(file_path, 'w', encoding='utf-8')
    except:
        logging.error("could not open/write file: {0}".format(file_path))

    try:
        f.writelines(source_text)
    except UnicodeEncodeError:
        # some pydriller.commit.mod_file.source_text has encoding differences
        print("ERROR writelines", type(source_text))
        logging.warning("ERROR writelines {0}".format(type(source_text)))
        f.write(source_text.encode('utf-8-sig'))
    f.close()
    save_source_code_xml(file_path)


def save_source_code_xml(file_path):
    exec_cmd = "srcml"
    xml_filename = file_path.__str__() + ".xml"
    arg_target_symbol = ">"
    subprocess.run(
        [exec_cmd, file_path, arg_target_symbol, xml_filename],
        shell=True, capture_output=True
    )


def save_source_code_diff_file(arg_prev, arg_curr, arg_target_file):
    exec_cmd = "gumtree"
    diff_type = "textdiff"  # "textdiff" "parse"
    arg_target_symbol = ">"
    subprocess.run(
        [exec_cmd, diff_type, arg_prev, arg_curr,
            arg_target_symbol, arg_target_file],
        shell=True, capture_output=True
    )


def is_java_file(mod_file: str):
    return mod_file[-5:] == '.java'


def is_cpp_file(mod_file: str):
    # or mod_file[-2:] == '.h'
    return mod_file[-4:] == '.cpp' or mod_file[-2:] == '.c'


def is_python_file(mod_file: str):
    return mod_file[-3:] == '.py'


def get_file_type_validation_function(proj_lang):
    if proj_lang == 'java':
        return is_java_file
    if proj_lang == 'cpp':
        return is_cpp_file
    if proj_lang == 'python':
        return is_python_file


def save_method_call_change_info(file_path_sourcediff):
    mcci = None
    if is_java_file(file_path_sourcediff):
        None
    elif is_cpp_file(file_path_sourcediff):
        mcci = get_method_call_change_info_cpp(file_path_sourcediff)
    elif is_python_file(file_path_sourcediff):
        None
    return mcci


def get_file_imports(source_code: str, mod_file_data: FileData) -> List[FileImport]:
    count = 0
    r = []
    for code_line in source_code.splitlines():
        count += 1
        if count < 500:
            if code_line.startswith("#include "):
                f_name, f_path, f_dir_path = get_import_file_data(
                    mod_file_data.get_file_dir_path(), code_line)

                fi = FileImport(src_file_data=mod_file_data,
                                import_file_path=f_path,
                                import_file_name=f_name,
                                import_file_dir_path=f_dir_path)
                r.append(fi)
        else:
            break

    return r


def get_import_file_data(mod_file_dir_path, code_line: str):
    f_name = ''
    f_dir_path = ''
    f_path = code_line[9:len(code_line.rstrip())].replace('"', '')
    f_path = f_path.replace('<', '')
    f_path = f_path.replace('>', '')
    f_name = os.path.basename(f_path)

    """
                for x in str(f_path).split('/'):
                    if(x.__contains__('.h') or x.__contains__('.hpp')):
                        f_name = x
                f_path = f_path.replace(f_name, '')
                """
    # includes libraries eg. <cmath> <QApplication>
    if code_line.__contains__('<'):
        f_name = f_path

    if (code_line.__contains__('"') and not code_line.__contains__('/')):
        f_dir_path = mod_file_dir_path
        f_name = f_path
    else:
        f_dir_path = os.path.dirname(f_path)
    return f_name, f_path, f_dir_path


def jarWrapper(*args):
    process = Popen(['java', '-jar']+list(args), stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith(b'\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split(b'\n')
    if stderr != '':
        ret += stderr.split(b'\n')
    ret.remove(b'')
    return ret


def read_xml_diffs_from_file(file_path: str):
    # read xml in case saved on file
    with open(file_path, 'r') as f:
        data = f.read()


def get_calls(raw):
    indents = [(0, 0, 'root')]
    for a in raw.split('\n'):
        indent = 0
        while (a[indent] == ' '):
            indent += 1
        if indent % 4:
            print("not multiple of 4")
            break
        cnt = a.replace('  ', '')
        cnt = cnt.split("[", -1)[0]
        indents.append((len(indents), int(indent/4)+1, cnt))
    for a in indents:
        print(a)


def parse_xml_call_diffs(diff_xml_file, path_to_cache_current, mod_file_data: FileData) -> List[CallCommitInfo]:
    r = []
    try:
        f_name = diff_xml_file.dstFile.get_text()
        # TODO check how path is written
        f_name = f_name.replace(path_to_cache_current, '')
        logging.debug("Dest file name: {0}".format(f_name))

        for an in diff_xml_file.find_all('action'):
            logging.debug('---action node----')
            action_node_type = an.actionNodeType.get_text()
            logging.debug("Action node type: {0}".format(
                str(action_node_type)))
            ac = utils_py.get_action_class(an.actionClassName.get_text())
            logging.debug("CHECK Action class: {0}, ac: {1} ".format(
                an.actionClassName.get_text(), str(ac)))
            handled = an.handled.get_text()
            logging.debug("Handled: {0}".format(handled))
            parent_function_name = an.parentFunction.get_text()
            logging.debug("Parent: {0}".format(parent_function_name))
            an_calls = an.calls
            logging.debug("an_calls: {0}".format(an_calls))

            for ncall in an.calls.find_all('callName'):
                logging.debug(ncall.get_text())
                called_function_name = ncall.get_text()
                cci = CallCommitInfo(src_file_data=mod_file_data,
                                     calling_function=parent_function_name,
                                     called_function=called_function_name,
                                     action_class=ac)
                r.append(cci)
                # get_calls(at.get_text())
    except Exception as err:
        logging.exception(err)
    return r

