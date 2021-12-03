# %%
from models import *
import models
import logging
from datetime import datetime
from importlib import reload
import sys

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from gumtree_difffile_parser import get_method_call_change_info_cpp
from repository_mining_util import load_source_repository_data
from utils_sql import create_db_tables
from utils_py import replace_timezone
from call_graph_analysis import get_call_graph, print_graph_stats


# %%
import repository_mining_util
reload(repository_mining_util)
from repository_mining_util import save_source_code

import models
reload(models)
from models import CallCommitInfo, ProjectPaths, FileData, FileImport

# %%
def main():
    print('Started App ------------ ', datetime.now())
    proj_config, proj_paths = execute_project_conf_JKQtPlotter()
    logging.info('Started App ---------- ', datetime.now())

    args = sys.argv[1:]

    if len(args) == 1 and args[0] == '-init_db_yes':
        logging.info('Initialize the db.')    
        init_db()

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- ', datetime.now())
    print('Finished App -------------', datetime.now())



def execute_project_conf_PX4():
    path_to_cache_dir = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\'
    proj_name = 'PX4-Autopilot'
    log_filepath = path_to_cache_dir+proj_name+'\\app.log'

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.info('Started App - ', datetime.now())

    # source trail db 9.10.2021
    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    from_tag = 'v1.12.0'
    to_tag = 'v1.12.3'

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar='..\\resources\\astChangeAnalyzer_0_1_cpp.jar',
                                path_to_repo='https://github.com/PX4/PX4-Autopilot.git',
                                start_repo_date=st_date,
                                end_repo_date=end_date,
                                delete_cache_files=False,
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag
                                )
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='C:\\Users\\lopm\\Documents\\mt\\sandbox\\projects\\',
                              path_to_git_folder='C:\\Users\\lopm\\Documents\\gitprojects\\' + proj_config.proj_name + '\\')
                              
    return proj_config,proj_paths


def execute_project_conf_JKQtPlotter():
    path_to_cache_dir = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\'
    proj_name = 'JKQtPlotter'
    log_filepath = path_to_cache_dir+proj_name+'\\app.log'
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - ', str(datetime.now()))

    from_tag = 'v2019.11.0'
    to_tag = 'v2019.11.1'

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar='..\\resources\\astChangeAnalyzer_0_1_cpp.jar',
                                path_to_repo='https://github.com/jkriege2/JKQtPlotter.git',
                                delete_cache_files=False)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='C:\\Users\\lopm\\Documents\\mt\\sandbox\\projects\\',
                              path_to_git_folder='C:\\Users\\lopm\\Documents\\gitprojects\\' + proj_config.proj_name + '\\')

    logging.debug(proj_config)
    logging.debug(proj_paths)                              
    return proj_config,proj_paths

#%%
def init_db():
    # INITIALIZE DATABASE ------------------------------
    proj_config, proj_paths = execute_project_conf_JKQtPlotter()
    create_db_tables(proj_paths, drop=True)


#%%
if __name__ == '__main__':
    main()





# %%
#initate_analytics_db(proj_paths, drop=True, load_init_graph=True)
#clone_git_source(path_to_git_folder, path_to_git)

# %%
# only the graph part
#G = get_call_graph(proj_paths)
# print_graph_stats(G)


# proj_name = 'PX4-Autopilot' # 'glucosio-android'
# proj_lang = 'cpp' # 'cpp' 'python' 'java'
#path_to_repo = 'https://github.com/PX4/PX4-Autopilot.git'
# path_to_git = 'https://github.com/ishepard/pydriller.git' #'git@github.com:ishepard/pydriller.git/'

# start_repo_date = datetime(2021, 10, 1, 0, 1, 0)  #(2018, 4, 1, 0, 1, 0)

# 'https://github.com/ishepard/pydriller.git'
# 'https://github.com/PX4/PX4-Autopilot.git'
# 'https://github.com/Glucosio/glucosio-android.git'


# %%
