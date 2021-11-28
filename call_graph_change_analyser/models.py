# %%
from datetime import datetime
from enum import Enum
from typing import Optional, List

# Classes
# class CommitInfo:


class ProjectConfig:
    def __init__(
            self,  proj_name:
            str, proj_lang: str, commit_file_types: List[str], path_to_src_diff_jar: str,
            path_to_repo: str,
            start_repo_date: datetime, end_repo_date: Optional[datetime]) -> None:
        self.proj_name = proj_name
        self.proj_lang = proj_lang
        self.commit_file_types = commit_file_types
        self.path_to_repo = path_to_repo
        self.start_repo_date = start_repo_date
        self.end_repo_date = end_repo_date
        self.path_to_src_diff_jar = path_to_src_diff_jar

    def get_path_to_repo(self):
        return self.path_to_repo

    def get_commit_file_types(self):
        return self.commit_file_types

    def get_start_repo_date(self):
        return self.start_repo_date

    def get_end_repo_date(self):
        return self.end_repo_date

    def get_path_to_src_diff_jar(self):
        return self.path_to_src_diff_jar


class ProjectPaths:
    def __init__(self, proj_name: str, path_to_cache_dir: str,
                 path_to_proj_data_dir: str, path_to_git_folder: str) -> None:
        proj_folder = proj_name + '\\'
        # source and diff folders
        self.path_to_cache_dir = path_to_cache_dir
        self.path_to_cache_current = path_to_cache_dir + \
            str(proj_folder) + 'current\\'
        self.path_to_cache_previous = path_to_cache_dir + proj_folder + 'previous\\'
        self.path_to_cache_sourcediff = path_to_cache_dir + proj_folder + 'sourcediff\\'
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
    def __init__(self, src_file_data: FileData, call_node: str, called_node: str,
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
        self.call_node = call_node
        self.called_node = called_node
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
        return("CallCommitInfo: source_node: {0}, called_node: {1}, start_date: {2}, end_date: {3}, file_path: {4}"
               .format(self.call_node, self.called_node, self.commit_start_datetime, self.commit_end_datetime, self.file_path))


class FileImport():
    def __init__(self, src_file_data: FileData,
                 import_file_name: str,
                 import_file_dir_path: str,
                 commit_hash_start=None, commit_start_datetime=None,
                 commit_hash_end=None, commit_end_datetime=None) -> None:
        self.src_file_name = src_file_data.file_name
        self.src_file_dir_path = src_file_data.file_dir_path
        self.src_file_path = src_file_data.file_path
        self.import_file_name = import_file_name
        self.import_file_dir_path = import_file_dir_path
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_import_file_name(self) -> str:
        return self.import_file_name

    def __str__(self) -> str:
        return("FileImport[src_file_path: {0}, import_file_name: {1}, import_file_dir_path: {2}]"
               .format(self.src_file_path, self.import_file_name, self.import_file_dir_path))


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
