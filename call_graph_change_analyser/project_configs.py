import os
import logging
from datetime import datetime
from typing import Optional

from utils_py import replace_timezone
from models import ProjectPaths, ProjectConfig

def execute_project_conf_from_file(path_to_config_file:str):
    path_to_config_file = os.path.normpath(path_to_config_file)

    proj_name = None
    from_tag = None
    to_tag = None
    since_date = None
    to_date = None
    save_cache_files = None
    delete_cache_files = None
    path_to_proj_data_dir = None
    path_to_src_files = None
    proj_lang = None
    repo_url = None
    repo_type = None
    commit_file_types = None
    path_to_local_src_dir = None
    only_in_branch = None

    def get_label_content(line, label_size):
        return line[label_size:len(line.rstrip())].replace("'", '')

    with open(path_to_config_file, "r", encoding='utf-8') as configfile:
        lines = configfile.readlines()
        for line in lines:
            if (line.lstrip()).startswith("proj_name:"):
                proj_name=get_label_content(line, len("proj_name:"))
            if (line.lstrip()).startswith("from_tag:"):
                from_tag=get_label_content(line, len("from_tag:"))
            if (line.lstrip()).startswith("to_tag:"):
                to_tag=get_label_content(line, len("to_tag:"))
            if (line.lstrip()).startswith("since_date:"):
                since_date=get_label_content(line, len("since_date:"))
            if (line.lstrip()).startswith("to_date:"):
                to_date=get_label_content(line, len("to_date:"))
            if (line.lstrip()).startswith("save_cache_files:"):
                save_cache_files=get_label_content(line, len("save_cache_files:"))
            if (line.lstrip()).startswith("delete_cache_files:"):
                delete_cache_files=get_label_content(line, len("delete_cache_files:"))
            if (line.lstrip()).startswith("path_to_proj_data_dir:"):
                path_to_proj_data_dir=os.path.normpath(get_label_content(line, len("path_to_proj_data_dir:")))
            if (line.lstrip()).startswith("path_to_src_files:"):
                path_to_src_files=os.path.normpath(get_label_content(line, len("path_to_src_files:")))
            if (line.lstrip()).startswith("proj_lang:"):
                proj_lang=get_label_content(line, len("proj_lang:"))
            if (line.lstrip()).startswith("repo_url:"):
                repo_url=get_label_content(line, len("repo_url:"))
            if (line.lstrip()).startswith("repo_type:"):
                repo_type=get_label_content(line, len("repo_type:"))
            if (line.lstrip()).startswith("path_to_local_src_dir:"):
                path_to_local_src_dir=get_label_content(line, len("path_to_local_src_dir:"))
            if (line.lstrip()).startswith("only_in_branch:"):
                only_in_branch=get_label_content(line, len("only_in_branch:"))
                
    if proj_lang == 'cpp':
        commit_file_types=['.cpp']
    if proj_lang == 'java':
        commit_file_types=['.java']

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang=proj_lang,
                                commit_file_types=commit_file_types,
                                repo_url=repo_url,
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files,
                                only_in_branch=only_in_branch)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir,
                              path_to_src_files=path_to_src_files,
                              path_to_local_src_dir=path_to_local_src_dir)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths


def execute_project_default_conf_PX4(from_tag: Optional[str], to_tag: Optional[str],
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
                                repo_url='https://github.com/PX4/PX4-Autopilot.git',
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


def execute_project_default_conf_JKQtPlotter(from_tag: Optional[str], to_tag: Optional[str],
                                     since_date: Optional[str], to_date: Optional[str],
                                     save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'JKQtPlotter'
    path_to_proj_data_dir = os.path.normpath('../project_results/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='cpp',
                                commit_file_types=['.cpp'],
                                repo_url='https://github.com/jkriege2/JKQtPlotter.git',
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


def execute_project_default_conf_Glucosio(from_tag: Optional[str], to_tag: Optional[str],
                                  since_date: Optional[str] = None, to_date: Optional[str] = None,
                                  save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'glucosio-android'
    path_to_proj_data_dir = os.path.normpath('../project_results/')
    path_to_src_files = os.path.normpath('app/src/main/java/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='java',
                                commit_file_types=['.java'],
                                repo_url='https://github.com/Glucosio/glucosio-android.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir,
                              path_to_src_files=path_to_src_files)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths


def execute_project_default_conf_OpenBot(from_tag: Optional[str] = 'v0.1.0', to_tag: Optional[str] = 'v0.4.0',
                                 since_date: Optional[str] = None, to_date: Optional[str] = None,
                                 save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v0.1.0'
    #to_tag = 'v0.1.0'

    proj_name = 'OpenBot'
    path_to_proj_data_dir = os.path.normpath('../project_results/')
    path_to_src_files = os.path.normpath('android/app/src/main/java/org/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='java',
                                commit_file_types=['.java'],
                                repo_url='https://github.com/isl-org/OpenBot.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir,
                              path_to_src_files=path_to_src_files)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths


def execute_project_default_conf_EConcierge(from_tag: Optional[str] = None, to_tag: Optional[str] = None,
                                    since_date: Optional[str] = '13-03-2014', to_date: Optional[str] = '01-01-2021',
                                    save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'EConcierge'
    path_to_proj_data_dir = os.path.normpath('../project_results/')
    path_to_src_files = os.path.normpath(
        'framework/org.eclipse.concierge/src/')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='java',
                                commit_file_types=['.java'],
                                repo_url='https://github.com/eclipse/concierge.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir,
                              path_to_src_files=path_to_src_files)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths


def execute_project_default_conf_GRIP(from_tag: Optional[str] = None, to_tag: Optional[str] = None,
                              since_date: Optional[str] = '01-01-2016', to_date: Optional[str] = '01-11-2021',
                              save_cache_files: bool = False, delete_cache_files: bool = False):
    #from_tag = 'v2019.11.0'
    #to_tag = 'v2019.11.1'

    proj_name = 'GRIP'
    path_to_proj_data_dir = os.path.normpath('../project_results/')
    path_to_src_files = os.path.normpath('core/src/main/java/edu/wpi/grip')

    proj_config = ProjectConfig(proj_name=proj_name,
                                proj_lang='java',
                                commit_file_types=['.java'],
                                repo_url='https://github.com/WPIRoboticsProjects/GRIP.git',
                                repo_type='Git',
                                repo_from_tag=from_tag,
                                repo_to_tag=to_tag,
                                start_repo_date=since_date,
                                end_repo_date=to_date,
                                save_cache_files=save_cache_files,
                                delete_cache_files=delete_cache_files)
    proj_paths = ProjectPaths(proj_name=proj_config.proj_name,
                              path_to_proj_data_dir=path_to_proj_data_dir,
                              path_to_src_files=path_to_src_files)

    log_filepath = os.path.join(proj_paths.get_path_to_cache_dir(), 'app.log')
    print(log_filepath)

    logging.basicConfig(filename=log_filepath, level=logging.DEBUG,
                        format='%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
    logging.debug('Started App - {0}'.format(str(datetime.now())))

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths
