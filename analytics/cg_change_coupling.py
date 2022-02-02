import pandas as pd
import matplotlib.pyplot as plt


def display_cg_coupling_on_commit(con_analytics_db, display_total_edges=False):
    sql_statement = """select * from git_commit order by commit_commiter_datetime;"""
    git_commit_df = pd.read_sql_query(sql_statement, con_analytics_db)

    sql_statement = """select * from cg_statistics;"""
    cg_statistics_df = pd.read_sql_query(sql_statement, con_analytics_db)

    labels = []
    labels_commit_hash = []
    l_edges = []
    l_dd1 = []
    l_dd2 = []
    l_dd3 = []
    l_dd4 = []
    l_dd5 = []
    l_dd6 = []
    l_dd7plus = []

    print("Number of commits: {0}".format(len(git_commit_df)))

    i = 0

    for g_idx, g in git_commit_df.iterrows():
        n1 = 0
        n2 = 0
        n3 = 0
        n4 = 0
        n5 = 0
        n6 = 0
        n7plus = 0

        row_edges = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (
            cg_statistics_df['param1'] == 'cg_n_edges')].reset_index(drop=True)

        row_dd1 = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] == 1) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)
        row_dd2 = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] == 2) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)
        row_dd3 = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] == 3) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)
        row_dd4 = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] == 4) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)
        row_dd5 = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] == 5) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)
        row_dd6 = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] == 6) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)
        row_dd7plus = cg_statistics_df[(cg_statistics_df['commit_hash'] == g['commit_hash']) & (cg_statistics_df['param1'] == 'degree_distance') & (
            cg_statistics_df['param1_value'] >= 7) & (cg_statistics_df['param2'] == 'nr_edges')].reset_index(drop=True)

        if len(row_dd1) > 0:
            n1 = int(row_dd1[0:1]['param2_value'][0])

        if len(row_dd2) > 0:
            n2 = int(row_dd2[0:1]['param2_value'][0])

        if len(row_dd3) > 0:
            n3 = int(row_dd3[0:1]['param2_value'][0])

        if len(row_dd4) > 0:
            n4 = int(row_dd4[0:1]['param2_value'][0])

        if len(row_dd5) > 0:
            n5 = int(row_dd5[0:1]['param2_value'][0])

        if len(row_dd6) > 0:
            n6 = int(row_dd6[0:1]['param2_value'][0])

        if len(row_dd7plus) > 0:
            n7plus = int(row_dd7plus[0:1]['param2_value'][0])

        if (n1+n2+n3+n4+n5+n6+n7plus > 0) & len(row_edges) > 0:
            i += 1
            labels.append(i)
            labels_commit_hash.append(g['commit_hash'])
            l_edges.append(int(row_edges[0:1]['param1_value'][0]))
            l_dd1.append(n1)
            l_dd2.append(n2)
            l_dd3.append(n3)
            l_dd4.append(n4)
            l_dd5.append(n5)
            l_dd6.append(n6)
            l_dd7plus.append(n7plus)

    plot_cg_coupling(labels, l_dd1, l_dd2, l_dd3, l_dd4, l_dd5,
                     l_dd6, l_dd7plus, l_edges, display_total_edges)


def display_cg_coupling_on_week(con_analytics_db):
    sql_statement = """select count(*) from git_commit;"""
    cur = con_analytics_db.cursor()
    cur.execute(sql_statement)
    r = cur.fetchone()
    print("Number of commits: {0}".format(r[0]))

    sql_statement = """select
        strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
        (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1 as iso_week,
        param1_value,
        sum(param2_value) as edges_in_week
        from cg_statistics
        where param1 = 'degree_distance'
        --and param1_value = 1
        group by 
        strftime('%Y', date(commit_commiter_datetime)),
        (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1,
        param1_value;"""
    cg_edges_week_df = pd.read_sql_query(sql_statement, con_analytics_db)
    cg_edges_week_df['yr_wk'] = cg_edges_week_df.apply(
        lambda row: ''.join([str(row.iso_yr), '-', str(row.iso_week)]), axis=1)

    labels = []
    l_dd1 = []
    l_dd2 = []
    l_dd3 = []
    l_dd4 = []
    l_dd5 = []
    l_dd6 = []
    l_dd7plus = []

    i = 0
    for g_idx, g in cg_edges_week_df.iterrows():
        n1 = 0
        n2 = 0
        n3 = 0
        n4 = 0
        n5 = 0
        n6 = 0
        n7plus = 0

        row_dd1 = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] == 1)].reset_index(drop=True)
        row_dd2 = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] == 2)].reset_index(drop=True)
        row_dd3 = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] == 3)].reset_index(drop=True)
        row_dd4 = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] == 4)].reset_index(drop=True)
        row_dd5 = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] == 5)].reset_index(drop=True)
        row_dd6 = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] == 6)].reset_index(drop=True)
        row_dd7plus = cg_edges_week_df[(cg_edges_week_df['yr_wk'] == g['yr_wk']) & (
            cg_edges_week_df['param1_value'] >= 7)].reset_index(drop=True)

        if len(row_dd1) > 0:
            n1 = int(row_dd1[0:1]['edges_in_week'][0])

        if len(row_dd2) > 0:
            n2 = int(row_dd2[0:1]['edges_in_week'][0])

        if len(row_dd3) > 0:
            n3 = int(row_dd3[0:1]['edges_in_week'][0])

        if len(row_dd4) > 0:
            n4 = int(row_dd4[0:1]['edges_in_week'][0])

        if len(row_dd5) > 0:
            n5 = int(row_dd5[0:1]['edges_in_week'][0])

        if len(row_dd6) > 0:
            n6 = int(row_dd6[0:1]['edges_in_week'][0])

        if len(row_dd7plus) > 0:
            n7plus = int(row_dd7plus[0:1]['edges_in_week'][0])

        if (n1+n2+n3+n4+n5+n6+n7plus > 0):
            i += 1
            labels.append(g['yr_wk'])
            l_dd1.append(n1)
            l_dd2.append(n2)
            l_dd3.append(n3)
            l_dd4.append(n4)
            l_dd5.append(n5)
            l_dd6.append(n6)
            l_dd7plus.append(n7plus)

    plot_cg_coupling(labels, l_dd1, l_dd2, l_dd3, l_dd4, l_dd5,
                     l_dd6, l_dd7plus, None, False)


