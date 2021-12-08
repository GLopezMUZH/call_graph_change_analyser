# %%
#import pydriller
import os
import pytest
import time
import logging
from bs4 import BeautifulSoup
from importlib import reload
from datetime import datetime

from pydriller import *
from pydriller.domain.commit import ModifiedFile

from models import CallCommitInfo, ProjectPaths, ProjectConfig, FileData, FileImport
from repository_mining import load_source_repository_data, get_file_imports, parse_xml_call_diffs, parse_mod_file_git, process_file_git_commit, get_import_file_data

from utils_sql import *
from utils_py import replace_timezone


# %%
def execute_project_conf_example_project():
    proj_name = 'example_project'
    path_to_proj_data_dir=os.path.normpath('../tests/project_results/')

    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar=os.path.normpath('../resources/astChangeAnalyzer_0_1_cpp.jar'),
                                path_to_repo='',
                                repo_type='Git',
                                start_repo_date=st_date,
                                end_repo_date=end_date,
                                delete_cache_files=False)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), proj_name, 'app.log')

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.info('Started App - {0}'.format(str(datetime.now())))

    return proj_config, proj_paths



# %%
raw = """animal
    carnivorous
        tiger
        lion
    vegetarian
        cow
        sheep
plant
    algea
    tree
        leaf
        pine
    fungus
        good
        bad
            evil
            mean
    cactus
        big
        small"""


raw = """expr_stmt [9364,9408]
        expr [9364,9407]
            call [9364,9407]
                name [9364,9384]
                    name: _subscriber_list [9364,9380]
                    operator: . [9380,9381]
                    name: add [9381,9384]
                argument_list [9384,9407]
                    argument [9385,9406]
                        expr [9385,9406]
                            operator: new [9385,9388]
                            call [9389,9406]
                                name: RTCMStream [9389,9399]
                                argument_list [9399,9406]
                                    argument [9400,9405]
                                        expr [9400,9405]
                                            name: _node [9400,9405]
    to
    block_content [8305,10426]
    at 17"""

raw = """else [9181,9268]
    block [9186,9268]
        block_content [9191,9264]
            expr_stmt [9191,9264]
                expr [9191,9263]
                    name: _trigger_pub [9191,9203]
                    operator: = [9204,9205]
                    call [9206,9263]
                        name: orb_advertise [9206,9219]
                        argument_list [9219,9263]
                            argument [9220,9252]
                                expr [9220,9252]
                                    call [9220,9252]
                                        name: ORB_ID [9220,9226]
                                        argument_list [9226,9252]
                                            argument [9227,9251]
                                                expr [9227,9251]
                                                    name: camera_trigger_secondary [9227,9251]
                            argument [9254,9262]
                                expr [9254,9262]
                                    operator: & [9254,9255]
                                    name: trigger [9255,9262]"""


# %%
lines = raw.split('\n')
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


# %%
# direct case, name is direct element, tabbed, from call
calls = [(x, y, z) for x, y, z in indents if z == 'call ']
call_next_indents = [y+1 for x, y, z in indents if z == 'call ']
call_names = [z[6:len(z)].strip() for x, y, z in indents if (
    z[0:5] == 'name:' and y in call_next_indents)]


# %%
stack = [indents[0]]
entries = [indents[0]]

prev_indent = 0
for item in indents[1:]:
    print("#########################")
    id, indent, content = item
    diff = indent - prev_indent
    print(item)
    print("diff", diff, [a[2] for a in stack])

    if diff > 0:
        entries.append(item+(stack[-1][2],))
    elif diff < 0:
        # entries.append(item+(stack[-diff][2],))
        count = -diff
        while count > -1:
            stack.pop()
            count -= 1
        entries.append(item+(stack[-1][2],))
    elif diff == 0:
        stack.pop()
        entries.append(item+(stack[-1][2],))
    stack.append(item)
    prev_indent = entries[-1][1]

    print("result", entries[-1])
print("########################")


# %%
for a in entries:
    if len(a) == 3:
        continue
    ident, level, content, parent = a
    print(level*' '*4, content, '(', parent, ')')




# %%
file_path = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\PX4-Autopilot\\current\\src\\drivers\\uavcannode\\UavcanNode.cpp'
file_contents = ''
with open(file_path, "r") as f:
    file_contents = f.read()

