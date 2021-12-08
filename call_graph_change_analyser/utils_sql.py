import logging
import os
import pandas
import sqlite3
from typing import Optional, List

from pydriller.domain.commit import Commit, ModifiedFile
from models import FileImport, CallCommitInfo, ActionClass, FileData

import models
from models import ProjectPaths


def create_db_tables(proj_paths: ProjectPaths, drop=False):
    if not os.path.exists(str(proj_paths.get_path_to_proj_data_dir())):
        os.makedirs(str(proj_paths.get_path_to_proj_data_dir()))
    print("create_db_tables drop", drop)
    create_graph_based_tables(proj_paths.path_to_project_db, drop)
    create_commit_based_tables(proj_paths.path_to_project_db, drop)


# Initate database
def load_graph_data(proj_paths: ProjectPaths, delete_existings=False, load_init_graph=True, load_function_to_file=False):
    con_graph_db = sqlite3.connect(proj_paths.path_to_srctrail_db)
    print("proj_paths.path_to_srctrail_db: ", proj_paths.path_to_srctrail_db)
    con_analytics_db = sqlite3.connect(proj_paths.path_to_project_db)
    print("proj_paths.path_to_project_db: ", proj_paths.path_to_project_db)

    if load_init_graph:
        #load_initial_graph(con_graph_db=con_graph_db, con_analytics_db=con_analytics_db)
        load_graph_data(con_graph_db=con_graph_db,
                        con_analytics_db=con_analytics_db)

    if load_function_to_file:
        load_function_to_file(con_graph_db=con_graph_db,
                              con_analytics_db=con_analytics_db)


def create_graph_based_tables(path_to_project_db, drop=False):
    print("create_graph_based_tables drop", drop)

    con = sqlite3.connect(path_to_project_db)
    cur = con.cursor()

    if drop:
        try:
            cur.execute('''DROP TABLE node''')
        except Exception as error:
            print("node ", error)
        try:
            cur.execute('''DROP TABLE node_call''')
        except Exception as error:
            print("node_call ", error)
        try:
            cur.execute('''DROP TABLE edge_call''')
        except Exception as error:
            print("edge_call ", error)

    cur.execute('''CREATE TABLE IF NOT EXISTS node
                (id number, type text, name text, file_path text, start_datetime text, end_datetime text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS node_call
                (id number, type text, name text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS edge_call
                (type text, source_node_id number, target_node_id number, start_datetime text, end_datetime text)''')

    con.commit()
    cur.close()


def create_commit_based_tables(path_to_project_db, drop=False):
    print("create_commit_based_tables drop", drop)
    con = sqlite3.connect(path_to_project_db)
    cur = con.cursor()

    if drop:
        try:
            cur.execute('''DROP TABLE file_import''')
        except Exception as error:
            print("file_import ", error)
        try:
            cur.execute('''DROP TABLE git_commit''')
        except Exception as error:
            print("call_commit ", error)
        try:
            cur.execute('''DROP TABLE file_commit''')
        except Exception as error:
            print("call_commit ", error)
        try:
            cur.execute('''DROP TABLE function_commit''')
        except Exception as error:
            print("call_commit ", error)
        try:
            cur.execute('''DROP TABLE call_commit''')
        except Exception as error:
            print("call_commit ", error)
        try:
            cur.execute('''DROP TABLE function_to_file''')
        except Exception as error:
            print("function_to_file ", error)

    cur.execute('''CREATE TABLE IF NOT EXISTS file_import
                (file_name text, file_dir_path text, file_path text, 
                import_file_path text, import_file_name text, import_file_dir_path text, 
                commit_hash_start text, commit_start_datetime text, 
                commit_hash_end text, commit_end_datetime text, closed,
                primary key (file_path, import_file_path))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS git_commit
                (commit_hash text, commit_commiter_datetime text, author text, 
                in_main_branch integer, merge integer, 
                nr_modified_files integer, nr_deletions integer, nr_insertions integer, nr_lines integer,
                primary key (commit_hash))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS file_commit
                (file_name text, file_dir_path text, file_path text, 
                commit_hash text, 
                commit_commiter_datetime text, commit_file_name text, 
                commit_new_path text, commit_old_path text, change_type text,
                path_change integer,
                primary key (file_path, commit_hash))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS function_commit
                (file_name text, file_dir_path text, file_path text, 
                function_name text, function_long_name text, function_parameters text, function_nloc integer,
                commit_hash text, commit_commiter_datetime text, 
                commit_file_name text, commit_new_path text, commit_old_path text,
                path_change integer,
                primary key (file_path, function_long_name, commit_hash))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS call_commit
                (file_name text, file_dir_path text, file_path text, 
                calling_function text, called_function text, 
                action_class text,
                commit_hash_start text, commit_start_datetime text, 
                commit_hash_end text, commit_end_datetime text,
                primary key (file_path, calling_function, called_function))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS function_to_file
                (file_name text, file_dir_path text, file_path text, 
                function_name text, function_long_name text, function_parameters text, 
                commit_hash_start text, commit_start_datetime text, 
                commit_hash_end text, commit_end_datetime text, closed,
                primary key (file_path, function_long_name, commit_hash_start, commit_hash_end))''')

    con.commit()
    cur.close()


