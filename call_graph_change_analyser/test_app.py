# %%
from models import *
import logging
from datetime import datetime
import sys

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from repository_mining import analyse_source_repository_data
from utils_sql import create_db_tables
from project_configs import *

from initial_indexing import execute_intitial_indexing
from git_util import download_initial_cache_source
from repository_mining import analyse_source_repository_data
from call_graph_parsing_util import calculate_cg_diffs
from cg_to_commit_util import update_commit_changes_to_cg_nodes
from utils_sql import create_db_tables, remove_unparsed_git_commits
from cg_change_coupling_util import save_cg_change_coupling

# %%
def main():
    path_to_config_file = os.path.normpath('..\project_config\GRIP.pconfig') #glucosio_small

    os.path.exists(path_to_config_file)

    proj_config, proj_paths = execute_project_conf_from_file(
        str(path_to_config_file))

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    init_db(proj_paths)

    download_initial_cache_source(proj_config.get_repo_url(), proj_paths.get_path_to_cache_src_dir(), proj_config.get_only_in_branch())
    execute_intitial_indexing(proj_paths)

    analyse_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    remove_unparsed_git_commits(proj_config=proj_config, proj_paths=proj_paths)

    calculate_cg_diffs(proj_config=proj_config, proj_paths=proj_paths)

    update_commit_changes_to_cg_nodes(proj_config=proj_config, proj_paths=proj_paths)

    save_cg_change_coupling(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))


def init_db(proj_paths):
    #logging.info('Initialize the db.')
    create_db_tables(proj_paths, drop=True)


# %%
if __name__ == '__main__':
    main()
