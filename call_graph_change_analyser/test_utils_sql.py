# %%
import pytest
import logging
from bs4 import BeautifulSoup
from imp import reload
from datetime import datetime
from git import Commit as GitCommit

from pydriller import *
from pydriller.domain.commit import ModifiedFile

from models import ProjectPaths, ProjectConfig, CallCommitInfo,  FileData, FileImport

from utils_sql import create_commit_based_tables, update_file_imports, create_db_tables, insert_git_commit
from utils_py import replace_timezone

# %%
def execute_project_conf_example_project():
    path_to_cache_dir = '..\\tests\\cache\\'
    proj_name = 'example_project'
    log_filepath = path_to_cache_dir+proj_name+'\\app.log'

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
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
                                end_repo_date=end_date,
                                delete_cache_files=False)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='..\\tests\\projects_data\\',  # TODO verify
                              path_to_git_folder='..\\tests\\cache\\gitprojects\\' + proj_config.proj_name + '\\')

    return proj_config, proj_paths

proj_config, proj_paths = execute_project_conf_example_project()


# %%
# INITIALIZE DATABASE ------------------------------
create_db_tables(proj_paths, drop=True)
#create_commit_based_tables(proj_paths.get_path_to_project_db(), drop=True)


# %%
insert_git_commit(proj_paths.get_path_to_project_db(),
                  commit_hash='GitCommit.NULL_BIN_SHA000000000000000000',
                  commit_commiter_datetime=str(datetime(2021, 11, 19, 0, 1, 0, 79043)),
                  author='GGG', in_main_branch=1,
                  merge=0, nr_modified_files=5,
                  nr_deletions=8, nr_insertions=4, nr_lines=12)

# %%
