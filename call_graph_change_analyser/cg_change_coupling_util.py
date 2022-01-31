import pandas as pd
import sqlite3
import os
import networkx as nx
import itertools
import logging

from models import ProjectConfig, ProjectPaths, StatisticNames, StatisticParams1, StatisticParams2



def save_cg_change_coupling(proj_config: ProjectConfig, proj_paths: ProjectPaths):
    logging.debug("Start save_cg_change_coupling")
    path_to_cache_cg_dbs_dir = proj_paths.get_path_to_cache_cg_dbs_dir()
    raw_cg_db_path = os.path.join(path_to_cache_cg_dbs_dir,
                                  (proj_config.get_proj_name() + '_raw_cg.db'))
    path_to_project_db = proj_paths.get_path_to_project_db()
    path_to_src_files_raw_cg = proj_paths.get_str_path_to_src_files()
    logging.debug(path_to_src_files_raw_cg)
    # 'C:/Users/lopm/Documents/gitprojects/call_graph_change_analyser/project_results/glucosio-android/.cache/git/'
    # 'C:/Users/lopm/Documents/gitprojects/call_graph_change_analyser/project_results/glucosio-android/.cache/git/'

    con_analytics_db = sqlite3.connect(path_to_project_db)
    con_raw_cg_db = sqlite3.connect(raw_cg_db_path)

    sql_statement = """select * from git_commit;"""
    git_commit_df = pd.read_sql_query(sql_statement, con_analytics_db)
    logging.debug("Nr of commits: {0}".format(len(git_commit_df)))

    list_stat = []

    for g_idx, g in git_commit_df.iterrows():
        logging.debug("commit_hash: {0}".format(g['commit_hash']))

        sql_statement = """select * from '{0}';""".format(g['commit_hash'])
        hash_raw_cg_df = pd.read_sql_query(sql_statement, con_raw_cg_db)

        # first degree coupling
        df_s_and_t = hash_raw_cg_df[(hash_raw_cg_df['s_node_change'] == 1) & (hash_raw_cg_df['t_node_change'] == 1)]
        deg1_coupling_nr_edges = len(df_s_and_t)
        set_s_and_t_nodes_changed = set(df_s_and_t['source_node_id']).union(set(df_s_and_t['target_node_id']))
        deg1_coupling_nr_nodes = len(set_s_and_t_nodes_changed)
        list_stat.append([StatisticNames.cg_f_changes.name, g['commit_hash'], StatisticParams1.degree_distance.name, 1,  StatisticParams2.nr_edges.name, deg1_coupling_nr_edges])
        list_stat.append([StatisticNames.cg_f_changes.name, g['commit_hash'], StatisticParams1.degree_distance.name, 1,  StatisticParams2.nr_nodes.name, deg1_coupling_nr_nodes])

        # nth degree coupling
        df_s = hash_raw_cg_df[(hash_raw_cg_df['s_node_change'] == 1) & (hash_raw_cg_df['t_node_change'] == 0)]
        df_t = hash_raw_cg_df[(hash_raw_cg_df['s_node_change'] == 0) & (hash_raw_cg_df['t_node_change'] == 1)]
        G=nx.from_pandas_edgelist(hash_raw_cg_df, 'source_node_id', 'target_node_id', create_using=nx.DiGraph())
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
                print(p_l)
                set_nodes_changed_in_cg.add(pair_s_n[0])
                set_nodes_changed_in_cg.add(pair_s_n[1])
                i += 1
                print(nx.shortest_path(G, pair_s_n[0],pair_s_n[1]))
                cg_path_length[p_l]=cg_path_length.get(p_l,0)+1
            except nx.NetworkXNoPath as noPathErr:
                # do nothing
                pass

        #print("Nr pair permutations: ",len(list_pairs_s_nodes))
        logging.debug("Nr linked nodes: {0}".format(i))
        for k,v in cg_path_length.items():
                list_stat.append([StatisticNames.cg_f_changes.name, g['commit_hash'], StatisticParams1.degree_distance.name, k,  StatisticParams2.nr_edges.name, v])

        #print("Nr linked nodes with paths", len(set_nodes_changed_in_cg))
        #print(set_nodes_changed_in_cg)
        
    df_stats = pd.DataFrame(list_stat, columns =['stat_name', 'commit_hash', 'param1', 'param1_value', 'param2', 'param2_value', 'value'])
    df_stats.to_sql(StatisticNames.cg_f_changes.name, con_analytics_db, if_exists='replace', index=False)
