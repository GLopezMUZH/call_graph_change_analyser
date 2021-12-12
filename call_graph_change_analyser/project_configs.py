import os
import logging
from datetime import datetime
from typing import Optional

from utils_py import replace_timezone
from models import ProjectPaths, ProjectConfig


def execute_project_conf_PX4(from_tag: Optional[str], to_tag: Optional[str],
                             since_date: Optional[str], to_date: Optional[str],
                             save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v1.12.0'
    #to_tag = 'v1.12.3'

    proj_name = 'PX4-Autopilot'
    path_to_proj_data_dir = os.path.normpath('../project_results/')

    # source trail db 9.10.2021
    st_date = datetime(2021, 10, 1, 0, 1, 0, 79043)
    st_date = replace_timezone(st_date)
    end_date = datetime(2021, 10, 2, 0, 1, 0, 79043)
    end_date = replace_timezone(end_date)

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_repo='https://github.com/PX4/PX4-Autopilot.git',
                                repo_type='Git',
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files,
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag
                                )
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir)

    log_filepath = os.path.join(
        proj_paths.get_path_to_cache_dir(), proj_name, 'app.log')

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.info('Started App - {0}'.format(datetime.now()))

    return proj_config, proj_paths


def execute_project_conf_JKQtPlotter(from_tag: Optional[str], to_tag: Optional[str],
                                     since_date: Optional[str], to_date: Optional[str],
                                     save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'JKQtPlotter'
    path_to_proj_data_dir = os.path.normpath('../project_results/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                path_to_repo='https://github.com/jkriege2/JKQtPlotter.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths


def execute_project_conf_Glucosio(from_tag: Optional[str], to_tag: Optional[str],
                                  since_date: Optional[str]=None, to_date: Optional[str]=None,
                                  save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'glucosio-android'
    path_to_proj_data_dir = os.path.normpath('../project_results/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='java',
                                commit_file_types=['.java'],
                                path_to_repo='https://github.com/Glucosio/glucosio-android.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths
