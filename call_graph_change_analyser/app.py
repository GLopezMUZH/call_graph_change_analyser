# %%
from models import *
import logging
from datetime import datetime
import sys

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from repository_mining import load_source_repository_data
from utils_sql import create_db_tables
from project_configs import execute_project_conf_JKQtPlotter, execute_project_conf_PX4, execute_project_conf_Glucosio

from call_graph_analysis import get_call_graph, print_graph_stats


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
        proj_config, proj_paths = execute_project_conf_JKQtPlotter(from_tag=from_tag, to_tag=to_tag, save_cache_files=True)
    elif p_name == 'PX4-Autopilot':
        proj_config, proj_paths = execute_project_conf_PX4(from_tag, to_tag)
    elif p_name == 'glucosio':
        proj_config, proj_paths = execute_project_conf_Glucosio(from_tag=from_tag, to_tag=to_tag, save_cache_files=True)

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    if '-init_db_yes' in args:
        init_db(proj_paths)

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))


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

