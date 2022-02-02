from typing import List
from itertools import combinations
import sqlite3


def exist_import_dependency(con_analytics_db, l_items: List):
    """
    Returns list with format [exist_dependency, list_of_items]
    where exist_dependency = 1 if there is a structural dependency and 0 if not
    """
    r = []
    list_combinations = list(combinations(l_items, 2))
    dep = 0
    for c in list_combinations:
        dep = exist_import_dependency_2_items(con_analytics_db, c[0], c[1])
        if dep == 1:
            break
    r.append([dep, l_items])
    return r



def exist_import_dependency_2_items(con_analytics_db, A_file_name:str, B_file_name:str):
    """
    File B exists in the import list of file A
    """
    obj = 0
    cur = con_analytics_db.cursor()
    sql_statement = """select ifnull(sum(b_exists),0) r_exists from 
    (
    select 1 as b_exists from file_import a
        where a.file_name = '{0}'
        and EXISTS(
            select b.file_pkg
            from file_pkg b
            where b.file_name = '{1}'
            and b.class_pkg = a.import_file_pkg)
    union          
    select 1 as b_exists from file_import a
        where a.file_name = '{1}'
        and EXISTS(
            select b.file_pkg
            from file_pkg b
            where b.file_name = '{0}'
            and b.class_pkg = a.import_file_pkg)
    union
    select 
    (count(file_pkg) - count(distinct(file_pkg)))==1 as b_exists
    from file_pkg where file_name in('{0}','{1}')	
    );""".format(A_file_name, B_file_name)
    cur.execute(sql_statement)
    obj = cur.fetchone()            
    con_analytics_db.commit()
    cur.close()
    return obj[0]


