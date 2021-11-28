# %%
from models import *
import models
import logging
from datetime import datetime
from imp import reload

from models import CallCommitInfo, ProjectPaths, ProjectConfig
from gumtree_difffile_parser import get_method_call_change_info_cpp
from repository_mining_util import load_source_repository_data
from utils_sql import initate_analytics_db
from utils_py import replace_timezone
from call_graph_analysis import get_call_graph, print_graph_stats


# %%
import repository_mining_util
reload(repository_mining_util)
from repository_mining_util import load_source_repository_data, get_file_imports, parse_xml_diffs, parse_mod_file

import models
reload(models)
from models import CallCommitInfo, ProjectPaths, FileData, FileImport

# %%
def main():
    print('Started App - ', datetime.now())
    path_to_cache_dir = 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\'
    proj_name = 'PX4-Autopilot'
    log_filepath = path_to_cache_dir+proj_name+'\\app.log'

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s %(levelname)-8s %(message)s')
    logging.info('Started App - ', datetime.now())

    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                # 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\astChangeAnalyzer_0_1_cpp.jar',
                                path_to_src_diff_jar='..\\resources\\astChangeAnalyzer_0_1_cpp.jar',
                                path_to_repo='https://github.com/PX4/PX4-Autopilot.git',
                                start_repo_date=st_date,
                                end_repo_date=end_date)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_cache_dir=path_to_cache_dir,
                              path_to_proj_data_dir='C:\\Users\\lopm\\Documents\\mt\\sandbox\\projects\\',
                              path_to_git_folder='C:\\Users\\lopm\\Documents\\gitprojects\\' + proj_config.proj_name + '\\')

    load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App - ', datetime.now())
    print('Finished App -', datetime.now())


#%%
if __name__ == '__main__':
    main()


# %%



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
