import sqlite3
import logging
import pandas as pd
import os
import platform

from models import ProjectConfig, ProjectPaths


def update_commit_changes_to_cg_nodes(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    try:
        logging.debug("Start update_commit_changes_to_cg_nodes")
        print("update_commit_changes_to_cg_nodes")
        path_to_cache_cg_dbs_dir = proj_paths.get_path_to_cache_cg_dbs_dir()
        raw_cg_db_path = os.path.join(path_to_cache_cg_dbs_dir,
                                      (proj_config.get_proj_name() + '_raw_cg.db'))
        path_to_project_db = proj_paths.get_path_to_project_db()
        path_to_src_files_raw_cg = proj_paths.get_str_path_to_src_files()
        logging.debug(path_to_src_files_raw_cg)

        con_analytics_db = sqlite3.connect(path_to_project_db)
        con_raw_cg_db = sqlite3.connect(raw_cg_db_path)

        sql_statement = """select * from git_commit;"""
        git_commit_df = pd.read_sql_query(sql_statement, con_analytics_db)
        logging.debug("Nr of commits: {0}".format(len(git_commit_df)))

        sql_statement = """select * from function_commit;"""
        function_commit_df = pd.read_sql_query(sql_statement, con_analytics_db)
        logging.debug("Nr of function commits: {0}".format(
            len(function_commit_df)))

        # add columns to intresect to the cg nodes
        function_commit_df['s_file_path'] = function_commit_df['file_path']
        function_commit_df['t_file_path'] = function_commit_df['file_path']

        skip_commit = False
        for g_idx, g in git_commit_df.iterrows():
            logging.debug("commit_hash: {0}".format(g['commit_hash']))

            try:
                sql_statement = """select * from '{0}';""".format(
                    g['commit_hash'])
                hash_raw_cg_df = pd.read_sql_query(
                    sql_statement, con_raw_cg_db)
            except Exception as raw_err:
                skip_commit = True
                con_raw_cg_db.rollback()
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                err_message = template.format(
                    type(raw_err).__name__, raw_err.args)
                logging.info(err_message)

            if not skip_commit:
                # add transformed file path
                hash_raw_cg_df['s_file_path_original'] = hash_raw_cg_df['s_file_path']
                hash_raw_cg_df['t_file_path_original'] = hash_raw_cg_df['t_file_path']
                # print(hash_raw_cg_df[0:1]['s_file_path_original'][0])
                # print(hash_raw_cg_df[0:1].s_file_path[0])

                hash_raw_cg_df['s_file_path'] = hash_raw_cg_df['s_file_path'].str.replace(
                    path_to_src_files_raw_cg, '')
                hash_raw_cg_df['t_file_path'] = hash_raw_cg_df['t_file_path'].str.replace(
                    path_to_src_files_raw_cg, '')
                # print(hash_raw_cg_df[0:1].s_file_path[0])

                # replace window direcotry slash in cg df
                if platform.system() == 'Windows':
                    hash_raw_cg_df['s_file_path'] = hash_raw_cg_df['s_file_path'].str.replace(
                        "/", "\\")
                    hash_raw_cg_df['t_file_path'] = hash_raw_cg_df['t_file_path'].str.replace(
                        "/", "\\")
                    # print(hash_raw_cg_df[0:1].s_file_path[0])

                fc_for_hash = function_commit_df[(
                    function_commit_df['commit_hash'] == g['commit_hash'])]
                # print(fc_for_hash[0:1].s_file_path[0])

                intersection_s_file_path = pd.merge(
                    hash_raw_cg_df, fc_for_hash, how='inner', on=['s_file_path'])
                logging.debug("Len intersection_s_file_path: {0}".format(
                    len(intersection_s_file_path)))

                intersection_t_file_path = pd.merge(
                    hash_raw_cg_df, fc_for_hash, how='inner', on=['t_file_path'])
                logging.debug("Len intersection_t_file_path: {0}".format(
                    len(intersection_t_file_path)))

                str_update = ""
                j = 0
                k = 0
                set_s_nodes = set([])
                set_t_nodes = set([])

                cur = con_raw_cg_db.cursor()
                for s_e_idx, s_edge_row in intersection_s_file_path.iterrows():
                    if s_edge_row['function_unqualified_name'] in s_edge_row['source_node_name']:
                        j += 1
                        set_s_nodes.add(
                            (s_edge_row['s_file_path_original'], s_edge_row['source_node_name']))

                for s in set_s_nodes:
                    str_update = """update '{0}' set s_node_change = 1 where s_file_path = '{1}' and source_node_name = '{2}';""".format(
                        g['commit_hash'], s[0], s[1])
                    cur.execute(str_update)
                    if(cur.rowcount <= 0):
                        logging.warn("Rowcount {0}".format(cur.rowcount))
                        logging.debug(str_update)

                for t_e_idx, t_edge_row in intersection_t_file_path.iterrows():
                    if t_edge_row['function_unqualified_name'] in t_edge_row['target_node_name']:
                        k += 1
                        set_t_nodes.add(
                            (t_edge_row['t_file_path_original'], t_edge_row['target_node_name']))

                for t in set_t_nodes:
                    str_update = """update '{0}' set t_node_change = 1 where t_file_path = '{1}' and target_node_name = '{2}';""".format(
                        g['commit_hash'], t[0], t[1])
                    cur.execute(str_update)
                    if(cur.rowcount <= 0):
                        logging.warn("Rowcount {0}".format(cur.rowcount))
                        logging.debug(str_update)

                logging.debug("s nodes changed: {0} ".format(j))
                logging.debug("t nodes changed: {0} ".format(k))
                logging.debug("updates s nodes: {0} ".format(len(set_s_nodes)))
                logging.debug("updates t nodes: {0} ".format(len(set_t_nodes)))

                con_raw_cg_db.commit()
                cur.close()
    except Exception as err:
        con_raw_cg_db.rollback()
        cur.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)

    logging.debug("End update_commit_changes_to_cg_nodes")
