from models import ProjectConfig, ProjectPaths
from git_repository_mining_util import git_traverse_from_date, git_traverse_on_tags, git_traverse_all, git_traverse_between_dates

def load_source_repository_data(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    if proj_config.get_repo_type() == 'Git':
        if (proj_config.get_start_repo_date() is not None and proj_config.get_end_repo_date()):
            git_traverse_between_dates(proj_config, proj_paths)
        if proj_config.get_start_repo_date() is not None:
            git_traverse_from_date(proj_config, proj_paths)
        elif proj_config.get_repo_from_tag() is not None:
            git_traverse_on_tags(proj_config, proj_paths)
        else:
            git_traverse_all(proj_config, proj_paths)
    else:
        print("Alternative repository {0} implementation coming soon. ".format(proj_config.get_repo_type()))
    