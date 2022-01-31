# %%
from project_configs import execute_project_conf_from_file
import logging
from datetime import datetime
import sys

from git_util import download_initial_cache_source
from initial_indexing import execute_intitial_indexing
from repository_mining import analyse_source_repository_data
from call_graph_parsing_util import calculate_cg_diffs
from cg_to_commit_util import update_commit_changes_to_cg_nodes
from utils_sql import create_db_tables
from cg_change_coupling_util import save_cg_change_coupling


# error messages
INVALID_PATH_MSG = "Error: Invalid file path/name. Path %s does not exist."


def main():
    """
    since_date format '12-11-2019'
    """
    print('Started App ------------ {0}'.format(datetime.now()))

    args = sys.argv[1:]

    # argument format -P proj_name -from_tag tag -to_tag tag
    if '-C' in args:
        f_idx = args.index("-C")
        path_to_config_file = args[f_idx+1]
        proj_config, proj_paths = execute_project_conf_from_file(
            path_to_config_file)
    else:
        raise("Configuration file is mandatory. -C path")

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    if '-not_init_db_yes' in args:
        logging.info('Not re-initialized database...')
    else:
        init_db(proj_paths)

    #if '-init_index_yes' in args:
    download_initial_cache_source(proj_config.get_repo_url(), proj_paths.get_path_to_cache_src_dir(), proj_config.get_only_in_branch())
    execute_intitial_indexing(proj_paths)

    analyse_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    calculate_cg_diffs(proj_config=proj_config, proj_paths=proj_paths)

    update_commit_changes_to_cg_nodes(proj_config=proj_config, proj_paths=proj_paths)

    save_cg_change_coupling(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))


def init_db(proj_paths):
    logging.info('Initialize the db.')
    create_db_tables(proj_paths, drop=True)


# %%
if __name__ == '__main__':
    main()