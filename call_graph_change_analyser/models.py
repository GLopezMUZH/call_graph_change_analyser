# %%
import os
from datetime import datetime
from enum import Enum
from typing import Optional, List
from shutil import copy as shutil_copy


class ActionClass(Enum):
    ADD = 1
    DELETE = 2
    INSERT = 3
    MOVE = 4
    MODIFIY = 5


class StatisticNames(Enum):
    cg_f_changes = 1


class StatisticParams1(Enum):
    degree_distance = 1


class StatisticParams2(Enum):
    nr_edges = 1
    nr_nodes = 1


class ProjectConfig:
    PATH_TO_SRC_DIFF_JAR_CPP = os.path.normpath(
        '../resources/astChangeAnalyzer_0_1_cpp.jar')
    PATH_TO_SRC_DIFF_JAR_JAVA = os.path.normpath(
        '../resources/astChangeAnalyzer_0_1_java.jar')
    PATH_TO_SRC_COMPACT_XML_PARSING = os.path.normpath(
        '../resources/astChangeAnalyzer_0_1_parsexmlcompact.jar')

    def __init__(
            self,  proj_name:
            str, proj_lang: str, commit_file_types: List[str],
            repo_url: str, repo_type: str = 'Git',
            start_repo_date: Optional[datetime] = None, end_repo_date: Optional[datetime] = None,
            repo_from_tag: Optional[str] = None, repo_to_tag: Optional[str] = None,
            save_cache_files: Optional[bool] = True,
            delete_cache_files: Optional[bool] = True,
            delete_cg_src_db: Optional[bool] = True,
            only_in_branch: Optional[str] = None) -> None:
        self.proj_name = proj_name
        self.proj_lang = proj_lang
        self.commit_file_types = commit_file_types
        self.repo_url = repo_url
        self.repo_type = repo_type
        self.start_repo_date = start_repo_date
        self.end_repo_date = end_repo_date
        self.repo_from_tag = repo_from_tag
        self.repo_to_tag = repo_to_tag
        self.save_cache_files = save_cache_files
        self.delete_cache_files = delete_cache_files
        self.delete_cg_src_db = delete_cg_src_db
        self.only_in_branch = only_in_branch if only_in_branch is not None else 'master'
        self.path_to_src_compact_xml_parsing = ProjectConfig.PATH_TO_SRC_COMPACT_XML_PARSING
        if proj_lang == 'java':
            self.path_to_src_diff_jar = ProjectConfig.PATH_TO_SRC_DIFF_JAR_CPP
        elif proj_lang == 'cpp':
            self.path_to_src_diff_jar = ProjectConfig.PATH_TO_SRC_DIFF_JAR_CPP
        else:
            raise Exception("No valid language.")

    def get_proj_name(self):
        return self.proj_name

    def get_proj_lang(self):
        return self.proj_lang

    def get_commit_file_types(self):
        return self.commit_file_types

    def get_repo_url(self):
        return self.repo_url

    def get_repo_type(self):
        return self.repo_type

    def get_start_repo_date(self):
        return self.start_repo_date

    def get_end_repo_date(self):
        return self.end_repo_date

    def get_repo_from_tag(self):
        return self.repo_from_tag

    def get_repo_to_tag(self):
        return self.repo_to_tag

    def get_path_to_src_diff_jar(self):
        return self.path_to_src_diff_jar

    def get_save_cache_files(self):
        return self.save_cache_files

    def get_delete_cache_files(self) -> bool:
        return self.delete_cache_files

    def get_delete_cg_src_db(self) -> bool:
        return self.delete_cg_src_db

    def get_only_in_branch(self):
        return self.only_in_branch

    def __str__(self) -> str:
        return("ProjectConfig. Name: {0}, delete_cache_files: {1}".format(self.proj_name, self.delete_cache_files))


