# %%
from models import *
import logging
from datetime import datetime
import platform

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from utils_sql import remove_unparsed_git_commits
from project_configs import *


# %%
def main():

    path_to_config_file = os.path.normpath(
        '..\project_config\glucosio_small.pconfig')

    if platform.system() == 'Linux':
        path_to_config_file = os.path.normpath(
            '../project_config/glucosio-android.pconfig')


    print('Started App ------------ {0}'.format(datetime.now()))

    proj_config, proj_paths = execute_project_conf_from_file(
        path_to_config_file)

    # can only log after seting log file path
    logging.info('Started App ---------- {0}'.format(datetime.now()))

    #calculate_cg_diffs(proj_config=proj_config, proj_paths=proj_paths)
    remove_unparsed_git_commits(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- {0}'.format(datetime.now()))
    print('Finished App -------------{0}'.format(datetime.now()))

# %%
if __name__ == '__main__':
    main()


# %%
