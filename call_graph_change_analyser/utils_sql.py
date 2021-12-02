import logging
import os
import pandas
import sqlite3
from typing import Optional
from models import FileImport, CallCommitInfo, ActionClass

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
            cur.execute('''DROP TABLE source_changes''')
        except Exception as error:
            print("source_changes ", error)
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

    cur.execute('''CREATE TABLE IF NOT EXISTS source_changes
                (commit_hash text, commit_datetime text, source_file text, source_node text, target_node text, commit_author text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS node
                (id number, type text, name text, file_path text, start_datetime text, end_datetime text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS node_call
                (id number, type text, name text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS edge_call
                (type text, source_node_id number, target_node_id number, start_datetime text, end_datetime text)''')


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
                import_file_name text, import_file_dir_path text, 
                commit_hash_start text, commit_start_datetime text, 
                commit_hash_end text, commit_end_datetime text,
                primary key (file_path, import_file_name, import_file_dir_path))''')

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
                commit_hash_end text, commit_end_datetime text,
                primary key (file_path, function_long_name))''')


def save_source_change_row(
    commit_hash: str, commit_datetime: str, source_file: str,
    source_node: str, target_node: str, commit_author: str,
    cur: sqlite3.Cursor, con: sqlite3.Connection
):
    sql_statement = """INSERT INTO source_changes VALUES("""
    sql_statement = sql_statement + "'" + commit_hash + "', "
    sql_statement = sql_statement + "'" + commit_datetime + "', "
    sql_statement = sql_statement + "'" + source_file + "', "
    sql_statement = sql_statement + "'" + source_node + "', "
    sql_statement = sql_statement + "'" + target_node + "', "
    sql_statement = sql_statement + "'" + commit_author + "'"
    sql_statement = sql_statement + """)"""
    cur.execute(sql_statement)
    con.commit()


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

    print(sql_string)
    logging.debug(sql_string)
    cur.execute(sql_string)
    con_analytics_db.commit()


def update_file_imports(fis: list[FileImport],
                        path_to_project_db: str,
                        commit_hash_start: str,
                        commit_start_datetime: str,
                        commit_hash_end: Optional[str] = None,
                        commit_end_datetime: Optional[str] = None,):
    print("update_file_imports")
    if len(fis) > 0:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()
        for fi in fis:
            print(fi)
            insert_or_update_file_import(con_analytics_db=con_analytics_db,
                                         cur=cur,
                                         file_import=fi,
                                         commit_hash_start=commit_hash_start,
                                         commit_start_datetime=commit_start_datetime,
                                         commit_hash_end=commit_hash_end,
                                         commit_end_datetime=commit_end_datetime)
    else:
        logging.debug("no import_files")


def insert_or_update_file_import(con_analytics_db: sqlite3.Connection,
                                 cur: sqlite3.Cursor,
                                 file_import: FileImport,
                                 commit_hash_start: str,
                                 commit_start_datetime: str,
                                 commit_hash_end: Optional[str] = '',
                                 commit_end_datetime: Optional[str] = '',
                                 ):
    print("insert_or_update_file_import")
    print(file_import.get_file_name())
    sql_string = """INSERT INTO file_import 
                (file_name, file_dir_path, file_path, 
                import_file_name, import_file_dir_path, commit_hash_start, 
                commit_start_datetime, commit_hash_end, commit_end_datetime)
            VALUES 
                ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}') 
            ON CONFLICT (file_path, import_file_name, import_file_dir_path) 
            DO UPDATE SET commit_hash_start = excluded.commit_hash_start, 
                commit_start_datetime = excluded.commit_start_datetime,
                commit_hash_end = excluded.commit_hash_end,
                commit_end_datetime = excluded.commit_end_datetime;""".format(
        file_import.get_file_name(),
        file_import.get_file_dir_path(),
        file_import.get_file_path(),
        file_import.get_import_file_name(),
        file_import.get_import_file_dir_path(),
        commit_hash_start,
        commit_start_datetime, commit_hash_end, commit_end_datetime)

    print(sql_string)
    logging.debug(sql_string)
    cur.execute(sql_string)
    con_analytics_db.commit()


def update_call_commits(ccis: list[CallCommitInfo],
                        path_to_project_db: str,
                        commit_hash_start: str,
                        commit_start_datetime: str,
                        commit_hash_end: Optional[str] = None,
                        commit_end_datetime: Optional[str] = None,):
    print("update_call_commits")
    logging.debug('update_call_commits')
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
    print("insert_or_update_file_import")
    logging.debug(call_commit.get_file_name())
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
            "TODO, check if calling function is the same, else set end and insert", call_commit.get_action_class())
    else:
        logging.error("not valid Commit ActionClass",
                      call_commit.get_action_class())

    if execute_sql:
        print(sql_string)
        cur.execute(sql_string)
        con_analytics_db.commit()
    else:
        logging.warning("Nothing to insert call_commit",
                        call_commit.get_action_class())


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