class ProjectPaths:
    def __init__(self, proj_name: str, path_to_proj_data_dir: str, path_to_src_files: str = None,
                 srctrl_orig_config_file_path: str = None, separate_edge_hist_db: Optional[bool] = True) -> None:
        # project data directory
        self.path_to_proj_data_dir = os.path.join(
            path_to_proj_data_dir, proj_name)

        # for finding path from package
        self.path_to_src_files = os.path.normpath(path_to_src_files)
        
        # for replacing paths on the cg db
        self.str_path_to_src_files = path_to_src_files

        # sourcetrail config file
        self.srctrl_orig_config_file_path = os.path.normpath(
            srctrl_orig_config_file_path)

        # analytics database
        self.path_to_project_db = os.path.join(
            path_to_proj_data_dir, proj_name, proj_name + '_analytics.db')

        # edge_hist database
        self.path_to_edge_hist_db = os.path.join(
            path_to_proj_data_dir, proj_name, proj_name + '_edge_hist.db')

        # CACHE FILES
        # temporary files main folder
        self.path_to_cache_dir = os.path.join(
            path_to_proj_data_dir, proj_name, '.cache')

        # ast parsing analytics
        self.path_to_cache_current = os.path.join(
            self.path_to_cache_dir, 'astparsing', 'current')
        self.path_to_cache_previous = os.path.join(
            self.path_to_cache_dir, 'astparsing', 'previous')
        self.path_to_cache_sourcediff = os.path.join(
            self.path_to_cache_dir, 'astparsing', 'sourcediff')

        # cache source to track git changes
        self.path_to_cache_src_dir = os.path.join(
            self.path_to_cache_dir, 'git')
        # local folder with current source (Java
        # path_to_local_src_dir

        # temporary sourcetrail db's
        self.path_to_cache_cg_dbs_dir = os.path.join(
            self.path_to_cache_dir, 'callgraphdb')

        # TODO delete
        # graph db
        self.path_to_srctrail_db = os.path.join(
            path_to_proj_data_dir, proj_name, 'callgraphdb', proj_name + '.srctrldb')

        # create folders if not exist
        if not os.path.exists(self.path_to_cache_dir):
            os.makedirs(self.path_to_cache_dir)
        if not os.path.exists(self.path_to_cache_current):
            os.makedirs(self.path_to_cache_current)
        if not os.path.exists(self.path_to_cache_previous):
            os.makedirs(self.path_to_cache_previous)
        if not os.path.exists(self.path_to_cache_sourcediff):
            os.makedirs(self.path_to_cache_sourcediff)
        if not os.path.exists(self.path_to_cache_src_dir):
            os.makedirs(self.path_to_cache_src_dir)
        if not os.path.exists(self.path_to_cache_cg_dbs_dir):
            os.makedirs(self.path_to_cache_cg_dbs_dir)

        # copy original srctrail config file to temporary folder
        if os.path.isfile(self.srctrl_orig_config_file_path):
            shutil_copy(self.srctrl_orig_config_file_path,
                        self.path_to_cache_cg_dbs_dir)
        else:
            print("Wrong configuration file path.")

    def get_path_to_proj_data_dir(self):
        return self.path_to_proj_data_dir

    def get_path_to_src_files(self):
        return self.path_to_src_files

    def get_str_path_to_src_files(self):
        return self.str_path_to_src_files

    def get_srctrl_orig_config_file_path(self):
        return self.srctrl_orig_config_file_path

    def get_path_to_project_db(self):
        return self.path_to_project_db

    def get_path_to_edge_hist_db(self):
        return self.path_to_edge_hist_db

    def get_path_to_cache_dir(self):
        return self.path_to_cache_dir

    def get_path_to_cache_current(self):
        return self.path_to_cache_current

    def get_path_to_cache_previous(self):
        return self.path_to_cache_previous

    def get_path_to_cache_sourcediff(self):
        return self.path_to_cache_sourcediff

    def get_path_to_cache_src_dir(self):
        return self.path_to_cache_src_dir

    def get_path_to_cache_cg_dbs_dir(self):
        return self.path_to_cache_cg_dbs_dir

    # TODO delete
    def get_path_to_srctrail_db(self):
        return self.path_to_srctrail_db

    def __str__(self) -> str:
        return("ProjectPaths. Analytics db: {0}".format(self.path_to_project_db))


class FileData():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # calculate dir path and file name
        self.file_dir_path = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)

    def get_file_name(self):
        return self.file_name

    def get_file_dir_path(self):
        return self.file_dir_path

    def get_file_path(self):
        return self.file_path

    def __str__(self) -> str:
        return("FileData [file_name: {0}, file_dir_path: {1}]"
               .format(self.file_name,
                       self.file_dir_path))


