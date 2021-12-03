# %%
from models import *
import models
import logging
from datetime import datetime
import sys

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from gumtree_difffile_parser import get_method_call_change_info_cpp
from repository_mining_util import load_source_repository_data
from utils_sql import create_db_tables
from utils_py import replace_timezone
from call_graph_analysis import get_call_graph, print_graph_stats

# %%
def main():
    print('Started App ------------ ', datetime.now())
    proj_config, proj_paths = execute_project_conf_example_project()
    logging.info('Started App ---------- ', datetime.now())

    args = sys.argv[1:]
    print[args[0]]

    if len(args) == 1 and args[0] == '-init_db_yes':
        logging.info('Initialize the db.')    
        init_db()

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- ', datetime.now())
    print('Finished App -------------', datetime.now())


def execute_project_conf_example_project():
    path_to_cache_dir = '../tests/cache/'
    proj_name = 'example_project'
    log_filepath = path_to_cache_dir+proj_name+'/app.log'

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
                                path_to_src_diff_jar='../resources/astChangeAnalyzer_0_1_cpp.jar',
                                path_to_repo='',
                                start_repo_date=st_date,
                                end_repo_date=end_date,
                                delete_cache_files=False)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='../tests/projects_data/',  # TODO verify
                              path_to_git_folder='../tests/cache/gitprojects/' + proj_config.proj_name + '/')

    return proj_config, proj_paths

#%%
def init_db():
    # INITIALIZE DATABASE ------------------------------
    proj_config, proj_paths = execute_project_conf_example_project()
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