def load_graph_data(
    con_graph_db: sqlite3.Connection,
    con_analytics_db: sqlite3.Connection
):
    sql_statement = """SELECT * FROM node WHERE type in (4096,8192)"""
    df = pandas.read_sql_query(sql_statement, con_graph_db)
    df['type'].replace(models.NodeType, inplace=True)
    df_table_node_call = df[['id', 'type', 'serialized_name']]
    df_table_node_call.columns = ('id', 'type', 'name')
    print("df_table_node_call size", len(df_table_node_call))
    df_table_node_call.to_sql(
        'node_call', con_analytics_db, if_exists='replace', index=False)
    con_analytics_db.commit()

    sql_statement = """SELECT edge.id, edge.type, edge.source_node_id, edge.target_node_id
    FROM edge, node t_node, node s_node
    WHERE edge.target_node_id = t_node.id
    and edge.source_node_id = s_node.id
    and t_node.type in (4096,8192)
    and s_node.type in (4096,8192)
    and edge.type = 8"""
    df = pandas.read_sql_query(sql_statement, con_graph_db)
    df['type'].replace(models.EdgeType, inplace=True)
    df_table_edge_call = df[['type', 'source_node_id', 'target_node_id']]
    df_table_edge_call.columns = ('type', 'source_node_id', 'target_node_id')
    print("df_table_edge_call size", len(df_table_edge_call))
    df_table_edge_call.to_sql(
        'edge_call', con_analytics_db, if_exists='replace', index=False)
    con_analytics_db.commit()

    con_analytics_db.close()


def load_initial_graph(
    con_graph_db: sqlite3.Connection,
    con_analytics_db: sqlite3.Connection
):
    sql_statement = """select 
    edge.type as edge_type, NULL as edge_start_datetime, NULL as edge_end_datetime,
    s_node.id as source_node_id, s_node.type as source_node_type, s_node.serialized_name as source_node_name,
    t_node.id as target_node_id, t_node.type as target_node_type, t_node.serialized_name as target_node_name
    from edge, node as s_node, node as t_node
    where 
    edge.target_node_id = t_node.id 
    and edge.source_node_id = s_node.id
    and t_node.type in (4096,8192)"""
    df = pandas.read_sql_query(sql_statement, con_graph_db)
    df['edge_type'].replace(models.EdgeType, inplace=True)
    df['source_node_type'].replace(models.NodeType, inplace=True)
    df['target_node_type'].replace(models.NodeType, inplace=True)

    df_table_edge_call = df[['edge_type', 'source_node_id',
                             'target_node_id', 'edge_start_datetime', 'edge_end_datetime']]
    df_table_edge_call.columns = (
        'type', 'source_node_id', 'target_node_id', 'start_datetime', 'end_datetime')
    df_table_edge_call.to_sql(
        'edge_call', con_analytics_db, if_exists='replace', index=False)
    con_analytics_db.commit()

    df_table_node = df[['source_node_id',
                        'source_node_type', 'source_node_name']]
    df_table_node.columns = ('id', 'type', 'name')
    df_table_node_target = df[['target_node_id',
                               'target_node_type', 'target_node_name']]
    df_table_node_target.columns = ('id', 'type', 'name')

    df_table_node = df_table_node.append(df_table_node_target)
    df_table_node.drop_duplicates(inplace=True)
    df_table_node.to_sql('node', con_analytics_db,
                         if_exists='replace', index=False)
    con_analytics_db.commit()

    print(df_table_node.head(3))


def load_function_to_file_DEPRECATED(
    con_graph_db: sqlite3.Connection,
    con_analytics_db: sqlite3.Connection
) -> None:
    sql_statement = """SELECT
	edge.id as edge_id,
	edge.type as edge_type,
	edge.source_node_id as ,
	s_node.type,
	s_node.serialized_name,
	edge.target_node_id,
	t_node.type,
	t_node.serialized_name
	from edge, node s_node, node t_node
	where edge.source_node_id = s_node.id
	and edge.target_node_id = t_node.id"""
    df = pandas.read_sql_query(sql_statement, con_graph_db)
    df['edge_type'].replace(models.EdgeType, inplace=True)
    df['source_node_type'].replace(models.NodeType, inplace=True)
    df['target_node_type'].replace(models.NodeType, inplace=True)
    df.to_sql('edge_node_info', con_analytics_db,
              if_exists='replace', index=False)
    con_analytics_db.commit()


def get_graph_edges(path_to_project_db) -> pandas.DataFrame:
    con_analytics_db = sqlite3.connect(path_to_project_db)
    sql_statement = """
    select source_node_id, target_node_id from edge_call
    """
    return(pandas.read_sql_query(sql_statement, con_analytics_db))


def insert_git_commit(path_to_project_db: str, commit_hash: Optional[str] = None,
                      commit_commiter_datetime: Optional[str] = None, author: Optional[str] = None,
                      in_main_branch: Optional[bool] = None, merge: Optional[bool] = None,
                      nr_modified_files: Optional[int] = None, nr_deletions: Optional[int] = None,
                      nr_insertions: Optional[int] = None, nr_lines: Optional[int] = None):
    try:
        print("insert_git_commit")
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = """INSERT INTO git_commit 
                    (commit_hash, commit_commiter_datetime, author, 
                    in_main_branch, merge, 
                    nr_modified_files, nr_deletions, nr_insertions, nr_lines)
                VALUES 
                    ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}');""".format(
            commit_hash, commit_commiter_datetime, author, in_main_branch,
            merge, nr_modified_files, nr_deletions, nr_insertions, nr_lines)

        cur.execute(sql_string)
        con_analytics_db.commit()
        cur.close()
    except Exception as er:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(er).__name__, er.args)
        print("IntegrityError. UNIQUE failed for [{0}] ".format(commit_hash))
        logging.error("[{0}] ".format(commit_hash))
        logging.error(err_message)


def insert_file_commit(path_to_project_db: str, mod_file_data: FileData,
                       commit_hash: str, commit_commiter_datetime: str,
                       commit_file_name: str,
                       commit_new_path: str, commit_old_path: str,
                       change_type: str):
    try:
        print("insert_file_commit")
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        path_change = 0 if commit_new_path == commit_old_path else 1

        sql_string = """INSERT INTO file_commit 
                    (file_name, file_dir_path, file_path, 
                    commit_hash, commit_commiter_datetime, commit_file_name, 
                    commit_new_path, commit_old_path, change_type, path_change)
                VALUES 
                    ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}');""".format(
            mod_file_data.get_file_name(), mod_file_data.get_file_dir_path(
            ), mod_file_data.get_file_path(),
            commit_hash, commit_commiter_datetime, commit_file_name,
            commit_new_path, commit_old_path, change_type, path_change)

        cur.execute(sql_string)
        con_analytics_db.commit()
        cur.close()
    except Exception as err:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        print("IntegrityError. UNIQUE failed for [{0},{1}] ".format(
            commit_hash, mod_file_data.get_file_path()))
        logging.error("[{0},{1}] ".format(
            commit_hash, mod_file_data.get_file_path()))
        logging.error(err_message)


def get_previous_file_import_long_names(path_to_project_db: str, mod_file_data: FileData):
    try:

        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = """SELECT import_file_path 
        FROM file_import 
        WHERE file_path = '{0}'
        AND closed = 0""".format(mod_file_data.get_file_path())

        print(sql_string)
        cur.execute(sql_string)
        result = cur.fetchall()
        print(result)

        con_analytics_db.commit()
        cur.close()
        return result

    except Exception as err:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
        return None


def update_file_imports(mod_file_data: FileData, fis: List[FileImport],
                        path_to_project_db: str,
                        commit_hash: str,
                        commit_datetime: str):
    print("update_file_imports")
    try:
        # TODO change to parsing previous file.... 
        previous_file_import_long_names = get_previous_file_import_long_names(
            path_to_project_db, mod_file_data)
        curr_file_imports_long_names = [
            f.get_import_file_path() for f in fis]

        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        # get existing in prev but not in curr
        added_functions = list(
            set(curr_file_imports_long_names) - set(previous_file_import_long_names))
        # get existing in prev but not in curr
        deleted_functions = list(
            set(previous_file_import_long_names) - set(curr_file_imports_long_names))
        # get intersection
        unchanged_functions = list(set(curr_file_imports_long_names).intersection(
            previous_file_import_long_names))

        # handle added file_imports
        for fi in [fi for fi in fis if fi.get_import_file_path() in added_functions]:
            sql_string = """INSERT INTO file_import 
                        (file_name, file_dir_path, file_path, 
                        import_file_name, import_file_path, import_file_dir_path, 
                        commit_hash_start, commit_start_datetime)
                    VALUES 
                        ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}');""".format(
                fi.get_file_name(),  fi.get_file_dir_path(), fi.get_file_path(),
                fi.get_import_file_name(), fi.get_import_file_path(), fi.get_import_file_dir_path(),
                commit_hash, commit_datetime)
            cur.execute(sql_string)

        # handle deleted file_imports
        for ln in deleted_functions:
            sql_string = """UPDATE file_import SET 
                        commit_hash_end='{0}', commit_end_datetime='{1}'
                        WHERE 
                        file_path='{2}'
                        AND import_file_path='{3}';""".format(
                commit_hash, commit_datetime,
                mod_file_data.get_file_path(), ln)
            cur.execute(sql_string)

        # handle unchanged file_imports
        for fi in [f for f in fis if f.get_import_file_path() in unchanged_functions]:
            print(fi)
            sql_string = """UPDATE file_import SET 
                        commit_hash_start='{0}', commit_start_datetime='{1}'
                        WHERE 
                        file_path='{2}'
                        AND import_file_path='{3}';""".format(
                commit_hash, commit_datetime,
                mod_file_data.get_file_path(), fi.get_import_file_path())
            cur.execute(sql_string)

        con_analytics_db.commit()

    except Exception as err:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)


def insert_function_commit(path_to_project_db: str, mod_file: ModifiedFile, commit: Commit):
    mod_file_data = FileData(str(mod_file._new_path))
    try:
        changed_methods = mod_file.changed_methods
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        for cm in changed_methods:
            print(cm)
            print(cm.__hash__())
            print(cm.parameters)

            params = ','.join(cm.parameters)

            path_change = 0 if mod_file.new_path == mod_file.old_path else 1

            sql_string = """INSERT INTO function_commit 
                        (file_name, file_dir_path, file_path, 
                        function_name, function_long_name, function_parameters, function_nloc,
                        commit_hash, commit_commiter_datetime, 
                        commit_file_name, commit_new_path, commit_old_path,
                        path_change)
                    VALUES 
                        ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}');""".format(
                mod_file_data.get_file_name(),
                mod_file_data.get_file_dir_path(), mod_file_data.get_file_path(),
                cm.name, cm.long_name, params, cm.nloc,
                commit.hash, commit.committer_date,
                mod_file.filename, mod_file.new_path, mod_file.old_path,
                path_change)

            cur.execute(sql_string)

        con_analytics_db.commit()
        cur.close()
    except Exception as err:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)


def get_previous_active_functions_in_file(path_to_project_db: str, mod_file: ModifiedFile) -> List[str]:
    mod_file_data = FileData(str(mod_file._new_path))
    try:

        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = """SELECT function_long_name 
        FROM function_to_file 
        WHERE file_path = '{0}'
        AND closed = 0""".format(mod_file_data.get_file_path())

        cur.execute(sql_string)
        result = cur.fetchall()
        print(result)

        con_analytics_db.commit()
        cur.close()
        return result

    except Exception as err:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
        return None


def update_function_to_file(path_to_project_db: str, mod_file: ModifiedFile,
                            commit: Commit, previous_active_functions_in_file: List[str]):
    mod_file_data = FileData(str(mod_file._new_path))
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        commit_previous_functions = [
            f.long_name for f in mod_file.methods_before]
        commit_current_functions = [f.long_name for f in mod_file.methods]
        commit_changed_functions = [
            f.long_name for f in mod_file.changed_methods]

        # get added functions (existing in curr but not prev)
        added_functions = list(
            set(commit_current_functions) - set(commit_previous_functions))
        # get deleted functions (existing in prev but not in curr)
        deleted_functions = list(
            set(commit_previous_functions) - set(commit_current_functions))
        # get just changed functions
        changed_functions = list(
            set(commit_changed_functions) - set(added_functions) - set(deleted_functions))
        # get not changed functions
        unchanged_functions = list(
            set(commit_previous_functions).intersection(commit_current_functions) - set(changed_functions))

        # mod_file.methods include added, changed and unchanged
        for cm in mod_file.methods:
            print(cm.long_name)
            params = ','.join(cm.parameters)
            if (cm.long_name in added_functions) or (cm.long_name in changed_functions) or (cm.long_name in unchanged_functions):
                sql_string = """INSERT INTO function_to_file 
                            (file_name, file_dir_path, file_path, 
                            function_name, function_long_name, function_parameters,
                            commit_hash_start, commit_start_datetime, closed)
                        VALUES 
                            ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}',{8})
                        ON CONFLICT (file_path, function_long_name, commit_hash_start, commit_hash_end) 
                        DO UPDATE SET commit_hash_start = excluded.commit_hash_start, 
                            commit_start_datetime = excluded.commit_start_datetime;""".format(
                    mod_file_data.get_file_name(),
                    mod_file_data.get_file_dir_path(),
                    mod_file_data.get_file_path(),
                    cm.name, cm.long_name, params,
                    commit.hash, commit.committer_date, 0)
                cur.execute(sql_string)

        for cm in mod_file.changed_methods:
            if cm.long_name in deleted_functions:
                print("Deleted function_to_file: {0}".format(cm.long_name))
                logging.debug(
                    "Deleted function_to_file: {0}".format(cm.long_name))
                params = ','.join(cm.parameters)

                if cm.long_name in previous_active_functions_in_file:
                    sql_string = """UPDATE function_to_file SET 
                                commit_hash_end='{0}', commit_end_datetime='{1}', closed = 1
                                WHERE 
                                file_path='{2}'
                                AND function_long_name='{3}';""".format(
                        commit.hash, commit.committer_date,
                        mod_file_data.get_file_path(), cm.long_name)
                else:
                    # because we work from tag to tag it might be that the entry does not exist
                    sql_string = """INSERT INTO function_to_file 
                                (file_name, file_dir_path, file_path, 
                                function_name, function_long_name, function_parameters,
                                commit_hash_start, commit_start_datetime, 
                                commit_hash_end, commit_end_datetime, closed)
                            VALUES
                                ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}',{10})
                            ON CONFLICT (file_path, function_long_name, commit_hash_start, commit_hash_end) 
                            DO UPDATE SET commit_hash_end = excluded.commit_hash_end, 
                                commit_end_datetime = excluded.commit_end_datetime,
                                closed = excluded.closed;""".format(
                        mod_file_data.get_file_name(),
                        mod_file_data.get_file_dir_path(),
                        mod_file_data.get_file_path(),
                        cm.name, cm.long_name, params,
                        commit.hash, commit.committer_date,
                        commit.hash, commit.committer_date, 1)
                cur.execute(sql_string)

        con_analytics_db.commit()
        cur.close()
    except Exception as err:
        con_analytics_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)


def update_call_commits(ccis: List[CallCommitInfo],
                        path_to_project_db: str,
                        commit_hash_start: str,
                        commit_start_datetime: str,
                        commit_hash_end: Optional[str] = None,
                        commit_end_datetime: Optional[str] = None,):
    if len(ccis) > 0:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()
        for cci in ccis:
            print(cci)
            insert_or_update_call_commit(con_analytics_db=con_analytics_db,
                                         cur=cur,
                                         call_commit=cci,
                                         commit_hash_start=commit_hash_start,
                                         commit_start_datetime=commit_start_datetime,
                                         commit_hash_end=commit_hash_end,
                                         commit_end_datetime=commit_end_datetime)
    else:
        logging.debug("no call_commits")


def insert_or_update_call_commit(con_analytics_db: sqlite3.Connection,
                                 cur: sqlite3.Cursor,
                                 call_commit: CallCommitInfo,
                                 commit_hash_start: str,
                                 commit_start_datetime: str,
                                 commit_hash_end: Optional[str] = '',
                                 commit_end_datetime: Optional[str] = '',
                                 ):
    execute_sql = False

    if call_commit.get_action_class() is ActionClass.DELETE:
        commit_hash_end = commit_hash_start
        commit_end_datetime = commit_start_datetime
        sql_string = """INSERT INTO call_commit 
                    (file_name, file_dir_path, file_path, 
                    calling_function, called_function, commit_hash_end, commit_end_datetime)
                VALUES 
                    ('{0}','{1}','{2}','{3}','{4}','{5}','{6}') 
                ON CONFLICT (file_path, calling_function, called_function) 
                DO UPDATE SET commit_hash_end = excluded.commit_hash_end,
                    commit_end_datetime = excluded.commit_end_datetime;""".format(
            call_commit.get_file_name(),
            call_commit.get_file_dir_path(),
            call_commit.get_file_path(),
            call_commit.get_calling_function(),
            call_commit.get_called_function(),
            commit_hash_end, commit_end_datetime)
        execute_sql = True
    elif call_commit.get_action_class() is ActionClass.INSERT or call_commit.get_action_class() is ActionClass.ADD:
        sql_string = """INSERT INTO call_commit 
                    (file_name, file_dir_path, file_path, 
                    calling_function, called_function, 
                    commit_hash_start, commit_start_datetime)
                VALUES 
                    ('{0}','{1}','{2}','{3}','{4}','{5}','{6}') 
                ON CONFLICT (file_path, calling_function, called_function) 
                DO UPDATE SET commit_hash_start = excluded.commit_hash_start, 
                    commit_start_datetime = excluded.commit_start_datetime;""".format(
            call_commit.get_file_name(),
            call_commit.get_file_dir_path(),
            call_commit.get_file_path(),
            call_commit.get_calling_function(),
            call_commit.get_called_function(),
            commit_hash_start, commit_start_datetime)
        execute_sql = True
    elif call_commit.get_action_class() is ActionClass.MOVE:
        logging.debug(
            "TODO, check if calling function is the same, else set end and insert: {0}".function(call_commit.get_action_class()))
    else:
        logging.error("not valid Commit ActionClass: {0}".function(
            call_commit.get_action_class()))

    if execute_sql:
        print(sql_string)
        cur.execute(sql_string)
        con_analytics_db.commit()
    else:
        logging.warning("Nothing to insert call_commit: {0}".function(
            call_commit.get_action_class()))


"""
create table edge_node_info (edge_id, edge_type, source_node_id, source_node_type, source_node_name, target_node_id, target_node_type, target_node_name)

insert into edge_node_info (edge_id, edge_type, source_node_id, source_node_type, source_node_name, target_node_id, target_node_type, target_node_name)
	SELECT
	edge.id,
	edge.type,
	edge.source_node_id,
	s_node.type,
	s_node.serialized_name,
	edge.target_node_id,
	t_node.type,
	t_node.serialized_name
	from edge, node s_node, node t_node
	where edge.source_node_id = s_node.id
	and edge.target_node_id = t_node.id
"""
