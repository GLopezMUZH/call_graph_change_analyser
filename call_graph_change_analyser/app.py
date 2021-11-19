# %%
from call_graph_analysis import *
import call_graph_analysis
from datetime import datetime
from imp import reload

from models import MethodCallChangeInfo, ProjectPaths, ProjectConfig
from gumtree_difffile_parser import get_method_call_change_info_cpp
from repository_mining_util import load_source_repository_data
from utils_sql import initate_analytics_db
from call_graph_analysis import get_call_graph, print_graph_stats

# %%
import repository_mining_util
reload(repository_mining_util)
from repository_mining_util import load_source_repository_data
reload(call_graph_analysis)


#%%
import pytz
def _replace_timezone(dt: datetime):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt

# %%
st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
st_date = _replace_timezone(st_date)
end_date = datetime(2021, 10, 3, 0, 1, 0, 79043)
end_date = _replace_timezone(end_date)

proj_config = ProjectConfig(proj_name='PX4-Autopilot',
                            proj_lang='cpp',
                            commit_file_types=['.cpp'],
                            path_to_src_diff_jar='..\\resources\\astChangeAnalyzer_0_1_cpp.jar',  # 'C:\\Users\\lopm\\Documents\\mt\\sandbox\\astChangeAnalyzer_0_1_cpp.jar',
                            path_to_repo='https://github.com/PX4/PX4-Autopilot.git',
                            start_repo_date=st_date,
                            end_repo_date=end_date)
proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                          path_cache_dir='C:\\Users\\lopm\\Documents\\mt\\sandbox\\.cache\\')


#%%
load_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

# %%
initate_analytics_db(proj_paths, drop=True, load_init_graph=True)
#clone_git_source(path_to_git_folder, path_to_git)

# %%
# only the graph parth
G = get_call_graph(proj_paths)
print_graph_stats(G)


# proj_name = 'PX4-Autopilot' # 'glucosio-android'
# proj_lang = 'cpp' # 'cpp' 'python' 'java'
#path_to_repo = 'https://github.com/PX4/PX4-Autopilot.git'
# path_to_git = 'https://github.com/ishepard/pydriller.git' #'git@github.com:ishepard/pydriller.git/'

# start_repo_date = datetime(2021, 10, 1, 0, 1, 0)  #(2018, 4, 1, 0, 1, 0)

# 'https://github.com/ishepard/pydriller.git'
# 'https://github.com/PX4/PX4-Autopilot.git'
# 'https://github.com/Glucosio/glucosio-android.git'


# %%
