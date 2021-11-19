# %%
import os
import subprocess
from models import *
import models
from pathlib import Path
from imp import reload

from pydriller import *

from models import MethodCallChangeInfo, ProjectPaths, ProjectConfig
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
    xml_filename = file_path + ".xml"
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


#from subprocess import *

def jarWrapper(*args):
    process = Popen(['java', '-jar']+list(args), stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith('\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split('\n')
    if stderr != '':
        ret += stderr.split('\n')
    ret.remove('')
    return ret


# %%
def load_source_repository_data(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)

    """
    if proj_config.get_end_repo_date == None:
        repository_generator = Repository(
                path_to_repo=proj_config.get_path_to_repo(),
                since=proj_config.get_start_repo_date).traverse_commits()
                #only_modifications_with_file_types=proj_config.get_commit_file_types
    else:
        repository_generator = Repository(
                path_to_repo=proj_config.get_path_to_repo(),
                since=proj_config.get_start_repo_date,
                to=proj_config.get_end_repo_date()).traverse_commits()
    """
    # default is order='reverse'
    for commit in Repository(
                path_to_repo=proj_config.get_path_to_repo(),
                since=proj_config.get_start_repo_date,
                to=proj_config.get_end_repo_date()).traverse_commits():
        for mod_file in commit.modified_files:
            # print('Extension: ', str(mod_file._new_path)[-3:])
            if (is_valid_file_type(str(mod_file._new_path))):
                print('---------------------------')
                print(mod_file.change_type)
                print(str(mod_file._new_path))
                print(mod_file._old_path)
                # print(mod_file._new_path)
                # print(mod_file.diff)

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

                # Any number of args to be passed to the jar file
                args = [proj_config.get_path_to_src_diff_jar, file_path_previous]
                result = jarWrapper(*args)
                print(result)

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

                print('Nloc:', mod_file.nloc)
                print('---------------------------')
                print(mod_file.complexity)
                print('---------------------------')
                print(mod_file.token_count)
                print('---------------------------')
                """
                for m in mod_file.methods:
                    print(m.name)
                    print(m.parameters)
                    print(m.fan_in)
                    print(m.fan_out)
                    print(m.general_fan_out)
                """
                print('---------------------------')
                # print(mod_file.methods_before)
                break


# %%
