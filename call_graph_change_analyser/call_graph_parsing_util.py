# %%
from sqlite3.dbapi2 import OperationalError
import subprocess
from subprocess import *
from typing import Optional
from git import Repo
import os
import platform
from shutil import copy as shutil_copy
import sqlite3
from git.refs import log
import pandas
import logging
import re
import collections

import time
# from stopwatch import Stopwatch, profile
from datetime import datetime

from models import ProjectConfig, ProjectPaths


def sctWrapper(cgdbpath, *args):
    # print("Exists dir: ", os.path.exists(cgdbpath))
    file_path = os.path.join(cgdbpath, args[len(args)-1])
    logging.debug(file_path)
    # print("File path: ", file_path)
    # print("Exists file: ", args[len(args)-1], os.path.exists(file_path))

    shell_value = True
    if platform.system() == 'Linux':
        shell_value = False

    process = Popen(['sourcetrail', 'index']+list(args),
                    stdout=PIPE, stderr=PIPE, cwd=cgdbpath, shell=shell_value)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith(b'\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split(b'\n')
    if stderr != '':
        ret += stderr.split(b'\n')
    ret.remove(b'')
    logging.debug("ret ln1 {0}".format(ret[0]))
    return ret

# TODO define re-processing startegy


def parse_source_graph(proj_name: str, path_to_cache_cg_dbs_dir: str, commit_hash: str, srctrl_db_name: str) -> None:
    proj_srctrl_config_file_name = proj_name + \
        '.srctrlprj'  # original file was copied to this path
    proj_commit_srctrl_config_file_name = proj_name + commit_hash + '.srctrlprj'

    # if configuration file for parsing the source graph does not exist, create
    if not os.path.exists(os.path.join(path_to_cache_cg_dbs_dir, proj_commit_srctrl_config_file_name)):
        make_config_file_copy(orig_file_dir=path_to_cache_cg_dbs_dir, orig_file_name=proj_srctrl_config_file_name,
                              target_file_dir=path_to_cache_cg_dbs_dir, target_file_name=proj_commit_srctrl_config_file_name)
    else:
        logging.info("Commit srctrl prj config file already exists.")

    if not os.path.exists(os.path.join(path_to_cache_cg_dbs_dir, srctrl_db_name)):
        # creates srctrl db for the commit
        curr_src_args = [proj_commit_srctrl_config_file_name]
        result = sctWrapper(path_to_cache_cg_dbs_dir, *curr_src_args)
    else:
        logging.info("Commit srctrl database already exists.")


def exists_in_raw_cg_db(proj_name: str, path_to_cache_cg_dbs_dir: str, commit_hash: str):
    # check if call graph data for commit exist
    raw_cg_table_exists = False
    raw_cg_db_path = os.path.join(path_to_cache_cg_dbs_dir,
                                  (proj_name + '_raw_cg.db'))
    con_commit_cg_db = sqlite3.connect(raw_cg_db_path)
    cur = con_commit_cg_db.cursor()
    try:
        sql_string = """SELECT *
            FROM '{0}'
            LIMIT 1;""".format(commit_hash)
        cur.execute(sql_string)
        cur.fetchone()
        logging.debug(cur.rowcount)

        if(cur.rowcount > 0):
            raw_cg_table_exists = True
            logging.debug("Table '{0} already exists'".format(commit_hash))
        cur.close()
    except OperationalError:
        logging.info("Table '{0} does not exists'".format(commit_hash))
    except Exception as err:
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
    return raw_cg_table_exists


def save_cg_data_all(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    logging.debug("Start save_cg_data_all")
    path_to_cache_cg_dbs_dir = proj_paths.get_path_to_cache_cg_dbs_dir()
    path_to_project_db = proj_paths.get_path_to_project_db()
    path_to_src_files_raw_cg = proj_paths.get_str_path_to_src_files()
    logging.debug(path_to_src_files_raw_cg)

    con_analytics_db = sqlite3.connect(path_to_project_db)

    sql_statement = """select * from git_commit;"""
    git_commit_df = pd.read_sql_query(sql_statement, con_analytics_db)
    logging.debug("Nr of commits: {0}".format(len(git_commit_df)))

    for g_idx, g in git_commit_df.iterrows():
        logging.debug("commit_hash: {0}".format(g['commit_hash']))
        save_cg_data_for_commit(proj_config.get_proj_name(),
                                path_to_cache_cg_dbs_dir, g['commit_hash'],
                                proj_config.get_delete_cg_src_db())


def load_source_graph_for_commit(proj_name: str, path_to_cache_cg_dbs_dir: str, commit_hash: str, delete_cg_src_db: bool):
    srctrl_db_name = proj_name + commit_hash + '.srctrldb'
    path_to_srctrl_db = os.path.join(path_to_cache_cg_dbs_dir,
                                     srctrl_db_name)
    # if srctrl database does not exist, create
    if not exists_in_raw_cg_db(
            proj_name, path_to_cache_cg_dbs_dir, commit_hash):
        # save general source info from parsing component
        parse_source_graph(proj_name, path_to_cache_cg_dbs_dir,
                           commit_hash, srctrl_db_name)
    else:
        logging.info(
            "Table '{0}' already exists in raw_cg_db_path".format(commit_hash))

    logging.debug("delete_cg_src_db {0}".format(delete_cg_src_db))
    if delete_cg_src_db:
        if os.path.isfile(path_to_srctrl_db):
            os.remove(path_to_srctrl_db)
        else:  # Show an error ##
            logging.debug(
                "Error: {0} file not found".format(path_to_srctrl_db))


def save_cg_data_for_commit(proj_name: str, path_to_cache_cg_dbs_dir: str, commit_hash: str, delete_cg_src_db: bool):
    raw_cg_db_path = os.path.join(path_to_cache_cg_dbs_dir,
                                  (proj_name + '_raw_cg.db'))
    srctrl_db_name = proj_name + commit_hash + '.srctrldb'
    path_to_srctrl_db = os.path.join(path_to_cache_cg_dbs_dir,
                                     srctrl_db_name)
    # generate source graph file
    load_source_graph_for_commit(
        proj_name, path_to_cache_cg_dbs_dir, commit_hash, delete_cg_src_db)

    # retreive cg info from genearted db from parsing componen and save focused cg data
    save_curr_cg_from_source_graph_parcing(
        path_to_srctrl_db, raw_cg_db_path, commit_hash)


def save_curr_cg_from_source_graph_parcing(path_to_srctrl_db: str, raw_cg_db_path: str, commit_hash: str):
    try:
        con_commit_cg_db = sqlite3.connect(raw_cg_db_path)
        cur = con_commit_cg_db.cursor()
        try:
            sql_string = """SELECT *
                FROM '{0}'
                LIMIT 1;""".format(commit_hash)
            cur.execute(sql_string)
            cur.fetchone()
            logging.debug(cur.rowcount)
        except Exception as err:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            err_message = template.format(type(err).__name__, err.args)
            logging.error(err_message)

        if(cur.rowcount <= 0):
            sql_string = """select
                --edge.type as edge_type, --NULL as edge_start_datetime, NULL as edge_end_datetime,
                s_node.id as source_node_id, s_node.type as source_node_type, s_node.serialized_name as source_node_name,
                t_node.id as target_node_id, t_node.type as target_node_type, t_node.serialized_name as target_node_name,
                s_file.path as s_file_path,
                t_file.path as t_file_path,
                "" as mod_type,
                0 as s_node_change,
                0 as t_node_change
                from edge, node as s_node, node as t_node,
                source_location as s_src_loc, source_location as t_src_loc,
                occurrence as s_oc, occurrence as t_oc,
                file as s_file, file as t_file
                where
                edge.target_node_id = t_node.id
                and edge.source_node_id = s_node.id
                and t_node.type in (4096,8192) -- fuction and methods
                and edge.type = 8 -- call
                and s_oc.element_id = s_node.id
                and s_file.id = s_src_loc.file_node_id
                and s_src_loc.id = s_oc.source_location_id
                and t_src_loc.id = t_oc.source_location_id
                and t_oc.element_id = t_node.id
                and t_file.id = t_src_loc.file_node_id
                and s_src_loc.type = 0
                and t_src_loc.type = 0;"""

            con_srctrl_db = sqlite3.connect(path_to_srctrl_db)
            df = pandas.read_sql_query(sql_string, con_srctrl_db)
            con_srctrl_db.commit()
            con_srctrl_db.close()

            # save to commit call graph db in table with commit_hash name
            con_commit_cg_db = sqlite3.connect(raw_cg_db_path)
            df.to_sql(
                commit_hash, con_commit_cg_db, if_exists='replace', index=False)
            con_commit_cg_db.commit()
            con_commit_cg_db.close()
        else:
            logging.info(
                "Table '{0}' already exist, don't overwrite".format(commit_hash))

    except Exception as err:
        # TODO handle db connection errors
        # con_analytics_db.rollback()
        # cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
        return None


def get_node_name_nosrcref_dupplicates(set_call_edges: set):
    val_curr = collections.Counter(set_call_edges)
    uniqueList_curr = list(set_call_edges)
    val_node_name_nosrcref_dupplicates = {}
    n = 0
    for i in uniqueList_curr:
        if val_curr[i] >= 2:
            n += 1
            print(n, i, "-", val_curr[i])
            val_node_name_nosrcref_dupplicates[i] = val_curr[i]
    return val_node_name_nosrcref_dupplicates

# TODO delete


def save_cg_diffs(proj_name: str, path_to_cache_cg_dbs_dir: str, commit_hash: str,
                  commit_date: datetime, path_to_project_db: str, path_to_edge_hist_db: str):
    """We care about absolute calls between functions. if the same function B is called twice in function A, and in the next commit
    one of the calls is dropped, the call graph remains the same because function A is still calling function B."""
    logging.debug("------- commit_hash: {0}".format(commit_hash))
    con_analytics_db = sqlite3.connect(path_to_project_db)
    r = get_next_hash(con_analytics_db, commit_date)
    next_commit_hash = None if r is None else r[0]
    next_commit_date = None if r is None else r[1]
    raw_cg_db_path = os.path.join(path_to_cache_cg_dbs_dir,
                                  (proj_name + '_raw_cg.db'))
    if not os.path.exists(str(raw_cg_db_path)):
        logging.ERROR(
            "raw_cg_db_path does not exist! {0}".format(raw_cg_db_path))

    path_to_edge_hist_db = path_to_edge_hist_db
    eh_target_db_path = path_to_edge_hist_db if path_to_edge_hist_db is not None else raw_cg_db_path

    # example glucosio-android0ff0d3fae09581ea490794eaa82b4279fabeb7f4.srctrldb
    try:
        con_raw_cg_db = sqlite3.connect(raw_cg_db_path)
        cur = con_raw_cg_db.cursor()
        con_edge_hist_db = sqlite3.connect(eh_target_db_path)
        pattern = re.compile(r"\<\d+\:\d+\>")

        if next_commit_hash is not None:
            # TODO split for testability
            sql_string = """SELECT '{0}' as commit_hash,
                '{1}' as commit_date,
                'curr' as commit_type,
                *
                FROM '{0}' as curr_t
                WHERE NOT EXISTS (
                    SELECT *
                    FROM  "{2}" as next_t
                    WHERE next_t.s_file_path = curr_t.s_file_path
                    AND next_t.t_file_path = curr_t.t_file_path
                    AND next_t.source_node_name = curr_t.source_node_name
                    AND next_t.target_node_name = curr_t.target_node_name
                );""".format(commit_hash, commit_date, next_commit_hash)

            raw_cg_df_curr = pandas.read_sql_query(
                sql_string, con_raw_cg_db)

            sql_string = """SELECT "{0}" as commit_hash,
                '{1}' as commit_date,
                'next' as commit_type,
                *
                FROM '{0}' as next_t
                WHERE NOT EXISTS (
                    SELECT *
                    FROM  "{2}" as curr_t
                    WHERE next_t.s_file_path = curr_t.s_file_path
                    AND next_t.t_file_path = curr_t.t_file_path
                    AND next_t.source_node_name = curr_t.source_node_name
                    AND next_t.target_node_name = curr_t.target_node_name
                );""".format(next_commit_hash, next_commit_date, commit_hash)

            raw_cg_df_next = pandas.read_sql_query(
                sql_string, con_raw_cg_db)

            # name of node might include line number in code
            raw_cg_df_curr['source_node_name_nosrcref'] = raw_cg_df_curr['source_node_name'].str.replace(
                pattern, '<:>')
            raw_cg_df_curr['target_node_name_nosrcref'] = raw_cg_df_curr['target_node_name'].str.replace(
                pattern, '<:>')
            raw_cg_df_next['source_node_name_nosrcref'] = raw_cg_df_next['source_node_name'].str.replace(
                pattern, '<:>')
            raw_cg_df_next['target_node_name_nosrcref'] = raw_cg_df_next['target_node_name'].str.replace(
                pattern, '<:>')
            # remove the begin_line:begin_column from the node serialized name
            t_curr = tuple(zip(raw_cg_df_curr['source_node_name_nosrcref'], raw_cg_df_curr['target_node_name_nosrcref'],
                           raw_cg_df_curr['s_file_path'], raw_cg_df_curr['t_file_path']))
            s_curr = set(t_curr)
            logging.debug("""len t_curr {0}, len s_curr {1} """.format(
                len(t_curr), len(s_curr)))
            t_next = tuple(zip(raw_cg_df_next['source_node_name_nosrcref'], raw_cg_df_next['target_node_name_nosrcref'],
                           raw_cg_df_next['s_file_path'], raw_cg_df_next['t_file_path']))
            s_next = set(t_next)
            logging.debug("""len t_next {0}, len s_next {1} """.format(
                len(t_curr), len(s_curr)))

            # get added calls on next (existing in next but not curr)
            added_calls = list(s_next - s_curr)
            # get deleted calls on next (existing in curr but not in next)
            deleted_calls = list(s_curr - s_next)
            # get unchanged calls
            unchanged_calls = list(s_curr.intersection(s_next))

            logging.debug("len added_calls {0}".format(len(added_calls)))
            logging.debug("len deleted_calls {0}".format(len(deleted_calls)))
            logging.debug("len unchanged_calls {0}".format(
                len(unchanged_calls)))

            curr_node_name_nosrcref_dupplicates = get_node_name_nosrcref_dupplicates(
                s_curr)
            next_node_name_nosrcref_dupplicates = get_node_name_nosrcref_dupplicates(
                s_next)

            has_unique_node_name_nosrcref = False
            # Case 1: added/deleted call has unique node_name_nosrcref
            if len(curr_node_name_nosrcref_dupplicates) + len(next_node_name_nosrcref_dupplicates) == 0:
                has_unique_node_name_nosrcref = True

            if has_unique_node_name_nosrcref:
                for a in added_calls:
                    df_next_row = raw_cg_df_next.loc[(raw_cg_df_next['s_file_path'] == a[2])
                                                     & (raw_cg_df_next['t_file_path'] == a[3])
                                                     & (raw_cg_df_next['source_node_name_nosrcref'] == a[0])
                                                     & (raw_cg_df_next['target_node_name_nosrcref'] == a[1])]

                    if len(df_next_row) == 1:
                        sql_string = """UPDATE edge_hist SET
                                    commit_hash_start = "{0}", commit_start_datetime="{1}",
                                    commit_hash_oldest="{2}", commit_oldest_datetime="{3}"
                                    WHERE
                                    s_file_path = "{4}"
                                    AND t_file_path = "{5}"
                                    AND source_node_name = "{6}"
                                    AND target_node_name = "{7}"
                                    AND closed = 0;""".format(
                            df_next_row.iloc[0]['commit_hash'], df_next_row.iloc[0]['commit_date'],
                            df_next_row.iloc[0]['commit_hash'], df_next_row.iloc[0]['commit_date'],
                            df_next_row.iloc[0]['s_file_path'], df_next_row.iloc[0]['t_file_path'],
                            df_next_row.iloc[0]['source_node_name'], df_next_row.iloc[0]['target_node_name'])
                        # logging.debug(sql_string)
                        cur.execute(sql_string)

                    else:
                        logging.error(
                            "has_unique_node_name_nosrcref found more than one row in raw_cg_df_next!")

                for d in deleted_calls:
                    df_curr_row = raw_cg_df_curr.loc[(raw_cg_df_curr['s_file_path'] == d[2])
                                                     & (raw_cg_df_curr['t_file_path'] == d[3])
                                                     & (raw_cg_df_curr['source_node_name_nosrcref'] == d[0])
                                                     & (raw_cg_df_curr['target_node_name_nosrcref'] == d[1])]
                    if len(df_curr_row) == 1:
                        sql_string = """INSERT INTO edge_hist
                                    (source_node_id,
                                    source_node_type,
                                    source_node_name,
                                    target_node_id,
                                    target_node_type,
                                    target_node_name,
                                    s_file_path,
                                    t_file_path,
                                    commit_hash_start,
                                    commit_start_datetime,
                                    commit_hash_oldest,
                                    commit_oldest_datetime,
                                    commit_hash_end,
                                    commit_end_datetime,
                                    source_node_name_nosrcref,
                                    target_node_name_nosrcref,
                                    closed)
                                    VALUES
                                    ({0},"{1}","{2}",{3},"{4}","{5}","{6}","{7}","{8}","{9}",
                                    "{10}","{11}","{12}","{13}","{14}","{15}",1);""".format(
                            df_curr_row.iloc[0]['source_node_id'],
                            df_curr_row.iloc[0]['source_node_type'],
                            df_curr_row.iloc[0]['source_node_name'],
                            df_curr_row.iloc[0]['target_node_id'],
                            df_curr_row.iloc[0]['target_node_type'],
                            df_curr_row.iloc[0]['target_node_name'],
                            df_curr_row.iloc[0]['s_file_path'],
                            df_curr_row.iloc[0]['t_file_path'],
                            '',  # start hash
                            '',  # start date
                            df_curr_row.iloc[0]['commit_hash'],  # oldest hash
                            df_curr_row.iloc[0]['commit_date'],  # oldest date
                            df_curr_row.iloc[0]['commit_hash'],  # end hash
                            df_curr_row.iloc[0]['commit_date'],  # end date
                            df_curr_row.iloc[0]['source_node_name_nosrcref'],
                            df_curr_row.iloc[0]['target_node_name_nosrcref'],
                            1)  # we know that this was his last commit
                        # logging.debug(sql_string)
                        cur.execute(sql_string)

                    else:
                        logging.error(
                            "has_unique_node_name_nosrcref found more than one row in raw_cg_df_curr!")

                # TODO deal with re-insertions
                for u in unchanged_calls:
                    df_curr_row = raw_cg_df_curr.loc[(raw_cg_df_curr['s_file_path'] == u[2])
                                                     & (raw_cg_df_curr['t_file_path'] == u[3])
                                                     & (raw_cg_df_curr['source_node_name_nosrcref'] == u[0])
                                                     & (raw_cg_df_curr['target_node_name_nosrcref'] == u[1])]
                    df_next_row = raw_cg_df_next.loc[(raw_cg_df_next['s_file_path'] == u[2])
                                                     & (raw_cg_df_next['t_file_path'] == u[3])
                                                     & (raw_cg_df_next['source_node_name_nosrcref'] == u[0])
                                                     & (raw_cg_df_next['target_node_name_nosrcref'] == u[1])]

                    if len(df_next_row) == 1:
                        sql_string = """UPDATE edge_hist SET
                                    source_node_name = "{0}", target_node_name="{1}",
                                    commit_hash_oldest="{2}", commit_oldest_datetime="{3}"
                                    WHERE
                                    s_file_path = "{4}"
                                    AND t_file_path = "{5}"
                                    AND source_node_name = "{6}"
                                    AND target_node_name = "{7}"
                                    AND closed = 0;""".format(
                            df_curr_row.iloc[0]['source_node_name'], df_curr_row.iloc[0]['target_node_name'],
                            commit_hash, commit_date,
                            df_next_row.iloc[0]['s_file_path'], df_next_row.iloc[0]['t_file_path'],
                            df_next_row.iloc[0]['source_node_name'], df_next_row.iloc[0]['target_node_name'])
                        logging.debug(sql_string)
                        cur.execute(sql_string)

                    else:
                        logging.error(
                            "has_unique_node_name_nosrcref found more than one row in raw_cg_df_curr!")

                con_raw_cg_db.commit()
                cur.close()

            # Case 2: there are more than one node_name_nosrcref similar edges
            else:
                logging.debug(
                    "There are more than one node_name_nosrcref similar edges. curr {0}, next {1}".format(len(curr_node_name_nosrcref_dupplicates), len(next_node_name_nosrcref_dupplicates)))

        else:
            save_start_commit_in_edge_hist(
                path_to_edge_hist_db, raw_cg_db_path, commit_hash, commit_date)

            #logging.info("First commit in the database.")
            # sql_string = """select *,
            #    "" as commit_hash_start,
            #    "" as commit_start_datetime,
            #    "{0}" as commit_hash_oldest,
            #    "{1}" as commit_oldest_datetime,
            #    "" as commit_hash_end,
            #    "" as commit_end_datetime,
            #    0 as closed
            #    from "{0}";""".format(commit_hash, commit_date)
            #df = pandas.read_sql_query(sql_string, con_raw_cg_db)
            # df['source_node_name_nosrcref'] = df['source_node_name'].str.replace(
            #    pattern, '<:>')
            # df['target_node_name_nosrcref'] = df['target_node_name'].str.replace(
            #    pattern, '<:>')
            # df.to_sql(
            #    "edge_hist", con_raw_cg_db, if_exists='replace', index=False)
            # con_raw_cg_db.commit()
            # cur.close()

    except Exception as err:
        con_raw_cg_db.rollback()
        con_edge_hist_db.rollback()
        # cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
        return None


def save_start_commit_in_edge_hist(path_to_edge_hist_db, raw_cg_db_path, commit_hash, commit_date):
    logging.debug(
        "------- save_start_commit_in_edge_hist: {0}, {1}".format(commit_hash, commit_date))
    try:
        eh_target_db_path = path_to_edge_hist_db if path_to_edge_hist_db is not None else raw_cg_db_path
        con_raw_cg_db = sqlite3.connect(raw_cg_db_path)
        con_edge_hist_db = sqlite3.connect(eh_target_db_path)
        cur_edge_hist_db = con_edge_hist_db.cursor()
        pattern = re.compile(r"\<\d+\:\d+\>")

        logging.info("First commit in the database.")
        sql_string = """select *,
            "" as commit_hash_start,
            "" as commit_start_datetime,
            "{0}" as commit_hash_oldest,
            "{1}" as commit_oldest_datetime,
            "" as commit_hash_end,
            "" as commit_end_datetime,
            0 as closed
            from "{0}";""".format(commit_hash, commit_date)
        df = pandas.read_sql_query(sql_string, con_raw_cg_db)
        df['source_node_name_nosrcref'] = df['source_node_name'].str.replace(
            pattern, '<:>')
        df['target_node_name_nosrcref'] = df['target_node_name'].str.replace(
            pattern, '<:>')
        df.to_sql(
            "edge_hist", con_edge_hist_db, if_exists='replace', index=False)
        con_edge_hist_db.commit()
        cur_edge_hist_db.close()

    except Exception as err:
        con_raw_cg_db.rollback()
        # cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
        return None


def calculate_cg_diffs(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    """We care about absolute calls between functions. if the same function B is called twice in function A, and in the next commit
    one of the calls is dropped, the call graph remains the same because function A is still calling function B.
    Because all relevant cg data is already fetched we work from older to newer date/commit"""
    logging.debug("Start calculate_cg_diffs")

    # if (proj_config.get_start_repo_date() is not None and proj_config.get_end_repo_date()):
    #    git_traverse_between_dates(proj_config, proj_paths)

    # TODO check that start date is not None
    start_date = proj_config.get_start_repo_date()
    end_date = proj_config.get_end_repo_date()

    proj_name = proj_config.get_proj_name()
    path_to_cache_cg_dbs_dir = proj_paths.get_path_to_cache_cg_dbs_dir()
    path_to_project_db = proj_paths.get_path_to_project_db()
    path_to_edge_hist_db = proj_paths.get_path_to_edge_hist_db()

    raw_cg_db_path = os.path.join(path_to_cache_cg_dbs_dir,
                                  (proj_name + '_raw_cg.db'))
    if not os.path.exists(str(raw_cg_db_path)):
        logging.ERROR(
            "raw_cg_db_path does not exist! {0}".format(raw_cg_db_path))
    eh_target_db_path = path_to_edge_hist_db if path_to_edge_hist_db is not None else raw_cg_db_path

    con_analytics_db = sqlite3.connect(path_to_project_db)
    con_raw_cg_db = sqlite3.connect(raw_cg_db_path)
    con_edge_hist_db = sqlite3.connect(eh_target_db_path)

    # get first hash to process
    r = get_start_hash(con_analytics_db, start_date)
    start_commit_hash = None if r is None else r[0]
    start_commit_date = None if r is None else r[1]
    logging.debug(
        "------- start_commit_hash: {0}, {1}".format(start_commit_hash, start_commit_date))

    # get last hash to process
    r = get_end_hash(con_analytics_db, end_date)
    end_commit_hash = None if r is None else r[0]
    end_commit_date = None if r is None else r[1]
    logging.debug("end_commit_hash: {0}, {1}".format(
        end_commit_hash, end_commit_date))

    # process first hash
    save_start_commit_in_edge_hist(
        path_to_edge_hist_db, raw_cg_db_path, start_commit_hash, start_commit_date)

    curr_commit_hash = start_commit_hash
    curr_commit_date = start_commit_date
    # some function names include the source code row and column
    pattern = re.compile(r"\<\d+\:\d+\>")
    end_hash_reached = False
    while not end_hash_reached:
        logging.debug(
            "------- curr_commit_hash: {0}, {1}".format(curr_commit_hash, curr_commit_date))
        r = get_next_hash(con_analytics_db, curr_commit_date)
        next_commit_hash = None if r is None else r[0]
        next_commit_date = None if r is None else r[1]
        logging.debug("next_commit_hash: {0}, {1}".format(
            next_commit_hash, next_commit_date))

        if next_commit_date >= end_commit_date:
            logging.debug("last commit reached: {0}, {1}".format(
                end_commit_hash, end_commit_date))
            end_hash_reached = True

        # example glucosio-android0ff0d3fae09581ea490794eaa82b4279fabeb7f4.srctrldb
        try:
            cur_raw_cg_db = con_raw_cg_db.cursor()
            cur_edge_hist_db = con_edge_hist_db.cursor()
            # TODO split for testability
            # get nodes only existing in current commit
            sql_string = """SELECT '{0}' as commit_hash,
                '{1}' as commit_date,
                'curr' as commit_type,
                *  
                FROM '{0}' as curr_t
                WHERE NOT EXISTS (
                    SELECT *  
                    FROM  "{2}" as next_t
                    WHERE next_t.s_file_path = curr_t.s_file_path
                    AND next_t.t_file_path = curr_t.t_file_path
                    AND next_t.source_node_name = curr_t.source_node_name
                    AND next_t.target_node_name = curr_t.target_node_name
                );""".format(curr_commit_hash, curr_commit_date, next_commit_hash)

            raw_cg_df_curr = pandas.read_sql_query(
                sql_string, con_raw_cg_db)

            # get nodes only existing in next commit
            sql_string = """SELECT "{0}" as commit_hash,
                '{1}' as commit_date,
                'next' as commit_type,
                *  
                FROM '{0}' as next_t
                WHERE NOT EXISTS (
                    SELECT *  
                    FROM  "{2}" as curr_t
                    WHERE next_t.s_file_path = curr_t.s_file_path
                    AND next_t.t_file_path = curr_t.t_file_path
                    AND next_t.source_node_name = curr_t.source_node_name
                    AND next_t.target_node_name = curr_t.target_node_name
                );""".format(next_commit_hash, next_commit_date, curr_commit_hash)

            raw_cg_df_next = pandas.read_sql_query(
                sql_string, con_raw_cg_db)

            # name of node might include line number in code
            raw_cg_df_curr['source_node_name_nosrcref'] = raw_cg_df_curr['source_node_name'].str.replace(
                pattern, '<:>')
            raw_cg_df_curr['target_node_name_nosrcref'] = raw_cg_df_curr['target_node_name'].str.replace(
                pattern, '<:>')
            raw_cg_df_next['source_node_name_nosrcref'] = raw_cg_df_next['source_node_name'].str.replace(
                pattern, '<:>')
            raw_cg_df_next['target_node_name_nosrcref'] = raw_cg_df_next['target_node_name'].str.replace(
                pattern, '<:>')
            # remove the begin_line:begin_column from the node serialized name
            t_curr = tuple(zip(raw_cg_df_curr['source_node_name_nosrcref'], raw_cg_df_curr['target_node_name_nosrcref'],
                               raw_cg_df_curr['s_file_path'], raw_cg_df_curr['t_file_path']))
            s_curr = set(t_curr)
            logging.debug("""len t_curr {0}, len s_curr {1} """.format(
                len(t_curr), len(s_curr)))
            t_next = tuple(zip(raw_cg_df_next['source_node_name_nosrcref'], raw_cg_df_next['target_node_name_nosrcref'],
                               raw_cg_df_next['s_file_path'], raw_cg_df_next['t_file_path']))
            s_next = set(t_next)
            logging.debug("""len t_next {0}, len s_next {1} """.format(
                len(t_curr), len(s_curr)))

            # get added calls on next (existing in next but not curr)
            added_calls = list(s_next - s_curr)
            # get deleted calls on next (existing in curr but not in next)
            deleted_calls = list(s_curr - s_next)
            # get unchanged calls
            unchanged_calls = list(s_curr.intersection(s_next))

            logging.debug("len added_calls {0}".format(len(added_calls)))
            logging.debug("len deleted_calls {0}".format(len(deleted_calls)))
            logging.debug("len unchanged_calls {0}".format(
                len(unchanged_calls)))

            curr_node_name_nosrcref_dupplicates = get_node_name_nosrcref_dupplicates(
                s_curr)
            next_node_name_nosrcref_dupplicates = get_node_name_nosrcref_dupplicates(
                s_next)

            has_unique_node_name_nosrcref = False
            # Case 1: added/deleted call has unique node_name_nosrcref
            if len(curr_node_name_nosrcref_dupplicates) + len(next_node_name_nosrcref_dupplicates) == 0:
                has_unique_node_name_nosrcref = True

            if has_unique_node_name_nosrcref:
                for a in added_calls:
                    df_next_row = raw_cg_df_next.loc[(raw_cg_df_next['s_file_path'] == a[2])
                                                     & (raw_cg_df_next['t_file_path'] == a[3])
                                                     & (raw_cg_df_next['source_node_name_nosrcref'] == a[0])
                                                     & (raw_cg_df_next['target_node_name_nosrcref'] == a[1])]
                    if len(df_next_row) == 1:
                        sql_string = """INSERT INTO edge_hist
                                    (source_node_id, 
                                    source_node_type, 
                                    source_node_name, 
                                    target_node_id,
                                    target_node_type,
                                    target_node_name,
                                    s_file_path,
                                    t_file_path,
                                    commit_hash_start,
                                    commit_start_datetime,
                                    commit_hash_oldest,
                                    commit_oldest_datetime,
                                    commit_hash_end,
                                    commit_end_datetime,
                                    source_node_name_nosrcref,
                                    target_node_name_nosrcref,
                                    closed)
                                    VALUES
                                    ({0},"{1}","{2}",{3},"{4}","{5}","{6}","{7}","{8}","{9}",
                                    "{10}","{11}","{12}","{13}","{14}","{15}",0);""".format(
                            df_next_row.iloc[0]['source_node_id'],
                            df_next_row.iloc[0]['source_node_type'],
                            df_next_row.iloc[0]['source_node_name'],
                            df_next_row.iloc[0]['target_node_id'],
                            df_next_row.iloc[0]['target_node_type'],
                            df_next_row.iloc[0]['target_node_name'],
                            df_next_row.iloc[0]['s_file_path'],
                            df_next_row.iloc[0]['t_file_path'],
                            df_next_row.iloc[0]['commit_hash'],  # start hash
                            df_next_row.iloc[0]['commit_date'],  # start date
                            df_next_row.iloc[0]['commit_hash'],  # oldest hash
                            df_next_row.iloc[0]['commit_date'],  # oldest date
                            '',  # end hash
                            '',  # end date
                            df_next_row.iloc[0]['source_node_name_nosrcref'],
                            df_next_row.iloc[0]['target_node_name_nosrcref'])
                        #logging.debug(sql_string)
                        cur_edge_hist_db.execute(sql_string)

                    else:
                        logging.error(
                            "has_unique_node_name_nosrcref found more than one row in raw_cg_df_curr!")

                for d in deleted_calls:
                    df_curr_row = raw_cg_df_curr.loc[(raw_cg_df_curr['s_file_path'] == d[2])
                                                     & (raw_cg_df_curr['t_file_path'] == d[3])
                                                     & (raw_cg_df_curr['source_node_name_nosrcref'] == d[0])
                                                     & (raw_cg_df_curr['target_node_name_nosrcref'] == d[1])]

                    if len(df_curr_row) == 1:
                        sql_string = """UPDATE edge_hist SET
                                    commit_hash_end = "{0}", commit_end_datetime="{1}",
                                    closed = 1
                                    WHERE
                                    s_file_path = "{2}"
                                    AND t_file_path = "{3}"
                                    AND source_node_name = "{4}"
                                    AND target_node_name = "{5}" 
                                    AND closed = 0;""".format(
                            df_curr_row.iloc[0]['commit_hash'], df_curr_row.iloc[0]['commit_date'],
                            df_curr_row.iloc[0]['s_file_path'], df_curr_row.iloc[0]['t_file_path'],
                            df_curr_row.iloc[0]['source_node_name'], df_curr_row.iloc[0]['target_node_name'])
                        #logging.debug(sql_string)
                        cur_edge_hist_db.execute(sql_string)

                    else:
                        logging.error(
                            "has_unique_node_name_nosrcref found more than one row in raw_cg_df_next!")

                # TODO deal with re-insertions
                for u in unchanged_calls:
                    df_curr_row = raw_cg_df_curr.loc[(raw_cg_df_curr['s_file_path'] == u[2])
                                                     & (raw_cg_df_curr['t_file_path'] == u[3])
                                                     & (raw_cg_df_curr['source_node_name_nosrcref'] == u[0])
                                                     & (raw_cg_df_curr['target_node_name_nosrcref'] == u[1])]
                    df_next_row = raw_cg_df_next.loc[(raw_cg_df_next['s_file_path'] == u[2])
                                                     & (raw_cg_df_next['t_file_path'] == u[3])
                                                     & (raw_cg_df_next['source_node_name_nosrcref'] == u[0])
                                                     & (raw_cg_df_next['target_node_name_nosrcref'] == u[1])]

                    if len(df_next_row) == 1:
                        sql_string = """UPDATE edge_hist SET
                                    source_node_name = "{0}", target_node_name="{1}"
                                    WHERE
                                    s_file_path = "{2}"
                                    AND t_file_path = "{3}"
                                    AND source_node_name = "{4}"
                                    AND target_node_name = "{5}" 
                                    AND closed = 0;""".format(
                            df_next_row.iloc[0]['source_node_name'], df_next_row.iloc[0]['target_node_name'],
                            df_curr_row.iloc[0]['s_file_path'], df_curr_row.iloc[0]['t_file_path'],
                            df_curr_row.iloc[0]['source_node_name'], df_curr_row.iloc[0]['target_node_name'])
                        #logging.debug(sql_string)
                        cur_edge_hist_db.execute(sql_string)

                    else:
                        logging.error(
                            "has_unique_node_name_nosrcref found more than one row in raw_cg_df_curr!")

                con_raw_cg_db.commit()
                cur_raw_cg_db.close()

                con_edge_hist_db.commit()
                cur_edge_hist_db.close()

            # Case 2: there are more than one node_name_nosrcref similar edges
            else:
                logging.debug(
                    "There are more than one node_name_nosrcref similar edges. curr {0}, next {1}".format(len(curr_node_name_nosrcref_dupplicates), len(next_node_name_nosrcref_dupplicates)))

            curr_commit_hash = next_commit_hash
            curr_commit_date = next_commit_date

        except Exception as err:
            con_raw_cg_db.rollback()
            # cur.close()
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            err_message = template.format(type(err).__name__, err.args)
            logging.error(err_message)
            return None

    logging.debug("end_hash_reached {0}".format(end_hash_reached))
    logging.debug("End calculate_cg_diffs")


# in theory the git_repository_mining_util.git_traverse_on_X() could keep the commit previously processed (next in commit date),
# but better go to the db in case of interruptions
# and because the start of the current execution does not mean that there will not be
# saved commits on the db and call graph databases
# move to sql util


def get_start_hash(con_analytics_db, commit_date: datetime) -> str:
    try:
        cur = con_analytics_db.cursor()

        if commit_date is None:
            sql_string = """select commit_hash, commit_commiter_datetime
                from git_commit
                order by commit_commiter_datetime
                limit 1"""
        else:
            sql_string = """select commit_hash, commit_commiter_datetime
                from git_commit
                where commit_commiter_datetime >= '{0}'
                order by commit_commiter_datetime
                limit 1""".format(commit_date)

        cur.execute(sql_string)
        result = cur.fetchone()
        print("result", result)
        logging.debug(result)

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


def get_next_hash(con_analytics_db, commit_date: datetime) -> str:
    try:
        cur = con_analytics_db.cursor()

        sql_string = """select commit_hash, commit_commiter_datetime
            from git_commit
            where commit_commiter_datetime > '{0}'
            order by commit_commiter_datetime
            limit 1""".format(commit_date)

        cur.execute(sql_string)
        result = cur.fetchone()
        print("result", result)
        logging.debug(result)

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


def get_end_hash(con_analytics_db, commit_date: datetime) -> str:
    try:
        cur = con_analytics_db.cursor()

        if commit_date is None:
            sql_string = """select commit_hash, commit_commiter_datetime
                from git_commit
                order by commit_commiter_datetime desc
                limit 1"""
        else:
            sql_string = """select commit_hash, commit_commiter_datetime
                from git_commit
                where commit_commiter_datetime >= '{0}'
                order by commit_commiter_datetime
                limit 1""".format(commit_date)

        cur.execute(sql_string)
        result = cur.fetchone()
        print("result", result)
        logging.debug(result)

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


def make_config_file_copy(orig_file_dir, orig_file_name, target_file_dir, target_file_name):
    source_file_path = os.path.join(orig_file_dir, orig_file_name)
    # print(source_file_path)
    # print(os.path.exists(source_file_path))
    target_file_path = os.path.join(target_file_dir, target_file_name)
    shutil_copy(source_file_path, target_file_path)
    # print(target_file_path)
    # print(os.path.exists(target_file_path))
