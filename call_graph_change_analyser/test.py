# %%
#import pydriller
from pydriller.domain.commit import ModifiedFile
import pytest
from bs4 import BeautifulSoup


from utils_sql import create_commit_based_tables, update_file_imports
import utils_sql
from models import CallCommitInfo, ProjectPaths, FileData, FileImport
from repository_mining_util import load_source_repository_data, get_file_imports, parse_xml_diffs, parse_mod_file, process_file_commit
import gumtree_difffile_parser
from models import *
import models
from gumtree_difffile_parser import get_method_call_change_info_cpp
from imp import reload
from pydriller import *
from datetime import datetime
import logging


from utils_py import replace_timezone


# %%
for commit in Repository("https://github.com/PX4/PX4-Autopilot.git", since=datetime(2021, 11, 15, 0, 1, 0, 79043)).traverse_commits():
    print(commit.author_date)


# %%

# %%
reload(models)

# %%
reload(gumtree_difffile_parser)


# %%
mcci = get_method_call_change_info_cpp(
    'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\PX4-Autopilot_textdiff\\sourcediff\\src\\drivers\\camera_trigger\\camera_trigger.cpp')

# %%
print(str(mcci))
print(mcci.__str__)
print("Src node: %s, bla", mcci.source_node, "sjdhf")

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

r = parse_xml_diffs(diff_data_xml, path_to_cache_current=, mod_file_data=mod_file_data)

for cci in r:
    print(cci)


# %%
cci = CallCommitInfo(
    'f_name_TEST', 'parent_function_name_TEST', 'call_node_name_TEST')
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

    path_to_cache_dir = '..\\tests\\cache\\'
    proj_name = 'example_project'
    log_filepath = path_to_cache_dir+proj_name+'\\app.log'

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s %(levelname)-8s %(message)s')
    logging.info('Started App - ' + str(datetime.now()))

    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar='..\\resources\\astChangeAnalyzer_0_1_cpp.jar',
                                path_to_repo='',
                                start_repo_date=st_date,
                                end_repo_date=end_date)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='..\\tests\\projects_data\\',  # TODO verify
                              path_to_git_folder='..\\tests\\cache\\gitprojects\\' + proj_config.proj_name + '\\')

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

    fis, ccis = parse_mod_file(mod_file, proj_paths, proj_config)
    for fi in fis:
        print(fi)
    for cc in ccis:
        print(cc)

test_parse_model_file()


# %%
def test_update_file_imports():
    test_path_to_project_db = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\projects\\PX4-Autopilot\\PX4-Autopilot_analytics.db'
    commit_hash_start = 'hash_blabla'
    commit_start_datetime='20211129'

    file_path = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\PX4-Autopilot\\current\\src\\drivers\\uavcannode\\UavcanNode.cpp'
    file_contents = ''
    with open(file_path, "r") as f:
        file_contents = f.read()

    file_data = FileData(file_path)
    print(file_data)

    fis = get_file_imports(source_code=file_contents, mod_file_data=file_data)
    update_file_imports(fis,
                        test_path_to_project_db,
                        commit_hash_start=commit_hash_start,
                        commit_start_datetime=commit_start_datetime)

test_update_file_imports()


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


# %%
import utils_sql
reload(utils_sql)
from utils_sql import update_file_imports, insert_or_update_file_import

import models
reload(models)
from models import CallCommitInfo, ProjectPaths, FileData, FileImport

import repository_mining_util
reload(repository_mining_util)
from repository_mining_util import process_file_commit

# %%
def test_process_file_commit():

    path_to_cache_dir = '..\\tests\\cache\\'
    proj_name = 'example_project'
    log_filepath = path_to_cache_dir+proj_name+'\\app.log'

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s %(levelname)-8s %(message)s')
    logging.info('Started App - ' + str(datetime.now()))

    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar='..\\resources\\astChangeAnalyzer_0_1_cpp.jar',
                                path_to_repo='',
                                start_repo_date=st_date,
                                end_repo_date=end_date)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='..\\tests\\projects_data\\',  # TODO verify
                              path_to_git_folder='..\\tests\\cache\\gitprojects\\' + proj_config.proj_name + '\\')

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

    class PeudoCommit():
        def __init__(self, hash, committer_date) -> None:
            self.hash = hash
            self.committer_date = committer_date
    

    commit = PeudoCommit('hash_test_process_file_commit','211130')
    process_file_commit(proj_config, proj_paths, PeudoCommit, mod_file)


test_process_file_commit()
# %%
