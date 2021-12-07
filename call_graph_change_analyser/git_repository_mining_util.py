from typing import Tuple
from pydriller import Repository, Commit, ModificationType
from bs4 import BeautifulSoup

from models import *
from repository_mining_util import get_file_type_validation_function, save_source_code, jarWrapper, get_file_imports, parse_xml_call_diffs
from utils_sql import *


def parse_mod_file_git(mod_file, proj_paths: ProjectPaths,
                   proj_config: ProjectConfig) -> Tuple[List[FileImport], List[CallCommitInfo]]:
    logging.debug('---------------------------')
    logging.debug(mod_file.change_type)
    logging.debug(str(mod_file._new_path))
    logging.debug(mod_file._old_path)
    ccis = []
    fis = []

    mod_file_data = FileData(str(mod_file._new_path))

    # Save new source code
    file_path_current = os.path.join(
        proj_paths.get_path_to_cache_current(), str(mod_file._new_path))
    save_source_code(file_path_current, mod_file.source_code)

    # Save old source code
    if mod_file.change_type != ModificationType.ADD:
        file_path_previous = os.path.join(
            proj_paths.get_path_to_cache_previous(), str(mod_file._new_path))
        save_source_code(file_path_previous,
                         mod_file.source_code_before)

    # Create sourcediff directory
    if mod_file.change_type != ModificationType.ADD:
        file_path_sourcediff = os.path.join(
            proj_paths.get_path_to_cache_sourcediff(), str(mod_file._new_path))
        if not os.path.exists(os.path.dirname(file_path_sourcediff)):
            os.makedirs(os.path.dirname(file_path_sourcediff))

    # Create sourcediff file: not currently because relevant differences files are created in jar
    """
                if mod_file.change_type != ModificationType.ADD:
                    save_source_code_diff_file(
                        file_path_previous, file_path_current, file_path_sourcediff)
                else:
                    # adds new nodes, edges to the db
                    save_new_file_data(file_path_current)
                """

    # Save file imports
    fis = get_file_imports(mod_file.source_code, mod_file_data)

    # Execute the jar for finding the relevant source differences (function/method call changes)
    if mod_file.change_type != ModificationType.ADD:
        args = [proj_config.get_path_to_src_diff_jar(
        ), file_path_previous.__str__(), 'TRUE']
        result = jarWrapper(*args)

        # convert to string -> xml
        diff_xml_results = b''.join(result).decode('utf-8')
        diff_data_xml = BeautifulSoup(diff_xml_results, "xml")

        ccis = parse_xml_call_diffs(
            diff_data_xml, proj_paths.get_path_to_cache_current(), mod_file_data)

    # Delete temporary files after processing
    if proj_config.get_delete_cache_files():
        if os.path.isfile(file_path_current):
            os.remove(file_path_current)
        else:
            print("Error: %s file not found" % file_path_current)
            logging.error("Error: %s file not found" % file_path_current)

        if mod_file.change_type != ModificationType.ADD:
            if os.path.isfile(file_path_previous):
                os.remove(file_path_previous)
            else:
                print("Error: %s file not found" % file_path_previous)
                logging.error("Error: %s file not found" % file_path_previous)

        """
        if mod_file.change_type != ModificationType.ADD:
            if os.path.isfile(file_path_sourcediff):
                os.remove(file_path_sourcediff)
            else:    ## Show an error ##
                print("Error: %s file not found" % file_path_sourcediff)
                logging.error("Error: %s file not found" % file_path_sourcediff)
        """

    logging.debug('---------------------------')
    return (fis, ccis)


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

    # get previous_function_to_file
    previous_active_functions_in_file = get_previous_active_functions_in_file(
        proj_paths.get_path_to_project_db(), mod_file)

    # function_to_file
    update_function_to_file(proj_paths.get_path_to_project_db(
    ), mod_file, commit, previous_active_functions_in_file)

    # file_imports
    fis, ccis = parse_mod_file_git(mod_file, proj_paths, proj_config)
    update_file_imports(mod_file_data, fis,
                        proj_paths.get_path_to_project_db(),
                        commit_hash=commit.hash,
                        commit_datetime=str(commit.committer_date))

    # call_commits
    update_call_commits(ccis,
                        proj_paths.get_path_to_project_db(),
                        commit_hash_start=commit.hash,
                        commit_start_datetime=str(commit.committer_date))


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

                # Save method function change in db
                """
                            print('Nloc:', mod_file.nloc)
                            print('---------------------------')
                            print(mod_file.complexity)
                            print('---------------------------')
                            print(mod_file.token_count)
                            print('---------------------------')
                            """
                """
                            for m in mod_file.methods:
                                print(m.name)
                                print(m.parameters)
                                print(m.fan_in)
                                print(m.fan_out)
                                print(m.general_fan_out)
                            """
