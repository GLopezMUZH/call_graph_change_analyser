# %%
import os
import subprocess
from subprocess import *
from typing import Optional
import logging

from pathlib import Path
from imp import reload
from pydriller import *
from bs4 import BeautifulSoup

from models import *
import models
from models import CallCommitInfo, ProjectPaths, ProjectConfig, FileData
from gumtree_difffile_parser import get_method_call_change_info_cpp
from utils_sql import initate_analytics_db

# %%
import utils_sql
reload(utils_sql)
reload(models)


# %%
os.environ['COMSPEC']

# %%
# con.close()

# %%
# Functions


def save_source_code(file_path, source_text):
    if not os.path.exists(str(file_path.parent)):
        os.makedirs(str(file_path.parent))
    try:
        f = open(file_path, 'x')
    except FileExistsError:
        f = open(file_path, 'w')
    f.writelines(source_text)
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


def clone_git_source(path_to_git_folder, path_to_git):
    if not os.path.exists(str(path_to_git_folder)):
        os.makedirs(str(path_to_git_folder))

    # git.Git(path_to_git_folder).clone(path_to_git)   # ("git://gitorious.org/git-python/mainline.git")


def is_java_file(mod_file: str):
    return mod_file[-5:] == '.java'


def is_cpp_file(mod_file: str):
    return mod_file[-4:] == '.cpp' or mod_file[-2:] == '.c' or mod_file[-2:] == '.h'


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


def get_file_imports(source_code: str, mod_file_data: FileData):
    count = 0
    r = []
    for line in source_code.splitlines():
        count += 1
        if count < 500:
            if line.startswith("#include "):
                logging.debug("Include line{}: {}".format(count, line.strip()))
                f_path = line[9:len(line)].replace('"', '')
                f_path = f_path.replace('<', '')
                f_path = f_path.replace('>', '')
                f_name = ''
                for x in str(f_path).split('/'):
                    if(x.__contains__('.h') or x.__contains__('.hpp')):
                        f_name = x
                f_path = f_path.replace('>', '')
                f_path = f_path.replace(f_name, '')
                import_default_dir_path = mod_file_data.file_dir_path if line.__contains__(
                    '"') else f_path
                # TODO GGG replace  backslash from unix path ???
                fi = FileImports(src_file_data=mod_file_data,
                                 import_file_dir_path=import_default_dir_path,
                                 import_file_name=f_name)
                r.append(fi)
                logging.debug(fi)
        else:
            break

    return r


#from subprocess import *

def _jarWrapper(*args):
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


def parse_xml_diffs(diff_xml_file):

    for an in diff_xml_file.find_all('action'):
        logging.debug('---action node----')
        # print(type(an))
        # print(an)
        for at in an.find_all('actionText'):
            logging.debug(type(at))
            logging.debug(at)


# %%
def load_source_repository_data(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)

    """
    if proj_config.get_end_repo_date == None:
        repository_generator = Repository(
                path_to_repo=proj_config.get_path_to_repo(),
                since=proj_config.get_start_repo_date).traverse_commits()
                #only_modifications_with_file_types=proj_config.get_commit_file_types()
    else:
        repository_generator = Repository(
                path_to_repo=proj_config.get_path_to_repo(),
                since=proj_config.get_start_repo_date,
                to=proj_config.get_end_repo_date()).traverse_commits()
    """

    logging.debug(proj_config.get_path_to_repo())
    logging.debug(proj_config.get_start_repo_date())
    logging.debug(proj_config.get_start_repo_date().tzinfo)
    logging.debug(proj_config.get_end_repo_date())
    logging.debug(proj_config.get_commit_file_types())

    # default is order='reverse'
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            since=proj_config.get_start_repo_date(),
            to=proj_config.get_end_repo_date(),
            only_modifications_with_file_types=proj_config.get_commit_file_types()).traverse_commits():
        for mod_file in commit.modified_files:
            # print('Extension: ', str(mod_file._new_path)[-3:])
            if (is_valid_file_type(str(mod_file._new_path))):
                logging.debug('---------------------------')
                logging.debug(mod_file.change_type)
                logging.debug(str(mod_file._new_path))
                logging.debug(mod_file._old_path)
                # logging.debug(mod_file._new_path)
                # logging.debug(mod_file.diff)

                mod_file_data = FileData(str(mod_file._new_path))
                logging.debug(mod_file_data)

                # Save new source code
                file_path_current = Path(
                    proj_paths.get_path_to_cache_current() + str(mod_file._new_path))
                save_source_code(file_path_current, mod_file.source_code)

                # Save old source code
                if mod_file.change_type != ModificationType.ADD:
                    file_path_previous = Path(
                        proj_paths.get_path_to_cache_previous() + str(mod_file._new_path))
                    save_source_code(file_path_previous,
                                     mod_file.source_code_before)

                # Create sourcediff directory
                file_path_sourcediff = Path(
                    proj_paths.get_path_to_cache_sourcediff() + str(mod_file._new_path))
                if not os.path.exists(str(file_path_sourcediff.parent)):
                    os.makedirs(str(file_path_sourcediff.parent))

                # Create sourcediff file
                """
                if mod_file.change_type != ModificationType.ADD:
                    save_source_code_diff_file(
                        file_path_previous, file_path_current, file_path_sourcediff)
                else:
                    # adds new nodes, edges to the db
                    save_new_file_data(file_path_current)
                """

                # Save file imports
                fis = get_file_imports(mod_file.source_code, mod_file_data)
                logging.debug("File imports: ",fis)

                # Execute the jar for finding the source differences
                args = [proj_config.get_path_to_src_diff_jar(
                ), file_path_previous.__str__(), 'TRUE']
                result = _jarWrapper(*args)

                # convert to string -> xml
                diff_xml_results = b''.join(result).decode('utf-8')
                diff_data_xml = BeautifulSoup(diff_xml_results, "xml")

                parse_xml_diffs(diff_data_xml)

                # Save method/function call change info
                # ggg save_method_call_change_info(file_path_sourcediff)

                # Save method function change in db
                source_node = 'TBD'
                target_node = 'TBD'
                """
                save_source_change_row (
                    commit.hash, str(commit.author_date), str(mod_file._new_path), 
                    source_node, target_node, commit.author.name
                )
                """
                """
                print('Nloc:', mod_file.nloc)
                print('---------------------------')
                print(mod_file.complexity)
                print('---------------------------')
                print(mod_file.token_count)
                print('---------------------------')
                """
                """
                for m in mod_file.methods:
                    print(m.name)
                    print(m.parameters)
                    print(m.fan_in)
                    print(m.fan_out)
                    print(m.general_fan_out)
                """
                logging.debug('---------------------------')
                # print(mod_file.methods_before)
                break


# %%
