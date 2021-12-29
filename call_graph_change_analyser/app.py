# %%
from models import *
import logging
from datetime import datetime
import sys

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from repository_mining import load_source_repository_data
from utils_sql import create_db_tables
from project_configs import *

from initial_indexing import execute_intitial_indexing, download_initial_cache_source
from call_graph_analysis import get_call_graph, print_graph_stats


# %%
def main():
    """
    since_date format '12-11-2019'
    """
    print('Started App ------------ {0}'.format(datetime.now()))

    exists_from_tag = False
    exists_to_tag = False
    exists_since_date = False
    exists_to_tag = False

    from_tag = None
    to_tag = None
    since_date = None
    to_date = None

    args = sys.argv[1:]

    # argument format -P proj_name -from_tag tag -to_tag tag
    if '-C' in args:
        f_idx = args.index("-C")
        path_to_config_file = args[f_idx+1]
        proj_config, proj_paths = execute_project_conf_from_file(
            path_to_config_file)
    else:

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
            exists_from_tag = True

        if '-to_tag' in args:
            tt_idx = args.index("-to_tag")
            to_tag = args[tt_idx+1]
            print(to_tag)
            exists_to_tag = True

        if '-since_date' in args:
            ds_idx = args.index("-since_date")
            since_date = datetime.strptime(args[ds_idx+1], '%d-%m-%Y')
            print(from_tag)
            exists_since_date = True

        if '-to_date' in args:
            dt_idx = args.index("-to_date")
            to_date = datetime.strptime(args[dt_idx+1], '%d-%m-%Y')
            print(to_tag)
            exists_to_date = True

        # dates must be set
        """
        if not((exists_from_tag and exists_to_tag) or (exists_since_date and exists_to_date) or (exists_since_date)):
            err_msg = "ERROR. Currently required either[-from_tag X -to_tag Y] or [-since_date dd-mm-yyyy -to_date dd-mm-yyyy] arguments"
            raise Exception(err_msg)
        """

        if p_name == 'JKQtPlotter':
            proj_config, proj_paths = execute_project_default_conf_JKQtPlotter(
                from_tag=from_tag, to_tag=to_tag, since_date=since_date, to_date=to_date, save_cache_files=True)
        elif p_name == 'PX4-Autopilot':
            proj_config, proj_paths = execute_project_default_conf_PX4(
                from_tag=from_tag, to_tag=to_tag, since_date=since_date, to_date=to_date, save_cache_files=True)
        elif p_name == 'glucosio':
            proj_config, proj_paths = execute_project_default_conf_Glucosio(
                from_tag=from_tag, to_tag=to_tag, since_date=since_date, to_date=to_date, save_cache_files=True)
        elif p_name == 'OpenBot':
            proj_config, proj_paths = execute_project_default_conf_OpenBot(
                from_tag=from_tag, to_tag=to_tag, since_date=since_date, to_date=to_date, save_cache_files=True)
        elif p_name == 'EConcierge':
            proj_config, proj_paths = execute_project_default_conf_EConcierge(
                from_tag=from_tag, to_tag=to_tag, since_date=since_date, to_date=to_date, save_cache_files=True)
        elif p_name == 'GRIP':
            proj_config, proj_paths = execute_project_default_conf_GRIP(
                from_tag=from_tag, to_tag=to_tag, since_date=since_date, to_date=to_date, save_cache_files=True)

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    if '-init_db_yes' in args:
        init_db(proj_paths)

    #if '-init_index_yes' in args:
    download_initial_cache_source(proj_config.get_repo_url(), proj_paths.get_path_to_cache_src_dir())
    execute_intitial_indexing(proj_paths)

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))


def init_db(proj_paths):
    logging.info('Initialize the db.')
    create_db_tables(proj_paths, drop=True)


# %%
if __name__ == '__main__':
    main()

# %%
# init_db()

# %%
#initate_analytics_db(proj_paths, drop=True, load_init_graph=True)

# %%
# only the graph part
#G = get_call_graph(proj_paths)
# print_graph_stats(G)
