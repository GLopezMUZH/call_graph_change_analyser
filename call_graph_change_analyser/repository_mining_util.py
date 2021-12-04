# %%
import os
import subprocess
from subprocess import *
from typing import Optional, Tuple, List
import logging

from pathlib import Path
from importlib import reload
from pydriller import *
from bs4 import BeautifulSoup

from models import *
import models
from models import CallCommitInfo, ProjectPaths, ProjectConfig, FileData, FileImport
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
                f_name, f_path, f_dir_path = get_import_file_data(mod_file_data.get_file_dir_path() , code_line)

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


# from subprocess import *

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
            logging.debug("Action node type: {0}".format(str(action_node_type)))
            ac = utils_py.get_action_class(an.actionClassName.get_text())
            logging.debug("Action class: {0}, ac: {1} ".format(an.actionClassName.get_text(), str(ac)))
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
    except Exception as exceptionMsg:
        logging.error(exceptionMsg)
        print(exceptionMsg)
    return r


# %%
def parse_mod_file(mod_file, proj_paths: ProjectPaths,
                   proj_config: ProjectConfig) -> Tuple[List[FileImport], List[CallCommitInfo]]:
    logging.debug('---------------------------')
    logging.debug(mod_file.change_type)
    logging.debug(str(mod_file._new_path))
    logging.debug(mod_file._old_path)
    ccis = []
    fis = []

    mod_file_data = FileData(str(mod_file._new_path))

    # Save new source code
    file_path_current = os.path.join(proj_paths.get_path_to_cache_current(), str(mod_file._new_path))
    save_source_code(file_path_current, mod_file.source_code)

    # Save old source code
    if mod_file.change_type != ModificationType.ADD:
        file_path_previous = os.path.join(proj_paths.get_path_to_cache_previous(), str(mod_file._new_path))
        save_source_code(file_path_previous,
                         mod_file.source_code_before)

    # Create sourcediff directory
    if mod_file.change_type != ModificationType.ADD:
        file_path_sourcediff = os.path.join(proj_paths.get_path_to_cache_sourcediff(), str(mod_file._new_path))
        if not os.path.exists(os.path.dirname(file_path_sourcediff)):
            os.makedirs(os.path.dirname(file_path_sourcediff))

    # Create sourcediff file: not currently because relevant differences files are created in jar
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
    logging.debug("File imports len: {0}".format(len(fis)))

    # Execute the jar for finding the relevant source differences (function/method call changes)
    if mod_file.change_type != ModificationType.ADD:
        args = [proj_config.get_path_to_src_diff_jar(
        ), file_path_previous.__str__(), 'TRUE']
        result = _jarWrapper(*args)

        # convert to string -> xml
        diff_xml_results = b''.join(result).decode('utf-8')
        diff_data_xml = BeautifulSoup(diff_xml_results, "xml")

        ccis = parse_xml_call_diffs(
            diff_data_xml, proj_paths.get_path_to_cache_current(), mod_file_data)

    else:
        print("")
        logging.debug("ADD file")

    # Delete temporary files after processing
    if proj_config.get_delete_cache_files():
        if os.path.isfile(file_path_current):
            os.remove(file_path_current)
        else:
            print("Error: %s file not found" % file_path_current)
            logging.error("Error: %s file not found" % file_path_current)

        if mod_file.change_type != ModificationType.ADD:
            if os.path.isfile(file_path_previous):
                os.remove(file_path_previous)
            else:
                print("Error: %s file not found" % file_path_previous)
                logging.error("Error: %s file not found" % file_path_previous)

        """
        if mod_file.change_type != ModificationType.ADD:
            if os.path.isfile(file_path_sourcediff):
                os.remove(file_path_sourcediff)
            else:    ## Show an error ##
                print("Error: %s file not found" % file_path_sourcediff)
                logging.error("Error: %s file not found" % file_path_sourcediff)
        """

    logging.debug('---------------------------')
    return (fis, ccis)


def process_file_commit(proj_config, proj_paths, commit: Commit, mod_file: ModifiedFile):
    mod_file_data = FileData(str(mod_file._new_path))

    # file_commit
    insert_file_commit(proj_paths.get_path_to_project_db(), mod_file_data=mod_file_data,
                       commit_hash=commit.hash, commit_commiter_datetime=commit.committer_date,
                       commit_file_name=mod_file.filename,
                       commit_new_path=mod_file.new_path, commit_old_path=mod_file.old_path,
                       change_type=mod_file.change_type)

    # function_commit
    insert_function_commit(
        proj_paths.get_path_to_project_db(), mod_file, commit)

    # get previous_function_to_file
    previous_functions_in_file = get_previous_functions_in_file(proj_paths.get_path_to_project_db(), mod_file)

    # function_to_file
    update_function_to_file(proj_paths.get_path_to_project_db(), mod_file, commit, previous_functions_in_file)

    # file_imports
    fis, ccis = parse_mod_file(mod_file, proj_paths, proj_config)
    update_file_imports(mod_file_data, fis,
                        proj_paths.get_path_to_project_db(),
                        commit_hash=commit.hash,
                        commit_datetime=str(commit.committer_date))

    # call_commits
    update_call_commits(ccis,
                        proj_paths.get_path_to_project_db(),
                        commit_hash_start=commit.hash,
                        commit_start_datetime=str(commit.committer_date))


def traverse_all(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True, only_in_branch='master').traverse_commits():

        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_commit(proj_config, proj_paths, commit, mod_file)


def traverse_on_dates(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            since=proj_config.get_start_repo_date(),
            to=proj_config.get_end_repo_date(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True, only_in_branch='master').traverse_commits():

        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_commit(proj_config, proj_paths, commit, mod_file)


def traverse_on_tags(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            from_tag=proj_config.get_repo_from_tag(),
            to_tag=proj_config.get_repo_to_tag(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True, only_in_branch='master').traverse_commits():

        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_commit(proj_config, proj_paths, commit, mod_file)


                # Save method function change in db
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



# %%
def load_source_repository_data(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    logging.debug('Start load_source_repository_data')
    logging.debug(proj_config.get_path_to_repo())
    logging.debug(proj_config.get_commit_file_types())

    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)

    for commit in Repository('https://github.com/jkriege2/JKQtPlotter.git',
                             single='fc321f027ba5741de1be56bdee4379155647385a',
                             only_no_merge=True,
                             only_in_branch='master').traverse_commits():
        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_commit(proj_config, proj_paths, commit, mod_file)
    """
    if proj_config.get_start_repo_date() is not None:
        logging.debug(proj_config.get_start_repo_date())
        logging.debug(proj_config.get_start_repo_date().tzinfo)
        logging.debug(proj_config.get_end_repo_date())
        traverse_on_dates(proj_config, proj_paths)
    elif proj_config.get_repo_from_tag() is not None:
        logging.debug(proj_config.get_repo_from_tag())
        logging.debug(proj_config.get_repo_to_tag())
        traverse_on_tags(proj_config, proj_paths)
    else:
        traverse_all(proj_config, proj_paths)
    """