import os
import pandas
import sqlite3
from typing import Optional
from models import FileImport

import models
from models import ProjectPaths


# Initate database
def initate_analytics_db(proj_paths: ProjectPaths, drop=False, load_init_graph=True, load_function_to_file=False):
    create_graph_based_tables(proj_paths.path_to_project_db, drop)

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
        try:
            cur.execute('''DROP TABLE function_to_file''')
        except Exception as error:
            print("function_to_file ", error)
        try:
            cur.execute('''DROP TABLE file_import''')
        except Exception as error:
            print("file_import ", error)

    cur.execute('''CREATE TABLE IF NOT EXISTS source_changes
                (commit_hash text, commit_datetime text, source_file text, source_node text, target_node text, commit_author text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS node
                (id number, type text, name text, file_path text, start_datetime text, end_datetime text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS node_call
                (id number, type text, name text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS edge_call
                (type text, source_node_id number, target_node_id number, start_datetime text, end_datetime text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS function_to_file
                (function_node_id number, file_node_id number, nr_calls number)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS file_import
                (file_name text, dir_path text, import_file_name text, import_file_dir_path text, start_datetime text, end_datetime text)''')


def create_commit_based_tables(path_to_project_db, drop=False):
    con = sqlite3.connect(path_to_project_db)
    cur = con.cursor()

    if drop:
        try:
            cur.execute('''DROP TABLE file_import''')
        except Exception as error:
            print("file_import ", error)
        try:
            cur.execute('''DROP TABLE call_commit''')
        except Exception as error:
            print("call_commit ", error)

    cur.execute('''CREATE TABLE IF NOT EXISTS file_import
                (file_name text, file_dir_path text, file_path text, import_file_name text, import_file_dir_path text, commit_hash_start text, commit_start_datetime text, commit_hash_end text, commit_end_datetime text,
                primary key (file_path, import_file_name, import_file_dir_path ))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS call_commit
                (file_name text, file_dir_path text, file_path text, calling_function_node text, called_function_node text, commit_hash_start text, commit_start_datetime text, commit_hash_end text, commit_end_datetime text,
                primary key (file_path, calling_function_node, called_function_node ))''')


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


def load_function_to_file(
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


def update_file_imports(fis: list[FileImport],
                        path_to_project_db: str,
                        commit_hash_start: str,
                        commit_start_datetime: str,
                        commit_hash_end: Optional[str] = None,
                        commit_end_datetime: Optional[str] = None,):
    print("update_file_imports")
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
    cur.execute(sql_string)
    con_analytics_db.commit()


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