def display_cg_coupling_on_month(con_analytics_db):
    sql_statement = """select count(*) from git_commit;"""
    cur = con_analytics_db.cursor()
    cur.execute(sql_statement)
    r = cur.fetchone()
    print("Number of commits: {0}".format(r[0]))

    sql_statement = """select
        strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
        strftime('%m', date(commit_commiter_datetime)) as iso_month,
        param1_value,
        sum(param2_value) as edges_in_month
        from cg_statistics
        where param1 = 'degree_distance'
        --and param1_value = 1
        group by 
        strftime('%Y', date(commit_commiter_datetime)),
        strftime('%m', date(commit_commiter_datetime)),
        param1_value;"""
    cg_edges_month_df = pd.read_sql_query(sql_statement, con_analytics_db)
    cg_edges_month_df['yr_m'] = cg_edges_month_df.apply(lambda row: ''.join([str(row.iso_yr), '-', str(row.iso_month)]), axis=1)

    labels = []
    l_dd1 = []
    l_dd2 = []
    l_dd3 = []
    l_dd4 = []
    l_dd5 = []
    l_dd6 = []
    l_dd7plus = []

    i = 0

    for g_idx, g in cg_edges_month_df.iterrows():
        n1=0
        n2=0
        n3=0
        n4=0
        n5=0
        n6=0
        n7plus=0

        row_dd1 = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']==1)].reset_index(drop=True)
        row_dd2 = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']==2)].reset_index(drop=True)
        row_dd3 = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']==3)].reset_index(drop=True)
        row_dd4 = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']==4)].reset_index(drop=True)
        row_dd5 = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']==5)].reset_index(drop=True)
        row_dd6 = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']==6)].reset_index(drop=True)
        row_dd7plus = cg_edges_month_df[(cg_edges_month_df['yr_m'] == g['yr_m']) & (cg_edges_month_df['param1_value']>=7)].reset_index(drop=True)

        if len(row_dd1)>0:
            n1 = int(row_dd1[0:1]['edges_in_month'][0])

        if len(row_dd2)>0:
            n2 = int(row_dd2[0:1]['edges_in_month'][0])

        if len(row_dd3)>0:
            n3 = int(row_dd3[0:1]['edges_in_month'][0])

        if len(row_dd4)>0:
            n4 = int(row_dd4[0:1]['edges_in_month'][0])

        if len(row_dd5)>0:
            n5 = int(row_dd5[0:1]['edges_in_month'][0])

        if len(row_dd6)>0:
            n6 = int(row_dd6[0:1]['edges_in_month'][0])

        if len(row_dd7plus)>0:
            n7plus = int(row_dd7plus[0:1]['edges_in_month'][0])

        if (n1+n2+n3+n4+n5+n6+n7plus > 0):
            i+=1
            labels.append(g['yr_m'])
            l_dd1.append(n1)
            l_dd2.append(n2)
            l_dd3.append(n3)
            l_dd4.append(n4)
            l_dd5.append(n5)
            l_dd6.append(n6)
            l_dd7plus.append(n7plus)

    plot_cg_coupling(labels, l_dd1, l_dd2, l_dd3, l_dd4, l_dd5,
                     l_dd6, l_dd7plus, None, False)


def plot_cg_coupling(labels, l_dd1, l_dd2, l_dd3, l_dd4, l_dd5, l_dd6, l_dd7plus, l_edges, display_total_edges):
    width = 0.35       # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()
    #plt.figure(figsize=(30, 30))

    if display_total_edges and l_edges is not None:
        ax.bar(labels, l_edges, width, label='edges')

    ax.bar(labels, l_dd1, width, label='dd1')
    ax.bar(labels, l_dd2, width, label='dd2')
    ax.bar(labels, l_dd3, width, label='dd3')
    ax.bar(labels, l_dd4, width, label='dd4')
    ax.bar(labels, l_dd5, width, label='dd5')
    ax.bar(labels, l_dd6, width, label='dd6')
    ax.bar(labels, l_dd7plus, width, label='dd7plus')

    fig.set_figwidth(18)
    fig.set_figheight(8)

    ax.set_ylabel('nr edges')
    ax.set_title('callgraph change coupling')
    ax.legend(bbox_to_anchor=(1.05, 0.6))
    ax.tick_params(axis="x", rotation=50)

    plt.show()
