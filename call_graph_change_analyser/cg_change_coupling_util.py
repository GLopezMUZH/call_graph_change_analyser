import pandas as pd
import sqlite3
import os
import networkx as nx
import itertools
import logging

from models import ProjectConfig, ProjectPaths, StatisticNames, StatisticParams1, StatisticParams2



def save_cg_change_coupling(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    try:
        logging.debug("Start save_cg_change_coupling")
        print("save_cg_change_coupling")
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

        list_stat = []

        nr_skip_commits = 0
        nr_processed_commits = 0
        for g_idx, g in git_commit_df.iterrows():
            skip_commit = False
            
            try:
                sql_statement = """select * from '{0}';""".format(g['commit_hash'])
                hash_raw_cg_df = pd.read_sql_query(sql_statement, con_raw_cg_db)
            except Exception as raw_err:
                #logging.debug("commit_hash: {0} {1}".format(g['commit_hash'], g['commit_commiter_datetime']))
                skip_commit = True
                nr_skip_commits += 1
                con_raw_cg_db.rollback()
                template = "skip_commit An exception of type {0} occurred. Arguments:\n{1!r}"
                err_message = template.format(
                    type(raw_err).__name__, raw_err.args)
                logging.info(err_message)

            if not skip_commit:
                logging.debug("commit_hash: {0} {1}".format(g['commit_hash'], g['commit_commiter_datetime']))
                nr_processed_commits += 1
                # first degree coupling
                df_s_and_t = hash_raw_cg_df[(hash_raw_cg_df['s_node_change'] == 1) & (hash_raw_cg_df['t_node_change'] == 1)]
                deg1_coupling_nr_edges = len(df_s_and_t)
                set_s_and_t_nodes_changed = set(df_s_and_t['source_node_id']).union(set(df_s_and_t['target_node_id']))
                deg1_coupling_nr_nodes = len(set_s_and_t_nodes_changed)
                list_stat.append([StatisticNames.cg_f_changes.name, g['commit_hash'], g['commit_commiter_datetime'], StatisticParams1.degree_distance.name, 1,  StatisticParams2.nr_edges.name, deg1_coupling_nr_edges])
                list_stat.append([StatisticNames.cg_f_changes.name, g['commit_hash'], g['commit_commiter_datetime'], StatisticParams1.degree_distance.name, 1,  StatisticParams2.nr_nodes.name, deg1_coupling_nr_nodes])
                #logging.debug("Param2 {0}, v {1}".format(StatisticParams2.nr_edges.name, deg1_coupling_nr_edges))
                #logging.debug("Param2 {0}, v {1}".format(StatisticParams2.nr_nodes.name, deg1_coupling_nr_nodes))
                
                # nth degree coupling
                df_s = hash_raw_cg_df[(hash_raw_cg_df['s_node_change'] == 1) & (hash_raw_cg_df['t_node_change'] == 0)]
                df_t = hash_raw_cg_df[(hash_raw_cg_df['s_node_change'] == 0) & (hash_raw_cg_df['t_node_change'] == 1)]
                G=nx.from_pandas_edgelist(hash_raw_cg_df, 'source_node_id', 'target_node_id', create_using=nx.DiGraph())

                # statistics on the graph
                list_stat.append([StatisticNames.cg_stats.name, g['commit_hash'], g['commit_commiter_datetime'], StatisticParams1.cg_n_nodes.name, G.number_of_nodes(), '', ''])
                list_stat.append([StatisticNames.cg_stats.name, g['commit_hash'], g['commit_commiter_datetime'], StatisticParams1.cg_n_edges.name, G.number_of_edges(), '', ''])

                set_nodes_changed = set(df_s['source_node_id']).union(set(df_t['target_node_id']))
                # we do all the permutations because is a directed graph
                pair_permutations = itertools.permutations(set_nodes_changed, 2)
                list_pairs_s_nodes = list(pair_permutations)
                cg_path_length = {}
                set_nodes_changed_in_cg = set()

                i = 0
                for pair_s_n in list_pairs_s_nodes:
                #print(pair_s_n)
                    try:
                        p_l = nx.shortest_path_length(G,pair_s_n[0],pair_s_n[1])
                        set_nodes_changed_in_cg.add(pair_s_n[0])
                        set_nodes_changed_in_cg.add(pair_s_n[1])
                        i += 1
                        sp = nx.shortest_path(G, pair_s_n[0],pair_s_n[1])
                        set_nodes_changed_in_cg.update(sp)
                        cg_path_length[p_l]=cg_path_length.get(p_l,0)+1
                    except nx.NetworkXNoPath as noPathErr:
                        # do nothing
                        pass

                #print("Nr pair permutations: ",len(list_pairs_s_nodes))
                #logging.debug("Nr linked nodes: {0}".format(i))
                for k,v in cg_path_length.items():
                        if k == 1:
                            continue
                        #logging.debug("dd: {0}, nnodes: {1}".format(k,v))
                        list_stat.append([StatisticNames.cg_f_changes.name, g['commit_hash'], g['commit_commiter_datetime'], StatisticParams1.degree_distance.name, k,  StatisticParams2.nr_edges.name, v])

                logging.debug("Nr linked nodes within paths {0}".format(len(set_nodes_changed_in_cg)))
                #logging.debug(set_nodes_changed_in_cg)
            
                # update cg table
                cur_raw_cg_db = con_raw_cg_db.cursor()
                for n in set_nodes_changed_in_cg:
                    sql_statement = """update '{0}' set cg_change=1 where source_node_id = {1} or target_node_id = {1};""".format(g['commit_hash'], n)
                    cur_raw_cg_db.execute(sql_statement)
                con_raw_cg_db.commit()
                cur_raw_cg_db.close()

        # update general statistics, replace because we append per commit itteration 
        df_stats = pd.DataFrame(list_stat, columns =['stat_name', 'commit_hash', 'commit_commiter_datetime', 'param1', 'param1_value', 'param2', 'param2_value'])
        df_stats.to_sql('cg_statistics', con_analytics_db, if_exists='replace', index=False)

    except Exception as err:
        con_analytics_db.rollback()
        con_raw_cg_db.rollback()
        cur_raw_cg_db.close()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        err_message = template.format(type(err).__name__, err.args)
        logging.error(err_message)

    logging.debug("End update_commit_changes_to_cg_nodes. nr_skip_commits {0}, nr_processed_commits {1}".format(nr_skip_commits, nr_processed_commits))
