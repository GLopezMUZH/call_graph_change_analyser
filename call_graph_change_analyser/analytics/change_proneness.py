import os
import pandas as pd
from itertools import islice
import sqlite3
import numpy as np

from models import ProjectPaths

def save_change_proneness_file(proj_paths: ProjectPaths):
    conn = sqlite3.connect(proj_paths.get_path_to_project_db())
    cur = conn.cursor()

    try:
        cur.execute('''DROP TABLE change_proneness_file''')
    except Exception as error:
        print("Not existing")

    conn.commit()
    cur.close()


    sql_statement = """select
    file_name,
    strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
    (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1 as iso_week,
    count(*) as changes_in_week
    from file_commit
    group by 
    file_name,
    strftime('%Y', date(commit_commiter_datetime)),
    (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1;"""
    df = pd.read_sql_query(sql_statement, conn)

    df['yr-wk'] = df.apply(lambda row: ''.join([str(row.iso_yr),
                        '-', str(row.iso_week)]), axis=1)
    pdf = df[['yr-wk', 'file_name', 'changes_in_week']]

    changes_matrix = pd.pivot_table(pdf, index=['file_name'], values='changes_in_week',
                                    columns=['yr-wk'], aggfunc=np.sum)
    changes_matrix.to_sql('change_proneness_file', conn, if_exists='replace', index=True)    