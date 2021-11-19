import os
import pandas
import sqlite3

import models
from models import ProjectPaths


# Initate database 
def initate_analytics_db(proj_paths: ProjectPaths, drop=False, load_init_graph=True, load_function_to_file = False):
    create_tables(proj_paths.path_to_project_db, drop)

    con_graph_db = sqlite3.connect(proj_paths.path_to_srctrail_db)
    print("proj_paths.path_to_srctrail_db: ", proj_paths.path_to_srctrail_db)
    con_analytics_db = sqlite3.connect(proj_paths.path_to_project_db)
    print("proj_paths.path_to_project_db: ", proj_paths.path_to_project_db)

    if load_init_graph:
        #load_initial_graph(con_graph_db=con_graph_db, con_analytics_db=con_analytics_db)
        load_g_data(con_graph_db=con_graph_db, con_analytics_db=con_analytics_db)

    if load_function_to_file:
        load_function_to_file(con_graph_db=con_graph_db, con_analytics_db=con_analytics_db)

def create_tables(path_to_project_db, drop=False):
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
            print("edge_call ", error)

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



def save_source_change_row (
        commit_hash: str, commit_datetime: str, source_file: str, 
        source_node: str, target_node: str, commit_author: str,
        cur: sqlite3.Cursor, con: sqlite3.Connection
    ):
    sql_statement = """INSERT INTO source_changes VALUES("""
    sql_statement =  sql_statement + "'" + commit_hash + "', "
    sql_statement =  sql_statement + "'" + commit_datetime + "', "
    sql_statement =  sql_statement + "'" + source_file + "', "
    sql_statement =  sql_statement + "'" + source_node + "', "
    sql_statement =  sql_statement + "'" + target_node + "', "
    sql_statement =  sql_statement + "'" + commit_author + "'"
    sql_statement =  sql_statement + """)"""
    cur.execute(sql_statement)
    con.commit()


def load_g_data(
    con_graph_db: sqlite3.Connection,
    con_analytics_db: sqlite3.Connection
):
    sql_statement = """SELECT * FROM node WHERE type in (4096,8192)"""
    df = pandas.read_sql_query(sql_statement, con_graph_db)
    df['type'].replace(models.NodeType, inplace=True)
    df_table_node_call = df[['id','type','serialized_name']]
    df_table_node_call.columns = ('id','type','name')
    print("df_table_node_call size", len(df_table_node_call))
    df_table_node_call.to_sql('node_call', con_analytics_db, if_exists='replace', index=False)
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
    df_table_edge_call.columns = ('type', 'source_node_id','target_node_id')
    print("df_table_edge_call size", len(df_table_edge_call))
    df_table_edge_call.to_sql('edge_call', con_analytics_db, if_exists='replace', index=False)
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

    df_table_edge_call = df[['edge_type', 'source_node_id', 'target_node_id', 'edge_start_datetime' ,'edge_end_datetime']]
    df_table_edge_call.columns = ('type', 'source_node_id','target_node_id','start_datetime','end_datetime')
    df_table_edge_call.to_sql('edge_call', con_analytics_db, if_exists='replace', index=False)
    con_analytics_db.commit()

    df_table_node = df[['source_node_id','source_node_type','source_node_name']]
    df_table_node.columns = ('id','type','name')
    df_table_node_target = df[['target_node_id','target_node_type','target_node_name']]
    df_table_node_target.columns = ('id','type','name')

    df_table_node = df_table_node.append(df_table_node_target)
    df_table_node.drop_duplicates(inplace=True)
    df_table_node.to_sql('node', con_analytics_db, if_exists='replace', index=False)
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
    df.to_sql('edge_node_info', con_analytics_db, if_exists='replace', index=False)
    con_analytics_db.commit()




def get_graph_edges(path_to_project_db) -> pandas.DataFrame:
    con_analytics_db = sqlite3.connect(path_to_project_db)
    sql_statement = """
    select source_node_id, target_node_id from edge_call
    """
    return(pandas.read_sql_query(sql_statement, con_analytics_db))


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