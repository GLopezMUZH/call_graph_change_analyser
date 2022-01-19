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

# %%
def main():
    path_to_db_file = os.path.normpath(
        '..\project_results\glucosio-android\.cache\callgraphdb\glucosio-android_raw_cg.db')
    path_to_config_file = os.path.normpath('..\project_config\glucosio_small.pconfig')

    os.path.exists(path_to_config_file)
    os.path.exists(path_to_db_file)

    proj_config, proj_paths = execute_project_conf_from_file(
        str(path_to_config_file))

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    if True: #'-init_db_yes' in args:
        init_db(proj_paths)

    # if '-init_index_yes' in args:
    download_initial_cache_source(proj_config.get_repo_url(
    ), proj_paths.get_path_to_cache_src_dir(), proj_config.get_only_in_branch())
    execute_intitial_indexing(proj_paths)

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))


def init_db(proj_paths):
    #logging.info('Initialize the db.')
    create_db_tables(proj_paths, drop=True)


# %%
if __name__ == '__main__':
    main()