#file_data = FileData('src\\drivers\\uavcannode\\UavcanNode.cpp')
file_data = FileData(file_path)
print(file_data)

fis = get_file_imports(source_code=file_contents, mod_file_data=file_data)
for fi in fis:
    print(fi.get_import_file_name())


# %%
file_path = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\PX4-Autopilot\\sourcediff\\src\\drivers\\uavcannode\\UavcanNode.cpp.txt'
#file_path = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\PX4-Autopilot\\sourcediff\\src\\modules\\mavlink\\mavlink_parameters.cpp.txt'
file_contents = ''
with open(file_path, "r") as f:
    file_contents = f.read()

diff_data_xml = BeautifulSoup(file_contents, "xml")

mod_file_data = FileData(file_path)

r = parse_xml_call_diffs(diff_data_xml, path_to_cache_current=None, mod_file_data=mod_file_data)

for cci in r:
    print(cci)


# %%
cci = CallCommitInfo(
    'f_name_TEST', 'parent_function_name_TEST', 'calling_function_name_TEST')
print(cci)

# %%
def test_filename():
    diff_and_sc = {
        'diff': '',
        'source_code': '',
        'source_code_before': ''
    }
    m1 = ModifiedFile('dspadini/pydriller/myfile.py',
                      'dspadini/pydriller/mynewfile.py',
                      ModificationType.ADD, diff_and_sc)
    m3 = ModifiedFile('dspadini/pydriller/myfile.py',
                      'dspadini/pydriller/mynewfile.py',
                      ModificationType.ADD, diff_and_sc)
    m2 = ModifiedFile('dspadini/pydriller/myfile.py',
                      None,
                      ModificationType.ADD, diff_and_sc)

    print(m1.filename == 'mynewfile.py')
    assert m2.filename == 'myfile.py'
    assert m1 != m2
    assert m3 == m1


test_filename()

# %%
def test_metrics_cpp():
    print('started')
    with open('../tests/example_project/current/UavcanNode.cpp') as f:
        sc = f.read()

    with open('../tests/example_project/previous/UavcanNode.cpp') as f:
        sp = f.read()

    diff_and_sc = {
        'diff': '',
        'source_code': sc,
        'source_code_before': sp
    }

    m1 = ModifiedFile('example_project/previous/UavcanNode.cpp',
                      "example_project/current/UavcanNode.cpp",
                      ModificationType.MODIFY, diff_and_sc)

    print(m1.filename == 'UavcanNode.cpp')
    print(m1.nloc)
    print(m1.token_count)
    print(m1.complexity)
    print(len(m1.methods))

    assert m1.filename == 'UavcanNode.cpp'
    assert m1.nloc == 378
    assert m1.token_count == 2335
    assert m1.complexity == 0

    assert len(m1.methods) == 0


test_metrics_cpp()


# %%
def test_parse_model_file():

    proj_name = 'example_project'
    path_to_proj_data_dir=os.path.normpath('../tests/project_results/')
        
    proj_config, proj_paths = execute_project_conf_example_project()

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), proj_name, 'app.log')

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.info('Started App - {0}'.format(str(datetime.now())))

    print(proj_config)
    print(proj_paths)

    print('started')
    with open('../tests/cache/example_project/current/UavcanNode.cpp') as f:
        sc = f.read()

    with open('../tests/cache/example_project/previous/UavcanNode.cpp') as f:
        sp = f.read()

    diff_and_sc = {
        'diff': '',
        'source_code': sc,
        'source_code_before': sp
    }

    mod_file = ModifiedFile('UavcanNode.cpp',
                            "UavcanNode.cpp",
                            ModificationType.MODIFY, diff_and_sc)

    ccis = parse_mod_file_git(mod_file, proj_paths, proj_config)
    for cc in ccis:
        print(cc)

test_parse_model_file()


# %%
def test_get_file_imports():
    file_path = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\PX4-Autopilot\\current\\src\\drivers\\uavcannode\\UavcanNode.cpp'
    file_contents = ''
    with open(file_path, "r") as f:
        file_contents = f.read()

    file_data = FileData(file_path)
    print(file_data)

    fis = get_file_imports(source_code=file_contents, mod_file_data=file_data)
    # TODO complete test_get_file_imports

test_get_file_imports()


