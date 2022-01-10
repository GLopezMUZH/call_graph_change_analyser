from pydriller import Repository, Commit, ModificationType
from bs4 import BeautifulSoup

from models import *
from repository_mining_util import *
from compact_xml_parsing_java import get_function_calls_java
from utils_sql import *
from call_graph_parsing_util import save_cg_data, save_cg_diffs


def git_traverse_all(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    print(proj_config.get_only_in_branch())
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_repo_url(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True,
            only_in_branch=proj_config.get_only_in_branch()).traverse_commits():
        process_git_commit(proj_config=proj_config, proj_paths=proj_paths,
                           is_valid_file_type=is_valid_file_type, commit=commit)


def git_traverse_between_dates(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_repo_url(),
            since=proj_config.get_start_repo_date(),
            to=proj_config.get_end_repo_date(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True,
            only_in_branch=proj_config.get_only_in_branch()).traverse_commits():
        process_git_commit(proj_config=proj_config, proj_paths=proj_paths,
                           is_valid_file_type=is_valid_file_type, commit=commit)


def git_traverse_from_date(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_repo_url(),
            since=proj_config.get_start_repo_date(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True,
            only_in_branch=proj_config.get_only_in_branch()).traverse_commits():
        process_git_commit(proj_config=proj_config, proj_paths=proj_paths,
                           is_valid_file_type=is_valid_file_type, commit=commit, parse_cg=True)


def git_traverse_on_tags(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    is_valid_file_type = get_file_type_validation_function(
        proj_config.proj_lang)
    for commit in Repository(
            path_to_repo=proj_config.get_repo_url(),
            from_tag=proj_config.get_repo_from_tag(),
            to_tag=proj_config.get_repo_to_tag(),
            only_modifications_with_file_types=proj_config.get_commit_file_types(),
            order='reverse', only_no_merge=True,
            only_in_branch=proj_config.get_only_in_branch()).traverse_commits():
        process_git_commit(proj_config=proj_config, proj_paths=proj_paths,
                           is_valid_file_type=is_valid_file_type, commit=commit)


def process_git_commit(proj_config: ProjectConfig, proj_paths: ProjectPaths, is_valid_file_type, commit: Commit, parse_cg: bool = False):
    # git_commit
    insert_git_commit(proj_paths.get_path_to_project_db(),
                      commit_hash=commit.hash, commit_commiter_datetime=str(
        commit.committer_date),
        author=commit.author.name,
        in_main_branch=True,  # commit.in_main_branch,
        merge=commit.merge, nr_modified_files=len(
        commit.modified_files),
        nr_deletions=commit.deletions, nr_insertions=commit.insertions, nr_lines=commit.lines)

    dir_deleted_files = set([])

    for mod_file in commit.modified_files:
        if is_valid_file_type(str(mod_file._new_path)) or is_valid_file_type(str(mod_file._old_path)):
            dir_deleted_file = process_file_git_commit(proj_config, proj_paths,
                                                       commit, mod_file)
            if dir_deleted_file != '':
                dir_deleted_files.add(dir_deleted_file)

    for d in dir_deleted_files:
        delete_empty_dir(d)

    if parse_cg:
        save_cg_data(proj_name=proj_config.get_proj_name(),
                                    path_to_cache_cg_dbs=proj_paths.get_path_to_cache_cg_dbs(), commit_hash=commit.hash)

        save_cg_diffs(proj_name=proj_config.get_proj_name(),
                      path_to_cache_cg_dbs=proj_paths.get_path_to_cache_cg_dbs(), commit_hash=commit.hash, commit_date=commit.committer_date,
                      path_to_project_db=proj_paths.get_path_to_project_db())


def process_file_git_commit(proj_config: ProjectConfig, proj_paths: ProjectPaths,
                            commit: Commit, mod_file: ModifiedFile):

    process_file_git_commit_ASTdiff_parsing(proj_config, proj_paths,
                                            commit, mod_file)

    # process call graph sourceTrail
    dir_deleted_file = process_file_git_commit_cg_parsing(
        proj_paths, mod_file)

    return dir_deleted_file


def process_file_git_commit_cg_parsing(proj_paths: ProjectPaths, mod_file: ModifiedFile):
    # Save new source code
    # ADDed file
    # MODIFYed file
    # DELETEd file
    # RENAMEd file

    # COPY file
    # UNKNOWN file

    if mod_file.change_type == ModificationType.ADD or mod_file.change_type == ModificationType.MODIFY:
        logging.info("ADDorMOD {3}. File {0} old path: {1}, new path: {2}.".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path, mod_file.change_type.name))
        file_path_added = os.path.join(
            proj_paths.get_path_to_cache_src_dir(), str(mod_file._new_path))
        save_source_code(file_path_added,
                         mod_file.source_code)
        return ''

    if mod_file.change_type == ModificationType.DELETE:
        logging.info("DELETE {3}. File {0} old path: {1}, new path: {2}.".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path, mod_file.change_type.name))
        file_path_deleted = os.path.join(
            proj_paths.get_path_to_cache_src_dir(), str(mod_file._old_path))
        delete_source_code(file_path_deleted, mod_file.source_code)
        return os.path.dirname(file_path_deleted)

    # CSHttpCameraFrameGrabber.java
    # old path: core/src/main/java/edu/wpi/grip/core/sources/CSHttpCameraFrameGrabber.java,
    # new path: core/src/main/java/edu/wpi/grip/core/sources/CSCameraFrameGrabber.java. TODO
    if mod_file.change_type == ModificationType.RENAME:
        logging.info("RENAME. File {0} old path: {1}, new path: {2}.".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path))
        file_path_added = os.path.join(
            proj_paths.get_path_to_cache_src_dir(), str(mod_file._new_path))
        file_path_deleted = os.path.join(
            proj_paths.get_path_to_cache_src_dir(), str(mod_file._old_path))
        save_source_code(file_path_added,
                         mod_file.source_code)
        return os.path.dirname(file_path_deleted)

    if mod_file.change_type == ModificationType.COPY or mod_file.change_type == ModificationType.UNKNOWN:
        print("ModType COPY1/UNKN6 {3}. File {0} old path: {1}, new path: {2}. TODO".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path, mod_file.change_type.name))
        logging.info("ModType COPY1/UNKN6 {3}. File {0} old path: {1}, new path: {2}. TODO".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path, mod_file.change_type.name))
        return ''


