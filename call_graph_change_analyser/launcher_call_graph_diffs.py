# %%
from models import *
import logging
from datetime import datetime
import platform

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from utils_sql import create_db_tables
from project_configs import *
from call_graph_parsing_util import calculate_cg_diffs


# %%
def main():

    path_to_config_file = os.path.normpath(
        '..\project_config\glucosio_large_commits.pconfig') #glucosio_small

    if platform.system() == 'Linux':
        path_to_config_file = os.path.normpath(
            '../project_config/glucosio_small.pconfig')


    print('Started App ------------ {0}'.format(datetime.now()))

    proj_config, proj_paths = execute_project_conf_from_file(
        path_to_config_file)

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    calculate_cg_diffs(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))


# %%
if __name__ == '__main__':
    main()