# %%
import pandas
import sqlite3
def test_analytics_db():
    test_path_to_project_db = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\projects\\PX4-Autopilot\\PX4-Autopilot_analytics.db'
    con = sqlite3.connect(test_path_to_project_db)
    cur = con.cursor()
    sql_statement = """select * from file_import"""
    df = pandas.read_sql_query(sql_statement, con)
    print(df)

test_analytics_db()

#%%
from git import Commit as GitCommit,  Actor, Repo
from pydriller import Commit
import hashlib

def create_local_commit() -> Commit:
    repo = Repo('C:\\Users\\lopm\\Documents\\gitprojects\\call_graph_change_analyser')

    message = 'hash_test_process_file_git_commit message'

    tree = repo.index.write_tree()
    parents = [repo.head.commit]

    # Committer and Author
    actor = Actor("Gab", "Gab@testing.dev")
    cr = repo.config_reader()
    committer = Actor.committer(cr)
    author = Actor.author(cr)

    # Custom Date
    t = int(time.time())
    offset = time.altzone
    author_time, author_offset = t, offset
    committer_time, committer_offset = t, offset

    # UTF-8 Default
    conf_encoding = 'UTF-8'

    hash_obj = hashlib.sha1(b'Hello, Python!')

    comm = GitCommit(repo, GitCommit.NULL_BIN_SHA,  #hash_obj.digest(),  # Commit.NULL_BIN_SHA,
                tree,
                author, author_time, author_offset,
                committer, committer_time, committer_offset,
                message, parents, conf_encoding)


    print("Git Commit----")

    print(comm)
    print(comm.author)
    print(comm.hexsha)

    py_comm = Commit(comm, conf_encoding)

    print("PyDriller Commit--- ")
    print(py_comm.author)
    print(py_comm.author.name)
    print(str(py_comm.committer_date))
    #print(py_comm.in_main_branch)
    print(py_comm.merge)
    #print(py_comm.files)
    #print(len(py_comm.modified_files))
    #print(py_comm.deletions)
    #print(py_comm.insertions)
    #print(commit.lines)

    return py_comm


# %%
def test_process_file_git_commit():
    proj_config, proj_paths = execute_project_conf_example_project()

    print(proj_config)
    print(proj_paths)

    print('started')
    with open('../tests/cache/example_project/current/UavcanNode.cpp') as f:
        sc = f.read()

    with open('../tests/cache/example_project/previous/UavcanNode.cpp') as f:
        sp = f.read()

    diff_and_sc = {
        'diff': '',
        'source_code': sc,
        'source_code_before': sp
    }

    mfs = []
    mod_file1 = ModifiedFile('UavcanNode.cpp',
                            "UavcanNode.cpp",
                            ModificationType.MODIFY, diff_and_sc)
    mod_file2 = ModifiedFile('UavcanNode2.cpp',
                            "UavcanNode2.cpp",
                            ModificationType.MODIFY, diff_and_sc)
    mfs.append(mod_file1)
    mfs.append(mod_file2)

    local_commit = create_local_commit()
    print(local_commit)
    process_file_git_commit(proj_config, proj_paths, local_commit, mod_file1)


test_process_file_git_commit()


# %%
def test_is_valid_file_type():
    is_valid_file_type = get_file_type_validation_function('cpp')
    print(is_valid_file_type('lib\jkqtplotter\jkqtpcoordinateaxes.h'))
    print(is_valid_file_type('lib\jkqtplotter\jkqtpcoordinateaxes.cpp'))
    print(is_valid_file_type('lib\jkqtplotter\jkqtpcoordinateaxes.what'))

# %%
def test_get_import_file_data():
    mod_file_dir_path='lib/jkqtplotter/'
    cls=['#include <QSvgGenerator>',
        '#include <QDebug>',
        '#include "jkqtplotter/jkqtpbaseplotter.h"',
        '#include "jkqtplotter/gui/jkqtpgraphsmodel.h"',
        '#include "qftools.h"',
        '#include "jkqtplotter/graphs/jkqtpimpulses.h"        ']
    for code_line in cls:
        print(get_import_file_data(mod_file_dir_path, code_line))


test_get_import_file_data()


# %%
import utils_sql
reload(utils_sql)
from utils_sql import *

import models
reload(models)
from models import CallCommitInfo, ProjectPaths, FileData, FileImport

import repository_mining_util
reload(repository_mining_util)
from repository_mining_util import *