def process_file_git_commit_ASTdiff_parsing(proj_config: ProjectConfig, proj_paths: ProjectPaths,
                                            commit: Commit, mod_file: ModifiedFile):
    mod_file_data = FileData(str(mod_file._new_path))

    # Create sourcediff directory
    if proj_config.get_save_cache_files:
        file_path_sourcediff = os.path.join(
            proj_paths.get_path_to_cache_sourcediff(), str(mod_file._new_path))
        if not os.path.exists(os.path.dirname(file_path_sourcediff)):
            os.makedirs(os.path.dirname(file_path_sourcediff))

    # Save new source code
    file_path_current = None
    if mod_file.change_type != ModificationType.DELETE and mod_file.change_type != ModificationType.RENAME:
        file_path_current = os.path.join(
            proj_paths.get_path_to_cache_current(), str(mod_file._new_path))
        save_source_code(file_path_current, mod_file.source_code)

    file_path_previous = None
    if mod_file.change_type != ModificationType.ADD and mod_file.change_type != ModificationType.RENAME:
        file_path_previous = os.path.join(
            proj_paths.get_path_to_cache_previous(), str(mod_file._old_path))
        save_source_code(file_path_previous,
                         mod_file.source_code_before)

    if mod_file.change_type == ModificationType.RENAME:
        print("RENAME. File {0} old path: {1}, new path: {2}. TODO".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path))
        logging.info("RENAME. File {0} old path: {1}, new path: {2}. TODO".format(
            mod_file.filename, mod_file._new_path, mod_file._old_path))
        return

    # insert file_commit
    insert_file_commit(proj_paths.get_path_to_project_db(), mod_file_data=mod_file_data,
                       commit_hash=commit.hash, commit_commiter_datetime=commit.committer_date,
                       commit_file_name=mod_file.filename,
                       commit_new_path=mod_file.new_path, commit_old_path=mod_file.old_path,
                       change_type=mod_file.change_type)

    # update file imports
    fis = get_file_imports(proj_config.get_proj_lang(), proj_paths.get_path_to_src_files(),
                           mod_file.source_code, mod_file_data)
    update_file_imports(mod_file_data, fis,
                        proj_paths.get_path_to_project_db(),
                        commit_hash=commit.hash,
                        commit_datetime=str(commit.committer_date))

    # function_commit
    insert_function_commit(
        proj_paths.get_path_to_project_db(), mod_file, commit)

    # update function_to_file
    update_function_to_file(
        proj_paths.get_path_to_project_db(), mod_file, commit)

    # update function_call
    update_function_calls(proj_config, proj_paths, mod_file, commit,
                          file_path_current, file_path_previous)


