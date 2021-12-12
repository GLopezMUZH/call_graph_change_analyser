# %%
from models import *
import models
import logging
from datetime import datetime
import sys, os
from importlib import reload

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from repository_mining import load_source_repository_data
from utils_sql import create_db_tables
from utils_py import replace_timezone
from project_configs import execute_project_conf_JKQtPlotter,execute_project_conf_Glucosio

from call_graph_analysis import get_call_graph, print_graph_stats

# %%
def main():
    print('Started App ------------ {0}'.format(datetime.now()))
    #proj_config, proj_paths = execute_project_conf_example_project()
    #proj_config, proj_paths = execute_project_conf_JKQtPlotter(from_tag='v2019.11.0', to_tag='v2019.11.3')
    proj_config, proj_paths = execute_project_conf_Glucosio(from_tag='1.2.1', to_tag='1.3.0', save_cache_files=True)
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    init_db(proj_paths)

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App ------------- {0}'.format(datetime.now()))


def init_db(proj_paths):
    logging.info('Initialize the db.')    
    create_db_tables(proj_paths, drop=True)

#%%
if __name__ == '__main__':
    main()



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



# %%
#initate_analytics_db(proj_paths, drop=True, load_init_graph=True)

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
