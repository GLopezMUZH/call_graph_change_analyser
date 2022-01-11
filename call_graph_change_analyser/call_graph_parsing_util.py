# %%
import subprocess
from subprocess import *
from git import Repo
import os
from shutil import copy as shutil_copy
import sqlite3
import pandas
import logging

import time
from stopwatch import Stopwatch, profile
from datetime import datetime


def sctWrapper(cgdbpath, *args):
    #print("Exists dir: ", os.path.exists(cgdbpath))
    file_path = os.path.join(cgdbpath, args[len(args)-1])
    #print("File path: ", file_path)
    #print("Exists file: ", args[len(args)-1], os.path.exists(file_path))

    process = Popen(['sourcetrail', 'index']+list(args),
                    stdout=PIPE, stderr=PIPE, cwd=cgdbpath, shell=True)
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
    return ret


def parse_source_for_call_graph(proj_name: str, path_to_cache_cg_dbs: str, commit_hash: str, srctrl_db_name: str) -> None:
    proj_srctrl_config_file_name = proj_name + \
        '.srctrlprj'  # original file was copied to this path
    proj_commit_srctrl_config_file_name = proj_name + commit_hash + '.srctrlprj'

    # if configuration file for parsing the call graph does not exist, create
    if not os.path.exists(os.path.join(path_to_cache_cg_dbs, proj_commit_srctrl_config_file_name)):
        make_config_file_copy(orig_file_dir=path_to_cache_cg_dbs, orig_file_name=proj_srctrl_config_file_name,
                              target_file_dir=path_to_cache_cg_dbs, target_file_name=proj_commit_srctrl_config_file_name)
    else:
        logging.info("Commit srctrl prj config file already exists.")

    # if srctrl database does not exist, create
    if not os.path.exists(os.path.join(path_to_cache_cg_dbs, srctrl_db_name)):
        # creates srctrl db for the commit
        curr_src_args = [proj_commit_srctrl_config_file_name]
        result = sctWrapper(path_to_cache_cg_dbs, *curr_src_args)
    else:
        logging.info("Commit srctrl database already exists.")


def save_cg_data(proj_name: str, path_to_cache_cg_dbs: str, commit_hash: str, delete_cg_src_db: bool):
    cg_commit_db_path = os.path.join(path_to_cache_cg_dbs,
                                     (proj_name + commit_hash + '_raw_cg.db'))
    srctrl_db_name = proj_name + commit_hash + '.srctrldb'
    path_to_srctrl_db = os.path.join(path_to_cache_cg_dbs,
                                     srctrl_db_name)

    if not os.path.exists(cg_commit_db_path):
        parse_source_for_call_graph(proj_name, path_to_cache_cg_dbs,
                                    commit_hash, srctrl_db_name)

        save_curr_cg_from_source_parcing(path_to_srctrl_db, cg_commit_db_path)
    else:
        logging.info("Commit raw callgraph database already exists.")

    if delete_cg_src_db:
        if os.path.isfile(path_to_srctrl_db):
            os.remove(path_to_srctrl_db)
        else:  # Show an error ##
            logging.debug(
                "Error: {0} file not found".format(path_to_srctrl_db))


def save_curr_cg_from_source_parcing(path_to_srctrl_db: str, cg_commit_db_path: str):
    try:
        con_srctrl_db = sqlite3.connect(path_to_srctrl_db)
        #cur = con_analytics_db.cursor()

        sql_string = """select
            --edge.type as edge_type, --NULL as edge_start_datetime, NULL as edge_end_datetime,
            s_node.id as source_node_id, s_node.type as source_node_type, s_node.serialized_name as source_node_name,
            t_node.id as target_node_id, t_node.type as target_node_type, t_node.serialized_name as target_node_name,
            s_file.path as s_file_path,
            t_file.path as t_file_path
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

        df = pandas.read_sql_query(sql_string, con_srctrl_db)
        con_srctrl_db.commit()
        con_srctrl_db.close()

        # save to commit call graph db
        con_commit_cg_db = sqlite3.connect(cg_commit_db_path)
        df.to_sql(
            'raw_calls', con_commit_cg_db, if_exists='replace', index=False)
        con_commit_cg_db.commit()
        con_commit_cg_db.close()

    except Exception as err:
        # TODO handle db connection errors
        # con_analytics_db.rollback()
        # cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)
        return None


def save_cg_diffs(proj_name: str, path_to_cache_cg_dbs: str, commit_hash: str, commit_date: datetime, path_to_project_db: str):
    prev_commit_hash = get_previous_hash(path_to_project_db, commit_date)
    # example glucosio-android0ff0d3fae09581ea490794eaa82b4279fabeb7f4.srctrldb
    if prev_commit_hash is not None:
        prev_commit_cg_db_name = proj_name + prev_commit_hash + '_raw_cg.db'
        prev_commit_cg_db_path = os.path.join(
            path_to_cache_cg_dbs, prev_commit_cg_db_name)
        if os.path.exists(prev_commit_cg_db_path):
            print("TODO")

        curr_commit_cg_db_name = proj_name + commit_hash + '_raw_cg.db'
        curr_commit_cg_db_path = os.path.join(
            path_to_cache_cg_dbs, curr_commit_cg_db_name)
        if os.path.exists(curr_commit_cg_db_path):
            print("TODO")
        # print(source_file_path)
        # print(os.path.exists(source_file_path))
    else:
        logging.info("First commit in the database")

# in theory the git_repository_mining_util.git_traverse_on_X() could keep the previous commit, but better go to the db in case of interruptions
# and because the start of the current execution does not mean that there will not be saved commits on the db and call graph databases
# move to sql util


def get_previous_hash(path_to_project_db: str, commit_date: datetime) -> str:
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = """select commit_hash
            from git_commit
            where commit_commiter_datetime < '{0}'
            order by commit_commiter_datetime desc
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