# TODO list to array, maybe
# TODO handle mod_file._old_path != mod_file._new_path
def update_function_calls(proj_config: ProjectConfig, proj_paths: ProjectPaths,
                          mod_file: ModifiedFile, commit: Commit, file_path_current: str,
                          file_path_previous: Optional[str] = None):

    mod_file_data = FileData(str(mod_file._new_path))

    if proj_config.get_proj_lang() == 'java' or proj_config.get_proj_lang() == 'cpp':
        # Current source code
        curr_function_calls = []
        if file_path_current is not None:
            # get compact xml parsed source
            curr_src_args = [
                proj_config.PATH_TO_SRC_COMPACT_XML_PARSING, file_path_current]
            result = jarWrapper(*curr_src_args)
            # convert to string -> xml
            curr_src_str = b''.join(result).decode('utf-8')
            curr_src_xml = BeautifulSoup(curr_src_str, "xml")

            save_compact_xml_parsed_code(path_to_cache_dir=proj_paths.get_path_to_cache_current(),
                                         relative_file_path=str(mod_file._new_path), source_text=curr_src_str)

            """
            calling_function_unqualified_name,
            calling_function_nr_parameters,
            called_function_unqualified_name       
            """
            if proj_config.get_proj_lang() == 'java':
                curr_function_calls = get_function_calls_java(curr_src_xml)
            else:
                curr_function_calls = []
                logging.info("TODO")
                print("TODO")

        # Previous source code
        prev_function_calls = []
        if mod_file.change_type != ModificationType.ADD and file_path_previous is not None:
            # get compact xml parsed source
            prev_src_args = [
                proj_config.PATH_TO_SRC_COMPACT_XML_PARSING, file_path_previous]
            result = jarWrapper(*prev_src_args)
            # convert to string -> xml
            prev_src_str = b''.join(result).decode('utf-8')
            prev_src_xml = BeautifulSoup(prev_src_str, "xml")

            save_compact_xml_parsed_code(path_to_cache_dir=proj_paths.get_path_to_cache_previous(),
                                         relative_file_path=str(
                mod_file._new_path),
                source_text=prev_src_str)

            if proj_config.get_proj_lang() == 'java':
                prev_function_calls = get_function_calls_java(prev_src_xml)
            else:
                curr_function_calls = []
                print("TODO")
                logging.info("TODO")

        cm_dates = CommitDates(commit.hash, commit.committer_date)
        rows_curr, rows_deleted = set_hashes_to_function_calls(
            curr_function_calls, prev_function_calls, cm_dates, mod_file)
        logging.debug("Deleted: ")
        logging.debug(rows_deleted)
        #arr_all_function_calls = complete_function_calls_data(arr_all_function_calls)

        """
        FUNCTION_CALL
        file_name
        file_dir_path
        file_path
        calling_function_unqualified_name
        calling_function_nr_parameters
        called_function_unqualified_name
        called_function_nr_parameters
        commit_hash_start
        commit_start_datetime
        commit_hash_oldest
        commit_oldest_datetime
        commit_hash_end
        commit_end_datetime
        closed
        """
        save_raw_function_call_curr_rows(
            proj_paths.get_path_to_project_db(), rows_curr, mod_file_data)
        save_raw_function_call_deleted_rows(
            proj_paths.get_path_to_project_db(), rows_deleted, mod_file_data)

        # save_call_commit_rows() # MIGHT NOT NEED THEM

    else:
        print("No current parser for the project language.")