class GitCommitInfo:
    def __init__(self, commit_hash: Optional[str] = None, commit_commiter_datetime: Optional[str] = None,
                 author: Optional[str] = None, in_main_branch: Optional[bool] = None,
                 merge: Optional[bool] = None, nr_modified_files: Optional[int] = None,
                 nr_deletions: Optional[int] = None, nr_insertions: Optional[int] = None, nr_lines: Optional[int] = None) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source 
        of the called function can be inferred. 
        """
        self.commit_hash = commit_hash
        self.commit_commiter_datetime = commit_commiter_datetime
        self.author = author
        self.in_main_branch = in_main_branch
        self.merge = merge
        self.nr_modified_files = nr_modified_files
        self.nr_deletions = nr_deletions
        self.nr_insertions = nr_insertions
        self.nr_lines = nr_lines

    def __str__(self) -> str:
        return("GitCommitInfo: commit_hash: {0}, commit_commiter_datetime: {1}, nr_modified_files: {2}"
               .format(self.commit_hash, self.commit_commiter_datetime, self.nr_modified_files))


class FileCommitInfo:
    def __init__(self, src_file_data: FileData,
                 commit_hash: Optional[str] = None, commit_commiter_datetime: Optional[str] = None,
                 commit_file_name: Optional[str] = None,
                 commit_new_path: Optional[str] = None, commit_old_path: Optional[str] = None,
                 change_type: Optional[bool] = None) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source 
        of the called function can be inferred. 
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.commit_hash = commit_hash
        self.commit_commiter_datetime = commit_commiter_datetime
        self.commit_file_name = commit_file_name
        self.commit_new_path = commit_new_path
        self.commit_old_path = commit_old_path
        self.change_type = change_type
        self.path_change = False if commit_new_path == commit_old_path else True

    def __str__(self) -> str:
        return("FileCommitInfo: file_name: {0}, commit_file_name: {1}, commit_commiter_datetime: {2}, change_type: {3}, path_change: {4}"
               .format(self.file_name, self.commit_file_name, self.commit_commiter_datetime, self.change_type, self.path_change))


class FunctionCommitInfo:
    def __init__(self, src_file_data: FileData,
                 function_name: Optional[str] = None, function_long_name: Optional[str] = None,
                 function_parameters: Optional[str] = None, function_nloc: Optional[str] = None,
                 commit_hash: Optional[str] = None, commit_commiter_datetime: Optional[str] = None,
                 commit_file_name: Optional[str] = None,
                 commit_new_path: Optional[str] = None, commit_old_path: Optional[str] = None) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source 
        of the called function can be inferred. 
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.function_name = function_name
        self.function_long_name = function_long_name
        self.function_parameters = function_parameters
        self.function_nloc = function_nloc
        self.commit_hash = commit_hash
        self.commit_commiter_datetime = commit_commiter_datetime
        self.commit_file_name = commit_file_name
        self.commit_new_path = commit_new_path
        self.commit_old_path = commit_old_path
        self.path_change = False if commit_new_path == commit_old_path else True

    def __str__(self) -> str:
        return("FunctionCommitInfo: function_name: {0}, file_name: {1}, commit_commiter_datetime: {2}, commit_hash: {3}, path_change: {4}"
               .format(self.function_name, self.file_name, self.commit_commiter_datetime, self.commit_hash, self.path_change))


class CallCommitInfo:
    def __init__(self, src_file_data: FileData, calling_function: str, called_function: str,
                 action_class: ActionClass,
                 commit_hash_start: Optional[str] = None, commit_start_datetime: Optional[str] = None,
                 commit_hash_end: Optional[str] = None, commit_end_datetime: Optional[str] = None) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source 
        of the called function can be inferred. 
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.calling_function = calling_function
        self.called_function = called_function
        self.action_class = action_class
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_file_name(self) -> str:
        return self.file_name

    def get_file_dir_path(self) -> str:
        return self.file_dir_path

    def get_file_path(self) -> str:
        return self.file_path

    def get_calling_function(self) -> str:
        return self.calling_function

    def get_called_function(self) -> str:
        return self.called_function

    def get_action_class(self) -> ActionClass:
        return self.action_class

    def get_commit_hash_start(self) -> str:
        return self.commit_hash_start

    def get_commit_start_datetime(self) -> str:
        return self.commit_start_datetime

    def get_commit_hash_end(self) -> str:
        return self.commit_hash_end

    def get_commit_end_datetime(self) -> str:
        return self.commit_end_datetime

    def set_commit_hash_start(self, commit_hash_start):
        self.commit_hash_start = commit_hash_start

    def set_commit_start_datetime(self, commit_start_datetime):
        self.commit_start_datetime = commit_start_datetime

    def set_commit_hash_end(self, commit_hash_end):
        self.commit_hash_end = commit_hash_end

    def set_commit_end_datetime(self, commit_end_datetime):
        self.commit_end_datetime = commit_end_datetime

    def __str__(self) -> str:
        return("CallCommitInfo: source_node: {0}, called_function: {1}, start_date: {2}, end_date: {3}, file_path: {4}"
               .format(self.calling_function, self.called_function, self.commit_start_datetime, self.commit_end_datetime, self.file_path))


class FunctionToFile:
    def __init__(self, src_file_data: FileData,
                 function_name: Optional[str] = None, function_long_name: Optional[str] = None,
                 function_parameters: Optional[str] = None,
                 commit_hash_start: Optional[str] = None, commit_start_datetime: Optional[str] = None,
                 commit_hash_end: Optional[str] = None, commit_end_datetime: Optional[str] = None) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source 
        of the called function can be inferred. 
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.function_name = function_name
        self.function_long_name = function_long_name
        self.function_parameters = function_parameters
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def set_commit_hash_start(self, commit_hash_start):
        self.commit_hash_start = commit_hash_start

    def set_commit_start_datetime(self, commit_start_datetime):
        self.commit_start_datetime = commit_start_datetime

    def set_commit_hash_end(self, commit_hash_end):
        self.commit_hash_end = commit_hash_end

    def set_commit_end_datetime(self, commit_end_datetime):
        self.commit_end_datetime = commit_end_datetime

    def __str__(self) -> str:
        return("FunctionToFile: file_name: {0}, function_name: {1}, file_path: {2}, commit_start_datetime: {3}, commit_end_datetime: {4}"
               .format(self.file_name, self.function_name, self.file_path, self.commit_start_datetime, self.commit_end_datetime))


class FileImport():
    def __init__(self, src_file_data: FileData,
                 import_file_path: str,
                 import_file_name: str,
                 import_file_dir_path: str,
                 import_file_pkg: str = None,
                 commit_hash_start=None, commit_start_datetime=None,
                 commit_hash_end=None, commit_end_datetime=None) -> None:
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.import_file_path = import_file_path
        self.import_file_name = import_file_name
        self.import_file_dir_path = import_file_dir_path
        self.import_file_pkg = import_file_pkg
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_file_name(self) -> str:
        return self.file_name

    def get_file_dir_path(self) -> str:
        return self.file_dir_path

    def get_file_path(self) -> str:
        return self.file_path

    def get_import_file_path(self) -> str:
        return self.import_file_path

    def get_import_file_name(self) -> str:
        return self.import_file_name

    def get_import_file_dir_path(self) -> str:
        return self.import_file_dir_path

    def get_import_file_pkg(self) -> str:
        return self.import_file_pkg

    def get_commit_hash_start(self) -> str:
        return self.commit_hash_start

    def get_commit_start_datetime(self) -> str:
        return self.commit_start_datetime

    def get_commit_hash_end(self) -> str:
        return self.commit_hash_end

    def get_commit_end_datetime(self) -> str:
        return self.commit_end_datetime

    def set_commit_hash_end(self, commit_hash_end):
        self.commit_hash_end = commit_hash_end

    def set_commit_end_datetime(self, commit_end_datetime):
        self.commit_end_datetime = commit_end_datetime

    def __str__(self) -> str:
        return("FileImport[src_file_path: {0}, import_file_name: {1}, import_file_dir_path: {2}, import_file_pkg: {3}]"
               .format(self.file_path, self.import_file_name, self.import_file_dir_path, self.import_file_pkg))


class CommitDates():
    def __init__(self, commit_hash, commiter_datetime):
        self.commit_hash = commit_hash
        self.commiter_datetime = commiter_datetime

    def get_commit_hash(self) -> str:
        return self.commit_hash

    def get_commiter_datetime(self) -> str:
        return self.commiter_datetime


class CommitPairDates():
    def __init__(self, commit_hash_start, commit_start_datetime,
                 commit_hash_end, commit_end_datetime):
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_commit_hash_start(self) -> str:
        return self.commit_hash_start

    def get_commit_start_datetime(self) -> str:
        return self.commit_start_datetime

    def get_commit_hash_end(self) -> str:
        return self.commit_hash_end

    def get_commit_end_datetime(self) -> str:
        return self.commit_end_datetime


"""
class NodeType(Enum):
    NODE_SYMBOL = 1
    NODE_TYPE = 2
    NODE_BUILTIN_TYPE = 4
    NODE_MODULE = 8
    NODE_NAMESPACE = 16
    NODE_PACKAGE = 32
    NODE_STRUCT = 64
    NODE_CLASS = 128
    NODE_INTERFACE = 256
    NODE_ANNOTATION = 512
    NODE_GLOBAL_VARIABLE = 1024
    NODE_FIELD = 2048
    NODE_FUNCTION = 4096
    NODE_METHOD = 8192
    NODE_ENUM = 16384
    NODE_ENUM_CONSTANT = 32768
    NODE_TYPEDEF = 65536
    NODE_TYPE_PARAMETER = 131072
    NODE_FILE = 262144
    NODE_MACRO = 524288
    NODE_UNION = 1048576

