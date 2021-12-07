# %%
from models import *
import models
import logging
from datetime import datetime
from importlib import reload
import sys, os

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
    print('Started App ------------ {0}'.format(datetime.now()))

    args = sys.argv[1:]

    # argument format -P proj_name -from_tag tag -to_tag tag
    if '-P' in args:
        p_idx = args.index("-P")
        p_name = args[p_idx+1]
        print(p_name)
    else:
        err_msg = "ERROR. Project argument is required: -P [JKQtPlotter or PX4-Autopilot] "
        raise Exception(err_msg)

    if '-from_tag' in args:
        tf_idx = args.index("-from_tag")
        from_tag = args[tf_idx+1]
        print(from_tag)
    else: 
        err_msg = "ERROR. Currently required -from_tag X -to_tag Y arguments"
        raise Exception(err_msg)

    if '-to_tag' in args:
        tt_idx = args.index("-to_tag")
        to_tag = args[tt_idx+1]
        print(to_tag)
    else: 
        err_msg = "ERROR. Currently required -from_tag X -to_tag Y arguments"
        raise Exception(err_msg)

    if p_name == 'JKQtPlotter':
        proj_config, proj_paths = execute_project_conf_JKQtPlotter(from_tag, to_tag)
    elif p_name == 'PX4-Autopilot':
        proj_config, proj_paths = execute_project_conf_PX4(from_tag, to_tag)

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    if '-init_db_yes' in args:
        init_db(proj_paths)

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))



def execute_project_conf_PX4(from_tag: str, to_tag: str, delete_cache_files: bool = False):
    #from_tag = 'v1.12.0'
    #to_tag = 'v1.12.3'
  
    proj_name = 'PX4-Autopilot'
    path_to_proj_data_dir=os.path.normpath('../project_results/')

    # source trail db 9.10.2021
    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar=os.path.normpath('../resources/astChangeAnalyzer_0_1_cpp.jar'),
                                path_to_repo='https://github.com/PX4/PX4-Autopilot.git',
                                repo_type='Git',
                                #start_repo_date=st_date,
                                #end_repo_date=end_date,
                                delete_cache_files=delete_cache_files,
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag
                                )
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), proj_name, 'app.log')

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.info('Started App - {0}'.format(datetime.now()))


    return proj_config,proj_paths


def execute_project_conf_JKQtPlotter(from_tag: str, to_tag: str, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'JKQtPlotter'
    path_to_proj_data_dir=os.path.normpath('../project_results/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_src_diff_jar=os.path.normpath('../resources/astChangeAnalyzer_0_1_cpp.jar'),
                                path_to_repo='https://github.com/jkriege2/JKQtPlotter.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)                              
    return proj_config,proj_paths


def init_db(proj_paths):
    logging.info('Initialize the db.')    
    create_db_tables(proj_paths, drop=True)


#%%
if __name__ == '__main__':
    main()

#%%
#init_db()

# %%
#initate_analytics_db(proj_paths, drop=True, load_init_graph=True)

# %%
# only the graph part
#G = get_call_graph(proj_paths)
# print_graph_stats(G)

