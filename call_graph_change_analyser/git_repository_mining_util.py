from pydriller import Repository, Commit, ModificationType

from models import *
from repository_mining_util import get_file_type_validation_function, get_file_imports
from utils_sql import *



def git_traverse_all(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True, only_in_branch='master').traverse_commits():

        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_git_commit(proj_config, proj_paths, commit, mod_file)


def git_traverse_on_dates(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            since=proj_config.get_start_repo_date(),
            to=proj_config.get_end_repo_date(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True, only_in_branch='master').traverse_commits():

        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_git_commit(proj_config, proj_paths, commit, mod_file)


def git_traverse_on_tags(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_path_to_repo(),
            from_tag=proj_config.get_repo_from_tag(),
            to_tag=proj_config.get_repo_to_tag(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True, only_in_branch='master').traverse_commits():

        # git_commit
        insert_git_commit(proj_paths.get_path_to_project_db(),
                          commit_hash=commit.hash, commit_commiter_datetime=str(
            commit.committer_date),
            author=commit.author.name,
            in_main_branch=True,  # commit.in_main_branch,
            merge=commit.merge, nr_modified_files=len(
                              commit.modified_files),
            nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

        for mod_file in commit.modified_files:
            if (is_valid_file_type(str(mod_file._new_path))):
                process_file_git_commit(proj_config, proj_paths, commit, mod_file)


def process_file_git_commit(proj_config, proj_paths, commit: Commit, mod_file: ModifiedFile):
    mod_file_data = FileData(str(mod_file._new_path))

    # insert file_commit
    insert_file_commit(proj_paths.get_path_to_project_db(), mod_file_data=mod_file_data,
                       commit_hash=commit.hash, commit_commiter_datetime=commit.committer_date,
                       commit_file_name=mod_file.filename,
                       commit_new_path=mod_file.new_path, commit_old_path=mod_file.old_path,
                       change_type=mod_file.change_type)

    # insert function_commit 's
    insert_function_commit(
        proj_paths.get_path_to_project_db(), mod_file, commit)

    # update file imports
    fis = get_file_imports(mod_file.source_code, mod_file_data)
    update_file_imports(mod_file_data, fis,
                    proj_paths.get_path_to_project_db(),
                    commit_hash=commit.hash,
                    commit_datetime=str(commit.committer_date))
    
    
