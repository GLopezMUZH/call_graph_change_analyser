# %%
from datetime import datetime
from enum import Enum
from typing import Optional, List

# Classes
# class CommitInfo:


class ActionClass(Enum):
    ADD = 1
    DELETE = 2
    INSERT = 3
    MOVE = 4


class ProjectConfig:
    def __init__(
            self,  proj_name:
            str, proj_lang: str, commit_file_types: List[str], path_to_src_diff_jar: str,
            path_to_repo: str,
            start_repo_date: Optional[datetime] = None, end_repo_date: Optional[datetime] = None,
            repo_from_tag: Optional[str] = None, repo_to_tag: Optional[str] = None,
            delete_cache_files: Optional[bool] = True) -> None:
        self.proj_name = proj_name
        self.proj_lang = proj_lang
        self.commit_file_types = commit_file_types
        self.path_to_repo = path_to_repo
        self.start_repo_date = start_repo_date
        self.end_repo_date = end_repo_date
        self.repo_from_tag = repo_from_tag
        self.repo_to_tag = repo_to_tag
        self.path_to_src_diff_jar = path_to_src_diff_jar
        self.delete_cache_files = delete_cache_files

    def get_path_to_repo(self):
        return self.path_to_repo

    def get_commit_file_types(self):
        return self.commit_file_types

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

    def get_delete_cache_files(self) -> bool:
        return self.delete_cache_files

    def __str__(self) -> str:
        return("ProjectConfig. Name: {0}, delete_cache_files: {1}".format(self.proj_name, self.delete_cache_files))


class ProjectPaths:
    def __init__(self, proj_name: str, path_to_cache_dir: str,
                 path_to_proj_data_dir: str, path_to_git_folder: str) -> None:
        proj_folder = proj_name + '\\'
        # temporary source and diff folders
        self.path_to_cache_dir = path_to_cache_dir
        self.path_to_cache_current = path_to_cache_dir + \
            str(proj_folder) + 'current\\'
        self.path_to_cache_previous = path_to_cache_dir + proj_folder + 'previous\\'
        self.path_to_cache_sourcediff = path_to_cache_dir + proj_folder + 'sourcediff\\'
        # project data directory
        self.path_to_proj_data_dir = path_to_proj_data_dir + proj_folder
        # analytics database
        self.path_to_project_db = path_to_proj_data_dir + \
            proj_folder + proj_name + '_analytics.db'
        # initial graph db
        self.path_to_srctrail_db = path_to_proj_data_dir + \
            proj_folder + 'callgraphdb\\' + proj_name + '.srctrldb'
        # git source folder
        self.path_to_git_folder = path_to_git_folder

    def get_path_to_cache_current(self):
        return self.path_to_cache_current

    def get_path_to_cache_previous(self):
        return self.path_to_cache_previous

    def get_path_to_cache_sourcediff(self):
        return self.path_to_cache_sourcediff

    def get_path_to_proj_data_dir(self):
        return self.path_to_proj_data_dir

    def get_path_to_project_db(self):
        return self.path_to_project_db

    def get_path_to_srctrail_db(self):
        return self.path_to_srctrail_db

    def __str__(self) -> str:
        return("ProjectPaths. Analytics db: {0}".format(self.path_to_project_db))


class FileData():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # calculate dir path and file name
        for x in file_path.split('\\'):
            if(x.__contains__('.cpp')):
                file_name = x
        file_dir_path = file_path[0:len(file_path)-len(file_name)]

        self.file_dir_path = file_dir_path
        self.file_name = file_name

    def __str__(self) -> str:
        return("FileData [file_name: {0}, file_dir_path: {1}]"
               .format(self.file_name,
                       self.file_dir_path))


class CallCommitInfo:
    def __init__(self, src_file_data: FileData, calling_node: str, called_node: str,
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
        self.calling_node = calling_node
        self.called_node = called_node
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

    def get_calling_node(self) -> str:
        return self.calling_node

    def get_called_node(self) -> str:
        return self.called_node

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
        return("CallCommitInfo: source_node: {0}, called_node: {1}, start_date: {2}, end_date: {3}, file_path: {4}"
               .format(self.calling_node, self.called_node, self.commit_start_datetime, self.commit_end_datetime, self.file_path))


class CommitInfo:
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
        return("CommitInfo: commit_hash: {0}, commit_commiter_datetime: {1}, nr_modified_files: {2}"
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


class FileImport():
    def __init__(self, src_file_data: FileData,
                 import_file_name: str,
                 import_file_dir_path: str,
                 commit_hash_start=None, commit_start_datetime=None,
                 commit_hash_end=None, commit_end_datetime=None) -> None:
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.import_file_name = import_file_name
        self.import_file_dir_path = import_file_dir_path
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

    def get_import_file_name(self) -> str:
        return self.import_file_name

    def get_import_file_dir_path(self) -> str:
        return self.import_file_dir_path

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
        return("FileImport[src_file_path: {0}, import_file_name: {1}, import_file_dir_path: {2}]"
               .format(self.file_path, self.import_file_name, self.import_file_dir_path))


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