class EdgeType(Enum):
    EDGE_UNDEFINED = 0
    EDGE_MEMBER = 1
    EDGE_TYPE_USAGE = 2
    EDGE_USAGE = 4
    EDGE_CALL = 8
    EDGE_INHERITANCE = 16
    EDGE_OVERRIDE = 32
    EDGE_TYPE_ARGUMENT = 64
    EDGE_TEMPLATE_SPECIALIZATION = 128
    EDGE_INCLUDE = 256
    EDGE_IMPORT = 512
    EDGE_BUNDLED_EDGES = 1024
    EDGE_MACRO_USAGE = 2048
    EDGE_ANNOTATION_USAGE = 4096

dict 
"""

# %%
EdgeType = {
    0: 'EDGE_UNDEFINED',
    1: 'EDGE_MEMBER',
    2: 'EDGE_TYPE_USAGE',
    4: 'EDGE_USAGE',
    8: 'EDGE_CALL',
    16: 'EDGE_INHERITANCE',
    32: 'EDGE_OVERRIDE',
    64: 'EDGE_TYPE_ARGUMENT',
    128: 'EDGE_TEMPLATE_SPECIALIZATION',
    256: 'EDGE_INCLUDE',
    512: 'EDGE_IMPORT',
    1024: 'EDGE_BUNDLED_EDGES',
    2048: 'EDGE_MACRO_USAGE',
    4096: 'EDGE_ANNOTATION_USAGE',
}

NodeType = {
    1: 'NODE_SYMBOL',
    2: 'NODE_TYPE',
    4: 'NODE_BUILTIN_TYPE',
    8: 'NODE_MODULE',
    16: 'NODE_NAMESPACE',
    32: 'NODE_PACKAGE',
    64: 'NODE_STRUCT',
    128: 'NODE_CLASS',
    256: 'NODE_INTERFACE',
    512: 'NODE_ANNOTATION',
    1024: 'NODE_GLOBAL_VARIABLE',
    2048: 'NODE_FIELD',
    4096: 'NODE_FUNCTION',
    8192: 'NODE_METHOD',
    16384: 'NODE_ENUM',
    32768: 'NODE_ENUM_CONSTANT',
    65536: 'NODE_TYPEDEF',
    131072: 'NODE_TYPE_PARAMETER',
    262144: 'NODE_FILE',
    524288: 'NODE_MACRO',
    1048576: 'NODE_UNION',
}


# %%
